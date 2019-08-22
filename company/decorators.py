"""
Decorators
"""
from django.core.exceptions import PermissionDenied
from company.models import Company
from .models import Company


def is_auditor(function):
    """
    Decorator for Auditor Lookup
    """
    def wrap(request, *args, **kwargs):
        if not Company.objects.filter(auditor=request.user):
            return function(request, *args, **kwargs)
        raise PermissionDenied

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
