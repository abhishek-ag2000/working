from django.core.exceptions import PermissionDenied
from company.models import company
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from company.models import company
from userprofile.models import Profile

User = get_user_model()



def is_auditor(function):
    def wrap(request, *args, **kwargs):
        if not  company.objects.filter(auditor=request.user):
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap