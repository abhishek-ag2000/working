import arrow
from django.db import models
from django.utils.translation import ugettext_lazy as _

# from common.models import Address, User
from django.conf import settings    #import user
from company.models import Company  #import company
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.
class Contact(models.Model):
    # adding company details
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_contacts')

    # adding user
    assigned_to = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='contact_assigned_users')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='contact_created_by',
        on_delete=models.SET_NULL, null=True)



    first_name = models.CharField(_("First name"), max_length=255)
    last_name = models.CharField(_("Last name"), max_length=255)
    email = models.EmailField(unique=True)
    phone = PhoneNumberField(null=True, unique=True)
    # address = models.ForeignKey(
    #     Address, related_name='adress_contacts',
    #     on_delete=models.CASCADE, blank=True, null=True)

    address = models.CharField(_("Address"), max_length=500, blank=True, null=True)

    description = models.TextField(blank=True, null=True)
    
    created_on = models.DateTimeField(_("Created on"), auto_now_add=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.first_name