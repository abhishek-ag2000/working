from django.contrib import auth
from django.db import models
from django.utils import timezone


class User(auth.models.User, auth.models.PermissionsMixin):
    tandc = models.BooleanField()
    def __str__(self):
        return "@{}".format(self.username)



