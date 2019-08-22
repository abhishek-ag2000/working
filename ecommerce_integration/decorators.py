"""
Decorators
"""
from django.core.exceptions import PermissionDenied
from user_profile.models import ProductActivated, RoleBasedProductActivated


def product_1_activation(function):
    """
    Checks if Bracket Book activated or role based activation done
    """
    def wrap(request, *args, **kwargs):
        products = ProductActivated.objects.filter(user=request.user, product__id=1, is_active=True)
        role_products = RoleBasedProductActivated.objects.filter(user=request.user, product__id=1, is_active=True)
        if products or role_products:
            return function(request, *args, **kwargs)

        raise PermissionDenied
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
