"""
Views
"""
import string
import random
from datetime import date
import datetime
import decimal
import re
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models.functions import Coalesce
from django.db.models import Value, Count, Sum
from django.utils import timezone
from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from user_profile.models import Profile, ProfessionalVerify, ProductActivated, RoleBasedProductActivated
from messaging.models import Message
from ecommerce_integration.models import PriceModel, ProductSubscription, CashBackWallet
from .models import OrderItem, Order
from .razorpay import RAZORPAY_KEY, new_razorpay_order, fetch_razorpay_order_info, verify_razorpay_signature
from .etran_validation import subscribe_order_items, verify_payment_status


def get_new_order_code():
    """
    Function to generate unique new order code
    """
    date_str = date.today().strftime('%Y%m%d')[2:] + str(datetime.datetime.now().second)
    rand_str = "".join([random.choice(string.digits) for count in range(5)])
    return date_str + rand_str


def get_user_pending_order(request):
    """
    Function to get the user pending order
    """
    # get order for the correct user
    user_profile = get_object_or_404(Profile, user=request.user)
    order = Order.objects.filter(owner=user_profile, is_ordered=False).first()

    return order


@login_required
def add_to_cart(request, **kwargs):
    """
    Views that will add item to cart
    """
    user_profile = get_object_or_404(Profile, user=request.user)
    price_model = get_object_or_404(PriceModel, id=kwargs.get('price_model_id', "0"))
    month_count = int(kwargs.get('month_count', "0"))
    if month_count <= 0:
        raise Http404("Invalid month count")

    active_subscriptions_with_renewal_offer = ProductSubscription.objects.filter(
        user=request.user,
        price_model__product=price_model.product,  # any feature matching of same product to apply renewal offer discount
        subscription_from__lte=datetime.date.today(),
        subscription_upto__gte=datetime.date.today(),
        subscription_active=True,
        renewal_discount_percent__gt=0
    ).order_by("-subscription_from").first()

    renewal_discount_percent = 0
    if active_subscriptions_with_renewal_offer:
        renewal_discount_percent = active_subscriptions_with_renewal_offer.renewal_discount_percent

    order = get_user_pending_order(request)
    if not order:
        order = Order.objects.create(owner=user_profile, is_ordered=False, order_code=get_new_order_code())

    order_item, created = OrderItem.objects.update_or_create(
        order=order,
        price_model__product=price_model.product,
        defaults={
            'price_model': price_model,
            'month_count': month_count,
            'renewal_discount_percent': renewal_discount_percent,
            'date_added': timezone.now()
        }
    )

    # update all referral discount percent if applicable
    if order.referral_code and order.referrer:
        update_refereal_discount(order, order.referrer, order.referral_code)

    return redirect(reverse('ecommerce_integration:productlist', kwargs={'order_item_pk': order_item.pk}))
    #return redirect(reverse('ecommerce_integration:productlist'))


@login_required
def apply_wallet_view(request, **kwargs):
    """
    Apply wallet balance to order view
    """


@login_required
def order_summary_view(request, command='', **kwargs):
    """
    Cart summary view
    """
    order = get_user_pending_order(request)
    order_amount = decimal.Decimal(0.00)
    wallet_balance = decimal.Decimal("0.00")
    wallet_apply_amount = decimal.Decimal("0.00")

    if order:
        order_amount = order.get_cart_total_after_tax()

        if order.wallet_tran:
            # remove previous transaction wallet application
            wallet_tran_id = order.wallet_tran.pk
            order.wallet_tran = None
            order.save()
            CashBackWallet.objects.filter(pk=wallet_tran_id).delete()
            print("Unsuccessful wallet transaction removed for tran pk = ", wallet_tran_id)

        wallet_balance = CashBackWallet.objects.filter(user=request.user).aggregate(the_sum=Coalesce(Sum('tran_amount'), Value(0)))['the_sum']

        if command == 'APPLY_WALLET' and wallet_balance > 0:  # this block will only run if user trigger this view by Apply Wallet Balance button
            order.wallet_balance_apply = True
            order.save()

        for item in order.get_cart_items():
            # updating the renewal discount percent if the cart add date is different than today
            if item.date_added.date() != datetime.date.today():
                renewal_offer = ProductSubscription.objects.filter(
                    user=request.user,
                    price_model__product=item.price_model.product,  # any feature matching of same product to apply renewal offer discount
                    subscription_from__lte=datetime.date.today(),
                    subscription_upto__gte=datetime.date.today(),
                    subscription_active=True,
                    renewal_discount_percent__gt=0
                ).order_by("-subscription_from").first()

                disc_percent = decimal.Decimal(0.00)
                if renewal_offer:
                    disc_percent = renewal_offer.renewal_discount_percent

                if item.renewal_discount_percent != disc_percent:
                    item.renewal_discount_percent = disc_percent
                    item.save()

        if order.wallet_balance_apply and wallet_balance > 0:
            if order_amount >= wallet_balance:
                wallet_apply_amount = wallet_balance
            else:
                wallet_apply_amount = order_amount

    inbox = Message.objects.filter(reciever=request.user)
    inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
    send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

    context = {
        'product_aggrement': ProductActivated.objects.filter(user=request.user, product__id=9, is_active=True),
        'order': order,
        'order_amount': order_amount,
        'wallet_balance': wallet_balance,
        'wallet_apply_amount': wallet_apply_amount,
        'Products': ProductActivated.objects.filter(user=request.user, product__id=1, is_active=True),
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
        'role_product': RoleBasedProductActivated.objects.filter(user=request.user, product__id=1, is_active=True),
        'product_legal': ProductActivated.objects.filter(user=request.user, product__id=10, is_active=True)
    }

    return render(request, 'cart/cart.html', context)


@login_required
def check_out_view(request, **kwargs):
    """
    View to generate check_out_view Bill
    """
    order_amount = decimal.Decimal(0.00)
    wallet_apply_amount = decimal.Decimal("0.00")
    payable_amount = decimal.Decimal("0.00")
    razorpay_order_amount = 0
    razorpay_order_id = None
    order_description = "Bracketline Product"

    order = get_user_pending_order(request)
    if not order:
        return redirect(reverse('ecommerce_integration:subscribedproductlist'))

    # generating order description
    order_items = order.get_cart_items()
    if order_items:
        item_count = order_items.count()
        if item_count == 1:
            order_description = order_items.first().price_model.product.title
        elif item_count > 1:
            order_description = order_items.first().price_model.product.title + " +" + str(item_count-1) + " more product"

    order_amount = order.get_cart_total_after_tax()

    if order.wallet_tran:
        # remove previous transaction wallet application
        wallet_tran_id = order.wallet_tran.pk
        order.wallet_tran = None
        order.save()
        CashBackWallet.objects.filter(pk=wallet_tran_id).delete()
        print("Unsuccessful wallet transaction removed for tran pk = ", wallet_tran_id)

    if order.wallet_balance_apply:
        wallet_balance = CashBackWallet.objects.filter(user=request.user).aggregate(the_sum=Coalesce(Sum('tran_amount'), Value(0)))['the_sum']

        if wallet_balance <= 0:
            pass
        elif order_amount >= wallet_balance:
            wallet_apply_amount = wallet_balance
        else:
            wallet_apply_amount = order_amount

    if wallet_apply_amount > 0:
        order.wallet_tran = CashBackWallet.objects.create(
            user=request.user,
            tran_desc="Balance used for order of " + order_description,
            tran_amount=-wallet_apply_amount,
            tran_hash=str(hash(("RTNS", request.user.pk, round(-wallet_apply_amount, 2))))
        )
        order.save()

        payable_amount = round(order_amount - wallet_apply_amount, 0)
    else:
        payable_amount = order_amount

    razorpay_order_id = order.razorpay_order_id  # razorpay order id may already generated
    razorpay_order_amount = order.razorpay_order_amount

    if payable_amount <= 0 and razorpay_order_id:
        # remove razorpay order details as bill value is not payable
        razorpay_order_id = None
        order.razorpay_order_id = razorpay_order_id
        order.razorpay_order_status = None
        order.razorpay_order_amount = 0
        order.save()

    if payable_amount > 0 and (not razorpay_order_id or razorpay_order_amount != round(payable_amount*decimal.Decimal(100.00), 0)):
        # new or existing order but order amount changed; no payment status check; if payment done then support sould reftify issue
        try:
            #print("Requesting new Order ID from Razorpay......")
            razorpay_order_amount = int(round(payable_amount*decimal.Decimal(100.00), 0))  # convert bill rupee to paise
            razorpay_order_info = new_razorpay_order(razorpay_order_amount, order.order_code, {})
            #print("New Razorpay Order ID: ", razorpay_order_info.get('id'))
            order.razorpay_order_id = razorpay_order_info.get('id')
            order.razorpay_order_status = razorpay_order_info.get('status')
            order.razorpay_order_amount = razorpay_order_amount
            order.save()

        except Exception as ex:
            print(ex)
            raise Http404("The server is experiencing issue with the payment gateway. Please try again later.")
    elif payable_amount > 0 and razorpay_order_id:
        # razorpay order id already exists; checking if payment already made but subscription failed
        if verify_payment_status(razorpay_order_id, order):
            return redirect(reverse('ecommerce_integration:subscribedproductlist'))

    inbox = Message.objects.filter(reciever=request.user)
    inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
    send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

    context = {
        'product_aggrement': ProductActivated.objects.filter(user=request.user, product__id=9, is_active=True),
        'order': order,
        'order_amount': order_amount,
        'order_description': order_description,
        'wallet_apply_amount': wallet_apply_amount,
        'payable_amount': payable_amount,
        'RAZORPAY_KEY': RAZORPAY_KEY,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
        'Products': ProductActivated.objects.filter(user=request.user, product__id=1, is_active=True),
        'role_product': RoleBasedProductActivated.objects.filter(user=request.user, product__id=1, is_active=True),
        'product_legal': ProductActivated.objects.filter(user=request.user, product__id=10, is_active=True)
    }
    return render(request, 'cart/checkout.html', context)


@login_required()
def delete_from_cart(request, item_id):
    """
    View that will delete items from cart
    """
    item_to_delete = OrderItem.objects.filter(pk=item_id)

    if item_to_delete.exists():
        item_to_delete[0].delete()

    return redirect(reverse('ecommerce_cart:order_summary'))


@login_required
def apply_ref_code_cart_json(request):
    """
    Returns if the ref code is valid in JSON
    """
    data = {'is_error': False, 'error_message': ""}

    referral_code = request.POST.get('referral_code', None)
    if not referral_code:
        data['is_error'] = True
        data['error_message'] = "Referral code is not supplied"
        return JsonResponse(data)

    referral_code = referral_code.strip().upper()

    if not re.match(r'^REF\d+$', referral_code):
        data['is_error'] = True
        data['error_message'] = "Invalid Referral code pattern"
        return JsonResponse(data)

    referrer_id = referral_code[3:18]

    referrer = Profile.objects.filter(pk=referrer_id, user_type__exact='Professional').first()
    if not referrer:
        data['is_error'] = True
        data['error_message'] = "Invalid Referral code"
        return JsonResponse(data)

    order = get_user_pending_order(request)
    if not order:
        data['is_error'] = True
        data['error_message'] = "No order found to apply rererral code"
        return JsonResponse(data)

    if not update_refereal_discount(order, referrer, referral_code):
        data['is_error'] = True
        data['error_message'] = "The referral code is not applicable with your cart items"
        return JsonResponse(data)

    return JsonResponse(data)


def update_refereal_discount(order, referrer, referral_code):
    """
    Update rererral discount percent to each applicable order item and also updates order with referral code and rererrer
    """
    cart_items = order.get_cart_items()

    approved_products = ProfessionalVerify.objects.filter(
        user=referrer.user,
        request_status__exact="Approved").values_list('product__pk', flat=True).order_by('product__pk')

    if not cart_items or cart_items.count() == 0:
        return False

    if not approved_products or approved_products.count() == 0:
        return False

    approved_product_list = list(approved_products)

    for order_item in cart_items:
        user_ref_disc_percent = order_item.price_model.user_ref_disc_percent

        if user_ref_disc_percent > 0 and order_item.price_model.product.pk in approved_product_list:
            order_item.ref_discount_percent = user_ref_disc_percent
            order_item.save()

    order.referral_code = referral_code
    order.referrer = referrer
    order.save()

    return True


@login_required
def payment_submit_view(request, **kwargs):
    """
    View to receive payment details by the gateway
    """
    razorpay_order_id = request.POST.get('razorpay_order_id', None)  # Value Like: order_DE80c2ju4IhV2p
    razorpay_payment_id = request.POST.get('razorpay_payment_id', None)  # Value Like: pay_DE80lg9yYnkmRW
    razorpay_signature = request.POST.get('razorpay_signature', None)  # Value Like: 180b97f56771a5ad0b84797d0febe957d6ec06b6bb18bea95470a55f3d37d0db

    # for key, value in request.POST.items():
    #     print(key, value)

    if not razorpay_order_id or not razorpay_payment_id or not razorpay_signature:
        raise Http404("Payment failed!")

    order = Order.objects.filter(razorpay_order_id=razorpay_order_id).first()
    if not order:
        raise Http404("Payment failed! Order Info Missing!")

    try:
        verify_razorpay_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature)

        razorpay_order_info = fetch_razorpay_order_info(razorpay_order_id)
        #captured_data = capture_razorpay_payment(razorpay_payment_id, order.razorpay_order_amount)

        with transaction.atomic():
            order.razorpay_order_status = razorpay_order_info.get('status')
            order.razorpay_attempts = razorpay_order_info.get('attempts')
            order.razorpay_payment_id = razorpay_payment_id
            order.razorpay_signature = razorpay_signature
            order.is_ordered = True  # order done successfully
            order.save()

            subscribe_order_items(request.user, order)

    except Exception as ex:
        print(ex)
        raise Http404("The server is experiencing issue with the payment gateway. Your payment may have been done. Please contact support.")

    return redirect(reverse('ecommerce_integration:subscribedproductlist'))


@login_required()
def finish_submit_view(request, order_id):
    """
    View to finalize transaction with zero bill value
    """
    order = Order.objects.filter(pk=order_id).first()
    if not order:
        raise Http404("Subscription failed! Order Info Missing!")

    wallet_balance_applied = decimal.Decimal("0.00")
    if order.wallet_tran:
        wallet_balance_applied = order.wallet_tran.tran_amount

    if order.get_cart_total_after_tax() + wallet_balance_applied > 0:
        raise Http404("Subscription failed! Order has pending payment!")

    try:
        with transaction.atomic():
            order.is_ordered = True  # order done successfully
            order.save()

            subscribe_order_items(request.user, order)
    except Exception as ex:
        print(ex)
        raise Http404("The server is experiencing issue with checkout. Please contact support.")

    return redirect(reverse('ecommerce_integration:subscribedproductlist'))
