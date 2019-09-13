"""
URLs
"""
from django.conf.urls import url
from django.contrib import admin

from .views import HomeView
from .views_contacts import ContactsListView,CreateContactView,UpdateContactView,DeleteContactView,DetailContactView
from .views_accounts import AccountsListView,CreateAccountView


app_name = 'CRM'

############################################### CRM Dashboard ###############################################

urlpatterns = [
    url(r'^company/(?P<organisation_pk>\d+)/$', HomeView.as_view() ,name="CRMdashboard"),



# ############################################### CRM Urls ###############################################
    url(r'^company/(?P<organisation_pk>\d+)/crm_contacts/$', ContactsListView.as_view(), name='crm_contacts'),
    url(r'^company/(?P<organisation_pk>\d+)/crm_contact_create/$', CreateContactView.as_view(), name='crm_contact_create'),
    url(r'^company/(?P<organisation_pk>\d+)/crm_contact_update/(?P<contact_pk>\d+)/$', UpdateContactView.as_view(), name='crm_contact_update'),
    url(r'^company/(?P<organisation_pk>\d+)/crm_contact_delete/(?P<contact_pk>\d+)/$', DeleteContactView.as_view(), name='crm_contact_delete'),
    url(r'^company/(?P<organisation_pk>\d+)/crm_contact_detail/(?P<contact_pk>\d+)/$', DetailContactView.as_view(), name='crm_contact_detail'),
	url(r'^company/(?P<organisation_pk>\d+)/crm_accounts/$', AccountsListView.as_view(), name='crm_accounts'),
	 url(r'^company/(?P<organisation_pk>\d+)/crm_account_create/$', CreateAccountView.as_view(), name='crm_account_create'),

]