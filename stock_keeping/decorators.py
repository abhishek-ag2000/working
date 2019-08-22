"""
Decorators
"""
from django.core.exceptions import PermissionDenied
from company.models import Company


def company_account_with_invenroty_decorator(function):
    """
    Decorator to check company with only 'Accounts with Inventory'
    """
    def wrap(request, *args, **kwargs):
        company_with_accounts = Company.objects.filter(maintain='Accounts with Inventory')
        if company_with_accounts:
            return function(request, *args, **kwargs)

        raise PermissionDenied
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
