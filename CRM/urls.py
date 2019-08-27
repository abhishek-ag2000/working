"""
URLs
"""
from django.conf.urls import url
from django.contrib import admin

from .views import HomeView

app_name = 'CRM'

urlpatterns = [
    url(r'^company/(?P<organisation_pk>\d+)', HomeView.as_view() ,name="CRMdashboard"),

]