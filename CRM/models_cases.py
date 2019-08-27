import arrow
from django.db import models
from django.utils.translation import pgettext_lazy
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from .models_accounts import Account
from .models_contacts import Contact
# from common.models import User
from django.conf import settings    #import user
from company.models import Company  #import company
from CRMcommon.utils import CASE_TYPE, PRIORITY_CHOICE, STATUS_CHOICE
# from planner.models import Event


class Case(models.Model):
    # adding company details
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_cases')
    
    #adding user
    assigned_to = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='case_assigned_users')
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='case_created_by',
        on_delete=models.SET_NULL, null=True)
    
    name = models.CharField(
        pgettext_lazy("Name of the case", "Name"),
        max_length=64)
    
    status = models.CharField(choices=STATUS_CHOICE, max_length=64)
    priority = models.CharField(choices=PRIORITY_CHOICE, max_length=64)
    case_type = models.CharField(
        choices=CASE_TYPE, max_length=255, blank=True, null=True, default='')
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, blank=True, null=True)
    contacts = models.ManyToManyField(Contact)
    closed_on = models.DateField()
    description = models.TextField(blank=True, null=True)
    
    
    created_on = models.DateTimeField(_("Created on"), auto_now_add=True)
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return self.name

    # def get_meetings(self):
    #     content_type = ContentType.objects.get(app_label="cases", model="case")
    #     return Event.objects.filter(
    #         content_type=content_type,
    #         object_id=self.id,
    #         event_type="Meeting",
    #         status="Planned")

    # def get_completed_meetings(self):
    #     content_type = ContentType.objects.get(app_label="cases", model="case")
    #     return Event.objects.filter(
    #         content_type=content_type,
    #         object_id=self.id,
    #         event_type="Meeting").exclude(status="Planned")

    # def get_tasks(self):
    #     content_type = ContentType.objects.get(app_label="cases", model="case")
    #     return Event.objects.filter(content_type=content_type,
    #                                 object_id=self.id,
    #                                 event_type="Task",
    #                                 status="Planned")

    # def get_completed_tasks(self):
    #     content_type = ContentType.objects.get(app_label="cases", model="case")
    #     return Event.objects.filter(
    #         content_type=content_type,
    #         object_id=self.id,
    #         event_type="Task").exclude(status="Planned")

    # def get_calls(self):
    #     content_type = ContentType.objects.get(app_label="cases", model="case")
    #     return Event.objects.filter(content_type=content_type,
    #                                 object_id=self.id, event_type="Call",
    #                                 status="Planned")

    # def get_completed_calls(self):
    #     content_type = ContentType.objects.get(app_label="cases", model="case")
    #     return Event.objects.filter(
    #         content_type=content_type,
    #         object_id=self.id,
    #         event_type="Call").exclude(status="Planned")

    def get_assigned_user(self):
        return User.objects.get(id=self.assigned_to.id)

    @property
    def created_on_arrow(self):
        return arrow.get(self.created_on).humanize()