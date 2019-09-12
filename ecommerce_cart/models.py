"""
Models
"""
import decimal
import math
from django.db import models
from django.utils import timezone
from user_profile.models import Profile
from ecommerce_integration.models import PriceModel, CashBackWallet
from ecommerce_integration.utils import calculate_price


class Order(models.Model):
    """
    Order model
    """
    order_code = models.CharField(max_length=15)
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE)
    is_ordered = models.BooleanField(default=False)
    date_ordered = models.DateTimeField(auto_now=True)
    wallet_tran = models.ForeignKey(CashBackWallet, on_delete=models.DO_NOTHING, null=True, blank=True, related_name="wallet_tran_applied")
    wallet_balance_apply = models.BooleanField(default=True)
    referral_code = models.CharField(max_length=15, null=True, blank=True)
    referrer = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name="prof_referrer")
    razorpay_order_id = models.CharField(max_length=50, null=True, blank=True)
    razorpay_order_amount = models.PositiveIntegerField(default=0) # in paise
    razorpay_payment_id = models.CharField(max_length=50, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=255, null=True, blank=True)
    razorpay_order_status = models.CharField(max_length=20, null=True, blank=True)
    razorpay_attempts = models.PositiveIntegerField(default=0)

    def get_cart_items(self):
        """
        Function to get the Items present in Cart
        """
        # return self.items.all()
        return OrderItem.objects.filter(order=self.pk)

    def get_cart_total_product_value(self):
        """
        Function to get the Cart Total on Product Value
        """
        total = decimal.Decimal(0.00)

        for order_item in self.get_cart_items():
            total += order_item.get_item_product_value()

        return round(total, 2)

    def get_cart_total_renewal_discount(self):
        """
        Function to get the Cart Total on Renewal Discount
        """
        total = decimal.Decimal(0.00)

        for order_item in self.get_cart_items():
            total += order_item.get_renewal_discount_amount()

        return round(total, 2)

    def get_cart_total_referral_discount(self):
        """
        Function to get the Cart Total on Referral Discount
        """
        total = decimal.Decimal(0.00)

        for order_item in self.get_cart_items():
            total += order_item.get_referral_discount_amount()

        return round(total, 2)

    def get_common_tax_percent(self):
        """
        Function to return tax percent of first cart item assuming all items has same tax rate
        """
        # first_item = self.items.first()
        # if first_item:
        #     return first_item.price_model.tax_rate
        # return 0.0
        first_item = OrderItem.objects.filter(order=self.pk).first()
        if first_item:
            return first_item.price_model.tax_rate
        return 0.0

    def get_cart_total_after_tax(self):
        """
        Function to get the Cart Total after tax without cash back adjustment
        """
        total = decimal.Decimal(0.00)

        for order_item in self.get_cart_items():
            total += order_item.get_item_net_price()

        return math.floor(total)

    def __str__(self):
        return '{0} - {1}'.format(self.owner, self.order_code)


class OrderItem(models.Model):
    """
    Order Item model
    """
    price_model = models.ForeignKey(PriceModel, on_delete=models.DO_NOTHING)
    month_count = models.PositiveIntegerField()
    date_added = models.DateTimeField(default=timezone.now)
    renewal_discount_percent = models.DecimalField(default=0.00, max_digits=5, decimal_places=2)
    ref_discount_percent = models.DecimalField(default=0.00, max_digits=5, decimal_places=2)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_item")

    def get_item_gross_price(self):
        """
        Returns applicable price based on month count without discount inclusive of GST
        """
        return calculate_price(
            self.price_model.monthly_inclusive_price,
            self.price_model.quarterly_inclusive_price,
            self.price_model.half_yearly_inclusive_price,
            self.price_model.annual_inclusive_price,
            self.month_count)

    def get_item_product_value(self):
        """
        Returns applicable product value based on month count before discounts
        """
        price = self.get_item_gross_price()
        price = round(price - (price * self.price_model.tax_rate / (decimal.Decimal(100.00) + self.price_model.tax_rate)), 2)  # before tax

        return price

    def get_renewal_discount_amount(self):
        """
        Returns applicable renewal discount amount
        """
        product_value = self.get_item_product_value()
        renewal_disc_amount = decimal.Decimal(0.00)

        if self.renewal_discount_percent > 0:
            renewal_disc_amount = round(product_value * self.renewal_discount_percent / decimal.Decimal(100.00), 2)

        return renewal_disc_amount

    def get_referral_discount_amount(self):
        """
        Returns applicable referral discount amount
        """
        product_value = self.get_item_product_value()
        ref_disc_amount = decimal.Decimal(0.00)

        if self.ref_discount_percent > 0:
            ref_disc_amount = round(product_value * self.ref_discount_percent / decimal.Decimal(100.00), 2)

        return ref_disc_amount

    def get_item_taxable_price(self):
        """
        Returns applicable taxable price based on month count after discounts
        """
        price = round(self.get_item_product_value() - self.get_renewal_discount_amount() - self.get_referral_discount_amount(), 2)

        return price

    def get_item_net_price(self):
        """
        Returns applicable price based on month count after discount and GST
        """
        price = self.get_item_taxable_price()
        price = price + (price * self.price_model.tax_rate / decimal.Decimal(100.00))  # new price after tax
        price = math.floor(price)

        return price

    def __str__(self):
        return str(self.price_model.product)+" "+str(self.price_model.product_feature)
