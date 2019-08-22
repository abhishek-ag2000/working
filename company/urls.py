"""
URLs
"""
from django.conf.urls import url
from company import views

app_name = 'company'

urlpatterns = [

    ######################### Organisation Urls ################################################
    url(r'^create/$', views.OrganisationCreateView.as_view(), name='organisation_create'),
    url(r'^$', views.OrganisationListView.as_view(), name='list'),
    url(r'^(?P<organisation_pk>\d+)/date/(?P<period_selected_pk>\d+)/company_dashboard/$',
        views.OrganisationDetailsView.as_view(), name='CommonDashboard'),
    url(r'^(?P<organisation_pk>\d+)/date/(?P<period_selected_pk>\d+)/update_company/$',
        views.OrganisationUpdateView.as_view(), name='update_organisation'),
    url(r'^delete/(?P<organisation_pk>\d+)/$', views.organisation_delete_ajax, name='delete'),
    ######################### Company Urls ################################################

    url(r'^(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/$', views.CompanyDetailView.as_view(), name='Dashboard'),
    url(r'^(?P<organisation_pk>\d+)/date/(?P<period_selected_pk>\d+)/create/$', views.CompanyCreateView.as_view(), name='create'),
    url(r'^ajax/validate_gst_billing/$', views.validate_gst_billing, name='validate_gst_billing'),
    url(r'^update/(?P<company_pk>\d+)/$', views.CompanyUpdateView.as_view(), name='update'),
    url(r'^(?P<company_pk>\d+)/$', views.specific_company_details, name='company_details'),
    url(r'^object/(?P<company_pk>\d+)/$', views.get_company_object, name='backup'),
    url(r'^object/excel/(?P<company_pk>\d+)/$', views.get_company_excel, name='backup_excel'),
    url(r'^import_company/$', views.company_upload, name='import_company'),


    ######################### Auditor Urls ################################################

    url(r'^(?P<company_pk>\d+)/auditor/$', views.auditor_list, name='auditor_list'),
    url(r'^(?P<company_pk>\d+)/auditor/member/search/$', views.search_auditors, name='search_auditors'),
    url(r'^(?P<company_pk>\d+)/profile/(?P<profile_pk>\d+)/add_auditor/$', views.add_auditor, name='add_auditor'),
    url(r'^(?P<company_pk>\d+)/profile/(?P<profile_pk>\d+)/remove_auditors/$', views.delete_auditors, name='remove_auditor'),

    ######################### Accountant Urls ################################################

    url(r'^(?P<company_pk>\d+)/accountant/$', views.accountant_list, name='accountant_list'),
    url(r'^(?P<company_pk>\d+)/accountant/member/search/$', views.search_accountant, name='search_accountant'),
    url(r'^(?P<company_pk>\d+)/profile/(?P<profile_pk>\d+)/add_accountant/$', views.add_accountant, name='add_accountant'),
    url(r'^(?P<company_pk>\d+)/profile/(?P<profile_pk>\d+)/remove_accountant/$', views.delete_accountant, name='delete_accountant'),


    ######################### Purchase Personal Urls ################################################

    url(r'^(?P<company_pk>\d+)/purchase_personel/$', views.purchase_personel_list, name='purchase_personel_list'),
    url(r'^(?P<company_pk>\d+)/purchase_personel/member/search/$', views.search_purchase_personel, name='search_purchase_personel'),
    url(r'^(?P<company_pk>\d+)/profile/(?P<profile_pk>\d+)/add_purchase_personel/$', views.add_purchase_personel, name='add_purchase_personel'),
    url(r'^(?P<company_pk>\d+)/profile/(?P<profile_pk>\d+)/remove_purchase_personel/$', views.delete_purchase_personel, name='delete_purchase_personel'),


    ######################### Sales Personal Urls ################################################

    url(r'^(?P<company_pk>\d+)/sale_personel/$', views.sale_personel_list, name='sale_personel_list'),
    url(r'^(?P<company_pk>\d+)/sale_personel/member/search/$', views.search_sale_personel, name='search_sale_personel'),
    url(r'^(?P<company_pk>\d+)/profile/(?P<profile_pk>\d+)/add_sale_personel/$', views.add_sale_personel, name='add_sale_personel'),
    url(r'^(?P<company_pk>\d+)/profile/(?P<profile_pk>\d+)/remove_sale_personel/$', views.delete_sale_personel, name='delete_sale_personel'),


    ######################### Cash/Bank Personal Urls ################################################

    url(r'^(?P<company_pk>\d+)/cb_personal/$', views.cb_personal_list, name='cb_personal_list'),
    url(r'^(?P<company_pk>\d+)/cb_personal/member/search/$', views.search_cb_personal, name='search_cb_personal'),
    url(r'^(?P<company_pk>\d+)/profile/(?P<profile_pk>\d+)/add_cb_personal/$', views.add_cb_personal, name='add_cb_personal'),
    url(r'^(?P<company_pk>\d+)/profile/(?P<profile_pk>\d+)/remove_cb_personal/$', views.delete_cb_personal, name='delete_cb_personal'),

    ################################# Static page urls ################################
    
    url(r'^(?P<organisation_pk>\d+)/date/(?P<period_selected_pk>\d+)/static_demo_page/$', views.static_page, name='demo-page'),
    url(r'^(?P<organisation_pk>\d+)/date/(?P<period_selected_pk>\d+)/static/create/$',views.StaticPageCreateView.as_view(),name='static-page'),
    url(r'^(?P<organisation_pk>\d+)/date/(?P<period_selected_pk>\d+)/live_page/$', views.live_page, name='live-page'),
    url(r'^(?P<organisation_pk>\d+)/date/(?P<period_selected_pk>\d+)/static/update/$', views.StaticPageUpdateView.as_view(), name='update-page'),

]
