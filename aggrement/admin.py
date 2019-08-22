"""
Admin
"""
from django.contrib import admin
from aggrement.models import Aggrement, UserAggrements


class AggrementAdmin(admin.ModelAdmin):
    """
    Addrement Admin
    """
    model = Aggrement
    list_display = ['title', 'date', 'act', 'section', 'category']
    search_fields = ['title', 'act']


admin.site.register(Aggrement, AggrementAdmin)
admin.site.register(UserAggrements)
