"""
Mixins
"""
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from company.models import Company


class CompanyAccountsWithInventoryMixin:
    """
    Company Accounts with Inventory Mixin
    """

    def dispatch(self, request, *args, **kwargs):
        """
        Dispatch response after object access verification
        """
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])

        if Company.objects.filter(company_pk=company.pk, maintain='Accounts with Inventory'):
            return super().dispatch(request, *args, **kwargs)

        raise PermissionDenied
