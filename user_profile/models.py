"""
Models
"""
import sys
from io import BytesIO
import datetime
from PIL import Image
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from ckeditor_uploader.fields import RichTextUploadingField
from sorl.thumbnail import ImageField
from ecommerce_integration.models import Product, RoleBasedProduct
from accounting_entry.decorators import prevent_signal_call_on_bulk_load
from bracketline.models import StateMaster, CountryMaster


def file_size(value):  # add this to some file where you can import it from
    """
    Function to validate file size
    """
    limit = 2 * 1024 * 1024 * 1024 * 1024 * 1024
    if value.size > limit:
        raise ValidationError('File too large. Size should not exceed 5 MB.')


class Profile(models.Model):
    """
    Profile Model
    """
    date = models.DateTimeField(auto_now_add=True)
    full_name = models.CharField(max_length=32, blank=True)
    user_types = (
        ('Bussiness user', 'Bussiness user'),
        ('Professional', 'Professional'),
        ('Data Operators', 'Data Operators'),
        ('Others', 'Others')
    )
    user_type = models.CharField(max_length=32, choices=user_types, default='Others', blank=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='profile', on_delete=models.CASCADE)
    email = models.EmailField(max_length=70, blank=True)
    permanent_address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.ForeignKey(StateMaster, related_name="profile_state", on_delete=models.DO_NOTHING, null=True, blank=True)
    country = models.ForeignKey(CountryMaster, related_name="profile_country", on_delete=models.DO_NOTHING, null=True, blank=True)
    phone_no = models.CharField(max_length=32, blank=True)
    basic_info = models.TextField(blank=True)
    image = ImageField(upload_to='user_images', null=True, blank=True)
    subscribed_products = models.ManyToManyField(Product, related_name='products_subscribed', blank=True)
    subscribed_role_products = models.ManyToManyField(RoleBasedProduct, related_name='role_products_subscribed', blank=True)

    def __str__(self):
        return str(self.user)

    def save(self, *args, **kwargs):
        """
        Save Funtion to override the size and resolution of Profile Image
        """
        if self.image:
            temp_image = Image.open(self.image)
            output_stream = BytesIO()
            temp_resized_image = temp_image.resize((480, 480))
            temp_resized_image.save(output_stream, format='JPEG', quality=150)
            output_stream.seek(0)
            self.image = InMemoryUploadedFile(
                output_stream,
                'ImageField',
                "%s.jpg" % self.image.name.split('.')[0],  # need revision for file name
                'image/jpeg',
                sys.getsizeof(output_stream),
                None)

        super(Profile, self).save(*args, **kwargs)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
@prevent_signal_call_on_bulk_load
def create_user_on_profile_create(instance, created, **kwargs):  # sender, instance, created, **kwargs
    """
    Signal to create a Profile whenever a user Registers.
    """
    if created:
        Profile.objects.create(user=instance)


class ProductActivated(models.Model):
    """
    Product Activated Model
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_activate')
    date = models.DateField(default=datetime.date.today)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)


class RoleBasedProductActivated(models.Model):
    """
    Role based Product Activated Model
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(RoleBasedProduct, on_delete=models.CASCADE, related_name='role_product_activate')
    date = models.DateField(default=datetime.date.today)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)


@receiver(post_save, sender=Profile)
@prevent_signal_call_on_bulk_load
def products_activation(instance, **kwargs):  # sender, instance, created, **kwargs
    """
    Signal to create instances of ProductActivated and RoleBasedProductActivated models
    whenever a user profile saved
    """
    for product in instance.subscribed_products.all():
        if not ProductActivated.objects.filter(user=instance.user, product=product).exists():
            ProductActivated.objects.create(user=instance.user, product=product)

    for product in instance.subscribed_role_products.all():
        if not RoleBasedProductActivated.objects.filter(user=instance.user, product=product).exists():
            RoleBasedProductActivated.objects.create(user=instance.user, product=product)


class ProfessionalVerifyDoc(models.Model):
    """
    Professional Verify Document Model
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="requesting_user")
    user_doc_types = (
        ('Aadhar Card', 'Aadhar Card'),
        ('Birth Certificate', 'Birth Certificate'),
        ('Degree Certificate', 'Degree Certificate'),
        ('Diploma Certificate', 'Diploma Certificate'),
        ('Driving License', 'Driving License'),
        ('Experience Certificate', 'Experience Certificate'),
        ('NOC', 'NOC'),
        ('PAN Card', 'PAN Card'),
        ('Passport', 'Passport'),
        ('Registration Certificate', 'Registration Certificate'),
        ('Residential Certificate', 'Residential Certificate'),
        ('Trade License', 'Trade License'),
        ('Voter Card', 'Voter Card'),
        ('Others', 'Others'),
    )
    doc_type = models.CharField(max_length=30, choices=user_doc_types, default='Others', blank=False)
    manual_doc_type = models.CharField(max_length=30, null=True, blank=True)
    doc_image = models.ImageField(upload_to='pro_verification')
    date_added = models.DateTimeField(default=timezone.now)
    user_doc_status = (
        ('Pending', 'Pending'),
        ('Verified', 'Verified'),
        ('Regret', 'Regret'),
    )
    doc_status = models.CharField(max_length=30, choices=user_doc_status, default='Pending', blank=False)
    remarks = models.CharField(max_length=255, null=True, blank=True)
    verifier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="verifier_user")
    date_verified = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.user) + " " + self.doc_type


class ProfessionalVerify(models.Model):
    """
    Professional Verify Model
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='pro_product')
    phone_no = models.CharField(max_length=15)
    phone_verified = models.BooleanField(default=False)
    email = models.EmailField(max_length=70)
    email_verified = models.BooleanField(default=False)
    request_date = models.DateTimeField(default=timezone.now)
    request_status = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Regret', 'Regret'),
    )
    request_status = models.CharField(max_length=30, choices=request_status, default='Pending', blank=False)
    remarks = models.CharField(max_length=255, null=True, blank=True)
    verifier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="request_verifier")
    date_verified = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.user)

    def get_absolute_url(self):
        """
        Returns absolute url for the model object
        """
        return reverse("user_profile:pro_request_list")


class Post(models.Model):
    """
    Post Model
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, null=True, blank=True)
    post = RichTextUploadingField(blank=True,
                                  config_name='special',
                                  external_plugin_resources=[(
                                      'youtube',
                                      '/static/ckeditor/ckeditor/plugins/youtube_2.1.13/youtube/',
                                      'plugin.js',
                                  )],
                                  )
    date = models.DateTimeField(auto_now_add=True)
    like = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='like_post', blank=True)

    def __str__(self):
        return str(self.post)

    def get_absolute_url(self):
        """
        Returns absolute url for the model object
        """
        return reverse("user_profile:post_details", kwargs={'pk': self.pk})

    def total_like(self):
        """
        Returns total like for the model object
        """
        return self.like.count()


class PostComment(models.Model):
    """
    Post Comment Model
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_comment')
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text


class ProfessionalServices(models.Model):
    """
    Professional Services Model
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    service_name = models.CharField(max_length=100, blank=True)
    details = models.CharField(max_length=100, blank=True)
    types = (
        ('Returns', 'Returns'),
        ('Communication', 'Communication'),
        ('License', 'License')
    )
    service_type = models.CharField(
        max_length=100, choices=types, default='Returns', blank=True)
    time = (
        ('ANNUALLY', 'ANNUALLY'),
        ('QUARTERLY', 'QUARTERLY'),
        ('ONE TIME', 'ONE TIME')
    )
    duration = models.CharField(
        max_length=100, choices=time, default='ANNUALLY', blank=True)
    mode = (
        ('ON-PREMISES', 'ON-PREMISES'),
        ('CALLS - VOIP', 'CALLS - VOIP'),
        ('COLLECTION FROM CLIENT', 'COLLECTION FROM CLIENT')
    )
    service_mode = models.CharField(
        max_length=100, choices=mode, default='ON-PREMISES', blank=True)
    rate = models.DecimalField(
        default=0.00, max_digits=10, decimal_places=2, blank=True)

    def __str__(self):
        return self.service_name

    def get_absolute_url(self):
        """
        Returns absolute url for the model object
        """
        return reverse("user_profile:service_details", kwargs={'pk': self.pk})


class Achievement(models.Model):
    """
    Achievement Model
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    legal_case = models.BooleanField(default=False)
    act = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    facts = models.CharField(max_length=100, blank=True)
    issue = models.CharField(max_length=100, blank=True)
    argument = models.CharField(max_length=100, blank=True)
    judgement = models.CharField(max_length=100, blank=True)
    user_role = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.act

    def get_absolute_url(self):
        """
        Returns absolute url for the model object
        """
        return reverse("user_profile:case_details", kwargs={'pk': self.pk})
