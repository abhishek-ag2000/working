"""
Models
"""
from __future__ import unicode_literals
import math
import sys
import datetime
from decimal import Decimal
from io import BytesIO
from PIL import Image
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.db.models import Max, Value
from django.db.models.functions import Coalesce
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from ckeditor_uploader.fields import RichTextUploadingField
from accounting_entry.decorators import prevent_signal_call_on_bulk_load


class Product(models.Model):
    """
    Product model
    """
    title = models.CharField(max_length=50)
    price = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    image = models.ImageField(upload_to='product_images', default='user_profile/comming soon.jpg')
    rating = models.DecimalField(default=4.5, max_digits=4, decimal_places=1)
    summary = models.TextField(max_length=150, null=True)
    description = models.TextField(null=True)

    def __str__(self):
        return str(self.title)

    def save(self, *args, **kwargs):
        """
        Save function to override the size and resolution of the product image
        """
        if self.image:
            temp_image = Image.open(self.image).convert('RGB')
            output_stream = BytesIO()
            tmp_resized_image = temp_image.resize((438, 419))
            tmp_resized_image.save(output_stream, format='JPEG', quality=300)
            output_stream.seek(0)
            self.image = InMemoryUploadedFile(
                output_stream,
                'ImageField',
                "%s.jpg" % self.image.name.split(
                    '.')[0], 'image/jpeg', sys.getsizeof(output_stream), None)
        super(Product, self).save(*args, **kwargs)


class ProductFeature(models.Model):
    """
    Bracketline Product Feature Model
    """
    feature_name = models.CharField(max_length=100, unique=True)
    feature_summary = models.TextField(max_length=255, null=True, blank=True)
    company_count = models.IntegerField(default=-1)
    auditor_per_company = models.IntegerField(default=-1)
    accountant_per_company = models.IntegerField(default=-1)
    accountant_total = models.IntegerField(default=-1)
    purchaser_per_company = models.IntegerField(default=-1)
    seller_per_company = models.IntegerField(default=-1)
    cashier_per_company = models.IntegerField(default=-1)
    description = RichTextUploadingField(blank=True, config_name='special')
    suggested = models.BooleanField(default=False)
    sorting_watage = models.IntegerField(default=0)

    def __str__(self):
        return str(self.feature_name)

    def save(self, *args, **kwargs):
        """
        Function to update sorting watage when defalt value unchanged
        """
        if self.sorting_watage == 0:
            self.sorting_watage = 1 + ProductFeature.objects.all().aggregate(the_max=Coalesce(Max('sorting_watage'), Value(0)))['the_max']

        super(ProductFeature, self).save(*args, **kwargs)


class PriceModel(models.Model):
    """
    Bracketline Product Price Model
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_base_price')
    apply_from = models.DateField(default=datetime.date.today)
    product_feature = models.ForeignKey(ProductFeature, on_delete=models.DO_NOTHING, related_name='product_feature')
    annual_inclusive_price = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    half_yearly_inclusive_price = models.DecimalField(default=0.00, max_digits=20, decimal_places=2, editable=False)
    quarterly_inclusive_price = models.DecimalField(default=0.00, max_digits=20, decimal_places=2, editable=False)
    monthly_inclusive_price = models.DecimalField(default=0.00, max_digits=20, decimal_places=2, editable=False)
    tax_rate = models.DecimalField(default=18.00, max_digits=5, decimal_places=2)
    user_ref_disc_percent = models.DecimalField(default=0.00, max_digits=5, decimal_places=2)
    agent_ref_disc_percent = models.DecimalField(default=0.00, max_digits=5, decimal_places=2)
    active_new = models.BooleanField(default=True)  # whether the plan active for new sale; no effect for existing sale

    def __str__(self):
        return str(self.product)+" "+str(self.product_feature)+" "+str(self.apply_from)

    def save(self, *args, **kwargs):
        """
        Function to update price other than annual
        """
        raw_val = self.annual_inclusive_price / Decimal(2.0) * Decimal(1.15)
        self.half_yearly_inclusive_price = math.floor(raw_val)

        raw_val = raw_val / Decimal(2.0) * Decimal(1.15)
        self.quarterly_inclusive_price = math.floor(raw_val)

        raw_val = raw_val / Decimal(3.0) * Decimal(1.15)
        self.monthly_inclusive_price = math.floor(raw_val)

        super(PriceModel, self).save(*args, **kwargs)

    class Meta:
        # price plan for same product with same feature cannot be created for same date
        unique_together = ['product', 'apply_from', 'product_feature']


class ProductSubscription(models.Model):
    """
    Product Subscription Model
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='subscriber', on_delete=models.CASCADE)
    price_model = models.ForeignKey(PriceModel, on_delete=models.DO_NOTHING, related_name='product_subscription_price')
    applied_price = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    renewal_discount_percent = models.DecimalField(default=0.00, max_digits=5, decimal_places=2)
    subscription_type_choice = (
        ('Monthly', 'Monthly'),
        ('Quarterly', 'Quarterly'),
        ('Half Yearly', 'Half Yearly'),
        ('Yearly', 'Yearly'),
    )
    subscription_type = models.CharField(max_length=20, choices=subscription_type_choice, default='Yearly')
    subscription_from = models.DateField(default=datetime.date.today)
    subscription_upto = models.DateField(default=datetime.date.today)
    month_count = models.PositiveIntegerField(default=0)
    subscription_active = models.BooleanField(default=True)

    def clean(self):
        if self.subscription_from > self.subscription_upto:
            raise ValidationError(
                {
                    'subscription_from': ['Subscription from date cannot be greater than subscription upto date'],
                    'subscription_upto': ['Subscription upto date cannot be less than subscription from date'],
                })

        if self.renewal_discount_percent > 100 or self.renewal_discount_percent < 0:
            raise ValidationError(
                {
                    'renewal_discount_percent': ['Renewal discount percent cannot be greater than 100 or less than 0']
                })


class CashBackWallet(models.Model):
    """
    Cash-Back Wallet Model
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='wallet_user', on_delete=models.CASCADE)
    tran_date = models.DateTimeField(default=timezone.now)
    tran_desc = models.CharField(max_length=512)
    tran_amount = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    tran_hash = models.CharField(max_length=255)

    def clean(self):
        if not self.tran_hash or str(hash(("RTNS", self.user.pk, round(self.tran_amount, 2)))) != self.tran_hash:
            raise ValidationError(
                {
                    'tran_hash': ['Transaction hash is invalid']
                })


class ProductReview(models.Model):
    """
    Product Review Model
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=32)
    email = models.EmailField(max_length=70, null=True, blank=True)
    reviews = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_review')
    text = models.TextField()

    def __str__(self):
        return self.text


class RoleBasedProduct(models.Model):
    """
    Role Based Product Model
    """
    title = models.CharField(max_length=32)
    price = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    image = models.ImageField(upload_to='product_images', default='user_profile/comming soon.jpg', null=True, blank=True)
    rating = models.DecimalField(default=4.5, max_digits=4, decimal_places=1)
    summary = models.TextField(max_length=150, null=True)
    description = models.TextField(null=True)

    def __str__(self):
        return str(self.title)

    def save(self, *args, **kwargs):
        """
        Save function to override the size and resolution of the role based product image
        """
        if self.image:
            temp_image = Image.open(self.image).convert('RGB')
            output_stream = BytesIO()
            tmp_resized_image = temp_image.resize((438, 419))
            tmp_resized_image.save(
                output_stream, format='JPEG', quality=300)
            output_stream.seek(0)
            self.image = InMemoryUploadedFile(output_stream, 'ImageField', "%s.jpg" % self.image.name.split(
                '.')[0], 'image/jpeg', sys.getsizeof(output_stream), None)
        super(RoleBasedProduct, self).save(*args, **kwargs)


class Services(models.Model):
    """
    Services Model
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=32)
    image = models.ImageField(upload_to='service_images',
                              default='user_profile/comming soon.jpg', null=True, blank=True)
    summary = models.TextField(max_length=150, null=True)
    description = models.TextField(null=True)

    def __str__(self):
        return str(self.title)

    def save(self, *args, **kwargs):
        """
        Save function to override the size and resolution of the services image
        """
        if self.image:
            temp_image = Image.open(self.image).convert('RGB')
            output_stream = BytesIO()
            tmp_resized_image = temp_image.resize((1000, 400))
            tmp_resized_image.save(
                output_stream, format='JPEG', quality=300)
            output_stream.seek(0)
            self.image = InMemoryUploadedFile(output_stream, 'ImageField', "%s.jpg" % self.image.name.split(
                '.')[0], 'image/jpeg', sys.getsizeof(output_stream), None)
        super(Services, self).save(*args, **kwargs)


class API(models.Model):
    """
    API Model
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=32)
    price = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='api_images', default='user_profile/comming soon.jpg', null=True, blank=True)
    rating = models.DecimalField(default=4.5, max_digits=4, decimal_places=2)
    summary = models.TextField(max_length=150, null=True)
    description = models.TextField(null=True)

    def __str__(self):
        return str(self.title)

    def save(self, *args, **kwargs):
        """
        Save function to override the size and resolution of the apis image
        """
        if self.image:
            temp_image = Image.open(self.image).convert('RGB')
            output_stream = BytesIO()
            tmp_resized_image = temp_image.resize((1000, 400))
            tmp_resized_image.save(output_stream, format='JPEG', quality=300)
            output_stream.seek(0)
            self.image = InMemoryUploadedFile(output_stream, 'ImageField', "%s.jpg" % self.image.name.split(
                '.')[0], 'image/jpeg', sys.getsizeof(output_stream), None)
        super(API, self).save(*args, **kwargs)


@receiver(post_save, sender=PriceModel)
@prevent_signal_call_on_bulk_load
def set_price_tag(instance, **kwargs):  # sender, instance, created, **kwargs
    """
    Signal to update price tag in product model when new price model defined or updated
    """
    lowest_price_moel = PriceModel.objects.filter(
        product=instance.product,
        apply_from__lte=datetime.date.today(),
        active_new=True
    ).order_by('annual_inclusive_price', '-apply_from').first()

    if lowest_price_moel:
        product = Product.objects.get(id=instance.product.id)
        product.price = int(lowest_price_moel.annual_inclusive_price / 12)
        product.save()
