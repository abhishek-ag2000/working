import arrow

from django.db import models
# from common.models import User
from django.conf import settings    #import user
from company.models import Company  #import company
from django.utils.translation import ugettext_lazy as _


class Teams(models.Model):
    
    # adding company details
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_teams')

    name = models.CharField(max_length=100)
    description = models.TextField()
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='user_teams')
    created_on = models.DateTimeField(_("Created on"), auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='teams_created', blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('id',)

    @property
    def created_on_arrow(self):
        return arrow.get(self.created_on).humanize()