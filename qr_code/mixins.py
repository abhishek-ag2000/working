from django.core.exceptions import PermissionDenied

from user_profile.models import ProductActivated


class QRProductExistsRequiredMixin:
    """
    ProductExistsRequiredMixin
    """
    def dispatch(self, request, *args, **kwargs):
        """
        dispatch method
        """
        if ProductActivated.objects.filter(user=self.request.user, product__id=3, is_active=True):
            return super().dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied
