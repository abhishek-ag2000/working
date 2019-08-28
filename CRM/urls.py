"""
URLs
"""
from django.conf.urls import url
from django.contrib import admin

from .views import HomeView
from .views_contacts import ContactsListView

app_name = 'CRM'

############################################### CRM Dashboard ###############################################

urlpatterns = [
    url(r'^company/(?P<organisation_pk>\d+)', HomeView.as_view() ,name="CRMdashboard"),



# ############################################### CRM Urls ###############################################
    url(r'^company/(?P<organisation_pk>\d+)/CRM_contacts/$', ContactsListView.as_view(), name='CRM_contacts'),

]