"""
Admin
"""
from django.contrib import admin
from . import models


class CompanyAdmin(admin.ModelAdmin):
    """
    Company Admin
    """
    search_fields = ['url_hash']


admin.site.register(models.Company, CompanyAdmin)
admin.site.register(models.Organisation)
admin.site.register(models.StaticPage)
admin.site.register(models.Service)
admin.site.register(models.Portfolio)
admin.site.register(models.TeamMember)
