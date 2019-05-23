from django.conf.urls import url,include
from company import views
from django.urls import path
from django.views.decorators.csrf import csrf_exempt


app_name = 'company'

urlpatterns = [
######################### Company Urls ################################################

    url(r'^$',views.companyListView.as_view(),name='list'),
    url(r'^(?P<pk>\d+)/date/(?P<pk3>\d+)/$',views.companyDetailView.as_view(),name='Dashboard'),
    url(r'^create/$',views.companyCreateView.as_view(),name='create'),
    url(r'^ajax/validate_gst_billing/$', views.validate_gst_billing, name='validate_gst_billing'),
    url(r'^update/(?P<pk>\d+)/$',views.companyUpdateView.as_view(),name='update'),
    url(r'^delete/(?P<id>\d+)/$',views.company_delete,name='delete'),
    url(r'^(?P<pk>\d+)/$',views.specific_company_details,name='company_details'),
    url(r'^object/(?P<pk>\d+)/$',views.getcompanyObject,name='backup'),
    url(r'^import_company/$',views.company_upload,name='import_company'),


######################### Auditor Urls ################################################

    url(r'^(?P<pk>\d+)/auditor/$',views.auditor_list,name='auditor_list'),
    url(r'^(?P<pk>\d+)/auditor/member/search/$', views.search_auditors, name='search_auditors'),
    url(r'^(?P<pk>\d+)/profile/(?P<pk2>\d+)/add_auditor/$',views.add_auditor,name='add_auditor'),
    url(r'^(?P<pk>\d+)/profile/(?P<pk2>\d+)/remove_auditors/$',views.delete_auditors,name='remove_auditor'),

######################### Accountant Urls ################################################

    url(r'^(?P<pk>\d+)/accountant/$',views.accountant_list,name='accountant_list'),
    url(r'^(?P<pk>\d+)/accountant/member/search/$', views.search_accountant, name='search_accountant'),
    url(r'^(?P<pk>\d+)/profile/(?P<pk2>\d+)/add_accountant/$',views.add_accountant,name='add_accountant'),
    url(r'^(?P<pk>\d+)/profile/(?P<pk2>\d+)/remove_accountant/$',views.delete_accountant,name='delete_accountant'),


######################### Purchase Personal Urls ################################################

    url(r'^(?P<pk>\d+)/purchase_personal/$',views.purchase_personal_list,name='purchase_personal_list'),
    url(r'^(?P<pk>\d+)/purchase_personal/member/search/$', views.search_purchase_personal, name='search_purchase_personal'),
    url(r'^(?P<pk>\d+)/profile/(?P<pk2>\d+)/add_purchase_personal/$',views.add_purchase_personal,name='add_purchase_personal'),
    url(r'^(?P<pk>\d+)/profile/(?P<pk2>\d+)/remove_purchase_personal/$',views.delete_purchase_personal,name='delete_purchase_personal'),


######################### Sales Personal Urls ################################################

    url(r'^(?P<pk>\d+)/sales_personal/$',views.sales_personal_list,name='sales_personal_list'),
    url(r'^(?P<pk>\d+)/sales_personal/member/search/$', views.search_sales_personal, name='search_sales_personal'),
    url(r'^(?P<pk>\d+)/profile/(?P<pk2>\d+)/add_sales_personal/$',views.add_sales_personal,name='add_sales_personal'),
    url(r'^(?P<pk>\d+)/profile/(?P<pk2>\d+)/remove_sales_personal/$',views.delete_sales_personal,name='delete_sales_personal'),


######################### Cash/Bank Personal Urls ################################################

    url(r'^(?P<pk>\d+)/cb_personal/$',views.cb_personal_list,name='cb_personal_list'),
    url(r'^(?P<pk>\d+)/cb_personal/member/search/$', views.search_cb_personal, name='search_cb_personal'),
    url(r'^(?P<pk>\d+)/profile/(?P<pk2>\d+)/add_cb_personal/$',views.add_cb_personal,name='add_cb_personal'),
    url(r'^(?P<pk>\d+)/profile/(?P<pk2>\d+)/remove_cb_personal/$',views.delete_cb_personal,name='delete_cb_personal'),
	
]