"""
Models of app bracketline (root app)
"""
#from django.contrib import auth
from django.contrib.auth.models import AbstractUser #, PermissionsMixin
from django.db import models


class BracketlineUser(AbstractUser): #PermissionsMixin
    """
    Bracketline User
    """
    term_accepted = models.BooleanField(default=True)

    def __str__(self):
        return "@{}".format(self.username)


class GroupBase(models.Model):
    """
    Predefined base group name (initial data will be inserted by second migration script)
    """
    YesNo = (
        ('Yes', 'Yes'),
        ('No', 'No')
    )
    name = models.CharField(max_length=32, unique=True)
    parent = models.CharField(max_length=20)
    is_revenue = models.CharField(max_length=3, choices=YesNo, default='No')
    affects_trading = models.CharField(max_length=3, choices=YesNo, default='No')
    is_debit = models.CharField(max_length=3, choices=YesNo, default='No')

    def __str__(self):
        return self.name


class CountryMaster(models.Model):
    """
    Country Master
    """
    country_name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.country_name

    # @staticmethod
    # def get_default_country_object():
    #     """
    #     Returns default country object for India
    #     """
    #     return CountryMaster.objects.get(country_name='India')

class StateMaster(models.Model):
    """
    State Master
    """
    state_name = models.CharField(max_length=30, unique=True)
    state_code = models.CharField(max_length=2, unique=True)

    def __str__(self):
        return self.state_name


class UQC(models.Model):
    """
    Unit Quantity Code
    """
    unit_code = models.CharField(max_length=3, default='PCS', unique=True)
    unit_name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.unit_code+" - "+self.unit_name
