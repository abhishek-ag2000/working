"""
E-Commerce Transaction Validation
"""
import datetime
import decimal
import math
from dateutil.relativedelta import relativedelta
from django.db import transaction
from django.http import Http404
from ecommerce_integration.models import ProductSubscription, CashBackWallet
from .razorpay import fetch_razorpay_order_info, fetch_razorpay_payment_by_order


def subscribe_order_items(user, order):
    """
    Function to subscribe order items and also calculate cash-back when feature change done
    """
    # update subscription details
    today = datetime.date.today()
    order_items = order.get_cart_items()

    for order_item in order_items:
        active_subscription = ProductSubscription.objects.filter(
            user=user,
            price_model__product=order_item.price_model.product,
            subscription_from__lte=datetime.date.today(),
            subscription_upto__gte=datetime.date.today(),
            subscription_active=True
        ).order_by("-subscription_from").first()

        price_model = order_item.price_model
        applied_price = order_item.get_item_net_price()
        month_count = order_item.month_count

        # activate new subscription immediately; when active subscription exists with same price model these value may change
        subscription_from = today
        subscription_upto = subscription_from + relativedelta(months=+month_count, days=-1)

        if month_count < 3:
            subscription_type = "Monthly"
        elif month_count < 6:
            subscription_type = "Quarterly"
        elif month_count < 12:
            subscription_type = "Half Yearly"
        else:
            subscription_type = "Yearly"

        subscription_active = True

        if active_subscription:
            # active subscription of same product exists
            if active_subscription.price_model == order_item.price_model:
                # same product model active; add new subscription with new date range after active subscription expires
                subscription_from = active_subscription.subscription_upto + relativedelta(days=+1)
                subscription_upto = subscription_from + relativedelta(months=+month_count, days=-1)
            else:
                # calculate cash back if applicable for last subscription; deactive last subscription; activate new subscription immediately
                delta = active_subscription.subscription_upto - today
                delta_months = math.floor(delta.days / 30)

                if delta_months >= 1 and active_subscription.month_count > 0:
                    deduction_factor = decimal.Decimal(0.5)  # gst + commission + gatewayfee + service charge

                    if active_subscription.month_count < 3:
                        cash_back = math.floor(active_subscription.price_model.monthly_inclusive_price * delta_months * deduction_factor)
                    elif active_subscription.month_count < 6:
                        cash_back = math.floor(active_subscription.price_model.quarterly_inclusive_price / 3 * delta_months * deduction_factor)
                    elif active_subscription.month_count < 12:
                        cash_back = math.floor(active_subscription.price_model.half_yearly_inclusive_price / 6 * delta_months * deduction_factor)
                    else:
                        cash_back = math.floor(active_subscription.price_model.annual_inclusive_price / 12 * delta_months * deduction_factor)

                    if cash_back > 0:
                        CashBackWallet.objects.create(
                            user=user,
                            tran_desc="Cash back for plan change from "+active_subscription.price_model.product_feature.feature_name + " to " + order_item.price_model.product_feature.feature_name,
                            tran_amount=cash_back,
                            tran_hash=str(hash(("RTNS", user.pk, round(cash_back, 2))))
                        )

                active_subscription.subscription_active = False  # deactive last subscription
                active_subscription.save()
                # activate new subscription immediately

        # else: # active subscription of same product is not found; activate new subscription immediately

        ProductSubscription.objects.create(
            user=user,
            price_model=price_model,
            applied_price=applied_price,
            subscription_type=subscription_type,
            subscription_from=subscription_from,
            subscription_upto=subscription_upto,
            month_count=month_count,
            subscription_active=subscription_active
        )


def verify_payment_status(razorpay_order_id, order):
    """
    Check if payment already made using API; if so update order and subscription details; raises Http404; returns True if payment found else false
    """
    try:
        razorpay_order_info = fetch_razorpay_order_info(razorpay_order_id)

        if razorpay_order_info.get('status') == "paid":
            razorpay_payment_info = fetch_razorpay_payment_by_order(razorpay_order_id)

            for payment_try in razorpay_payment_info["items"]:
                if payment_try["status"] == "authorized" or payment_try["status"] == "captured":  # status can be in created-authorized-captured-refunded-failed
                    with transaction.atomic():
                        order.razorpay_order_status = razorpay_order_info.get('status')
                        order.razorpay_attempts = razorpay_order_info.get('attempts')
                        order.razorpay_payment_id = payment_try["id"]
                        # order.razorpay_signature = razorpay_signature #signature not available in the data or API
                        order.is_ordered = True  # order done successfully
                        order.save()
                        subscribe_order_items(request.user, order)
                        return True
        return False
    except Exception as ex:
        print(ex)
        raise Http404("The server is experiencing issue with the payment gateway. Please try again later.")
