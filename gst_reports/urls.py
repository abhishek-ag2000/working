"""
GSTR Report URLS
"""
from django.conf.urls import url
from . import views

app_name = 'gst_reports'

urlpatterns = [
    url(r'company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/gstr1/$',
        views.GSTR1View.as_view(), name='gstr_1'),
    url(r'company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/gstr2a/$',
        views.GSTR2AView.as_view(), name='gstr_2A'),
    url(r'company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/gstr3b/$',
        views.GSTR3BView.as_view(), name='gstr_3B'),
    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/gstrinvoices/(?P<gst_type>[\w\-]+)/$',
        views.GSTRInvoiceListView.as_view(), name='gstrinvoices'),
]
