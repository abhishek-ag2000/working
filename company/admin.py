"""
Admin
"""
from django.contrib import admin
from . import models



class OrganisationAdmin(admin.ModelAdmin):
    """
    Company Admin
    """
    list_display = ['name' , 'id']
    search_fields = ['url_hash']


class CompanyAdmin(admin.ModelAdmin):
    """
    Company Admin
    """
    search_fields = ['url_hash']


admin.site.register(models.Company, CompanyAdmin)
admin.site.register(models.Organisation, OrganisationAdmin)
admin.site.register(models.StaticPage)
admin.site.register(models.Service)
admin.site.register(models.Portfolio)
admin.site.register(models.TeamMember)
