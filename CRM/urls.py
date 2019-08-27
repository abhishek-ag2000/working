"""
URLs
"""
from django.conf.urls import url
from django.contrib import admin

from .views import HomeView

app_name = 'CRM'

urlpatterns = [
    url(r"^$", HomeView.as_view(), name="CRMdashboard"),
    # url(r'^CRMdashboard/$', HomeView.as_view() ,name="CRMdashboard"),
    

]