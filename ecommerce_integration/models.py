"""
Models
"""
from __future__ import unicode_literals
import sys
from io import BytesIO
from PIL import Image
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models


class Coupon(models.Model):
    """
    Coupon model
    """
    title_code = models.CharField(max_length=32)
    description = models.TextField(null=True)

    def __str__(self):
        return str(self.title_code)


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
    coupons = models.ForeignKey(Coupon, on_delete=models.CASCADE, null=True, blank=True, related_name='product_coupons')

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
    coupons = models.ForeignKey(Coupon, on_delete=models.CASCADE, null=True, blank=True, related_name='role_based_product_coupons')

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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,null=True,blank=True)
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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,null=True,blank=True)
    title = models.CharField(max_length=32)
    price = models.DecimalField(
        default=0.00, max_digits=10, decimal_places=2)
    image = models.ImageField(
        upload_to='api_images', default='user_profile/comming soon.jpg', null=True, blank=True)
    rating = models.DecimalField(default=4.5, max_digits=4, decimal_places=2)
    summary = models.TextField(max_length=150, null=True)
    description = models.TextField(null=True)
    coupons = models.ForeignKey(
        Coupon, on_delete=models.CASCADE, null=True, blank=True, related_name='api_coupons')

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
            tmp_resized_image.save(
                output_stream, format='JPEG', quality=300)
            output_stream.seek(0)
            self.image = InMemoryUploadedFile(output_stream, 'ImageField', "%s.jpg" % self.image.name.split(
                '.')[0], 'image/jpeg', sys.getsizeof(output_stream), None)
        super(API, self).save(*args, **kwargs)
