from django.core.exceptions import PermissionDenied
from company.models import company


def Company_only_accounts(function):
    def wrap(request, *args, **kwargs):
        company_with_accounts = company.objects.filter(maintain = 'Accounts with Inventory')
        if company_with_accounts:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap