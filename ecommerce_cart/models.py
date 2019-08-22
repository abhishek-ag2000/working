"""
Models
"""
from django.db import models
from django.db.models import Sum
from user_profile.models import Profile
from ecommerce_integration.models import Product


class OrderItem(models.Model):
    """
    Order Item model
    """
    product = models.OneToOneField(Product, on_delete=models.SET_NULL, null=True)
    is_ordered = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now=True)
    date_ordered = models.DateTimeField(null=True)

    def __str__(self):
        return self.product.title


class Order(models.Model):
    """
    Order model
    """
    ref_code = models.CharField(max_length=15)
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE)
    is_ordered = models.BooleanField(default=False)
    items = models.ManyToManyField(OrderItem)
    date_ordered = models.DateTimeField(auto_now=True)

    def get_cart_items(self):
        """
        Function to get the Items present in Cart
        """
        return self.items.all()

    def get_cart_total(self):
        """
        Function to get the Cart Total
        """
        return self.items.aggregate(total=Sum('product__price'))['total'] or 0

    def __str__(self):
        return '{0} - {1}'.format(self.owner, self.ref_code)
