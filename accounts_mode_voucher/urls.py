"""
URLs
"""
from django.conf.urls import url
from . import views_sales_account,views_ajax

app_name = 'accounts_mode_voucher'

urlpatterns = [

    ################################### AJAX Url #######################################


    url(r'^ajax/reg_ledger_value/$', views_ajax.is_ledger_nature_same_json,
        name='is_ledger_nature_same_json'),



    ################################### Sales Accounts Url #######################################

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/sales$',
        views_sales_account.SalesListAccountsView.as_view(), name='saleslist'),

    url(r'^company/(?P<company_pk>\d+)/salesdetail/(?P<sales_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_sales_account.SalesDetailsView.as_view(), name='salesdetail'),

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/salescreate/$',
        views_sales_account.SalesCreateView.as_view(), name='salescreate'),

    url(r'^company/(?P<company_pk>\d+)/salesupdate/(?P<sales_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_sales_account.SalesUpdateView.as_view(), name='salesupdate'),

    url(r'^company/(?P<company_pk>\d+)/salesdelete/(?P<sales_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_sales_account.SalesDeleteView.as_view(), name='salesdelete'),


]
