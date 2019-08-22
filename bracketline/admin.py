"""
admin registration for the app
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import GroupBase, UQC, BracketlineUser


# class BracketlineUserAdmin(admin.ModelAdmin):
#     """
#     Admin
#     """
#     search_fields = ['id', 'username']
#     list_display = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'is_superuser', 'last_login', 'term_accepted']


#admin.site.unregister(Django_User)

admin.site.register(BracketlineUser, UserAdmin)
admin.site.register(GroupBase)
admin.site.register(UQC)
