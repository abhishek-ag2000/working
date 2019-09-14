import arrow
from django.db import models
from django.utils.translation import pgettext_lazy
from django.utils.translation import ugettext_lazy as _

from .models import Tags
# from common.models import User
from django.conf import settings    #import user
from company.models import Company  #import company
from CRMcommon.utils import (COUNTRIES, LEAD_SOURCE, LEAD_STATUS,
                          return_complete_address)
from .models_contacts import Contact
from bracketline.models import CountryMaster, StateMaster 


class Lead(models.Model):
    # adding company details
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_Leads')
    # adding user details
    assigned_to = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='lead_assigned_users')
    created_by = models.ForeignKey( settings.AUTH_USER_MODEL, related_name='lead_created_by', on_delete=models.SET_NULL, null=True) 



    title = models.CharField(
        pgettext_lazy("Treatment Pronouns for the customer",
                      "Title"), max_length=64)
    first_name = models.CharField(_("First name"), null=True, max_length=255)
    last_name = models.CharField(_("Last name"), null=True, max_length=255)
    email = models.EmailField(null=True, blank=True)
    
    status = models.CharField(
        _("Status of Lead"),
        max_length=255, blank=True,
        null=True, choices=LEAD_STATUS)
    source = models.CharField(
        _("Source of Lead"), max_length=255,
        blank=True, null=True, choices=LEAD_SOURCE)
    address_line = models.CharField(
        _("Address"), max_length=255, blank=True, null=True)
    street = models.CharField(
        _("Street"), max_length=55, blank=True, null=True)
    city = models.CharField(_("City"), max_length=255, blank=True, null=True)
    state = models.ForeignKey(StateMaster, on_delete=models.DO_NOTHING, related_name='lead_state',blank=True, null=True)
    country = models.ForeignKey(CountryMaster, on_delete=models.DO_NOTHING, default=12, related_name="lead_country",blank=True, null=True)
    
    postcode = models.CharField(
        _("Post/Zip-code"), max_length=64, blank=True, null=True)

    website = models.CharField(
        _("Website"), max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    account_name = models.CharField(max_length=255, null=True, blank=True)
    opportunity_amount = models.DecimalField(
        _("Opportunity Amount"),
        decimal_places=2, max_digits=12,
        blank=True, null=True)
    
    created_on = models.DateTimeField(_("Created on"), auto_now_add=True)
    is_active = models.BooleanField(default=False)
    enquery_type = models.CharField(max_length=255, blank=True, null=True)
    tags = models.ManyToManyField(Tags, blank=True)
    contacts = models.ManyToManyField(Contact, related_name="lead_contacts")
    # created_from_site = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return self.title

    def get_complete_address(self):
        address = ""
        if self.address_line:
            address += self.address_line
        if self.street:
            if address:
                address += ", " + self.street
            else:
                address += self.street
        if self.city:
            if address:
                address += ", " + self.city
            else:
                address += self.city
        # if self.state:
        #     if address:
        #         address += ", " + self.state
        #     else:
        #         address += self.state
        if self.postcode:
            if address:
                address += ", " + self.postcode
            else:
                address += self.postcode
        # if self.country:
        #     if address:
        #         address += ", " + self.get_country_display()
        #     else:
        #         address += self.get_country_display()
        return address

    @property
    def created_on_arrow(self):
        return arrow.get(self.created_on).humanize()