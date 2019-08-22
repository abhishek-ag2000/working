"""
Mixins for Accounting Double Entry
"""
from django.core.exceptions import PermissionDenied
from user_profile.models import ProductActivated, RoleBasedProductActivated


class ProductExistsRequiredMixin:
    """
    Product Exists Required Mixin
    """

    def dispatch(self, request, *args, **kwargs):
        """
        dispatch
        """
        if ProductActivated.objects.filter(
                user=self.request.user,
                product__id=1,  # bracket-book
                is_active=True) or RoleBasedProductActivated.objects.filter(
                    user=request.user,
                    product__id=1,
                    is_active=True):
            return super().dispatch(request, *args, **kwargs)

        raise PermissionDenied(
            "You do not have permission to access this link, please activate the related product and then try again!")
