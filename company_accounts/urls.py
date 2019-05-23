from django.conf.urls import url
from company_accounts import views

app_name = 'company_accounts'

urlpatterns = [
################################### Purchase Url #######################################

	url(r'^company/(?P<pk>\d+)/date/(?P<pk3>\d+)/purchase_accounts$',views.Purchase_accounts_listview.as_view(),name='purchaselist_accounts'),
	url(r'^company/(?P<pk1>\d+)/purchasedetail_accounts/(?P<pk2>\d+)/date/(?P<pk3>\d+)/$',views.Purchase_accounts_detailsview.as_view(),name='purchasedetail_accounts'),
	url(r'^company/(?P<pk>\d+)/date/(?P<pk3>\d+)/purchasecreate_accounts/$',views.Purchase_accounts_createview.as_view(),name='purchasecreate_accounts'),
	url(r'^company/(?P<pk1>\d+)/purchaseupdate_accounts/(?P<pk2>\d+)/date/(?P<pk3>\d+)/$',views.Purchase_accounts_updateview.as_view(),name='purchaseupdate_accounts'),
	url(r'^company/(?P<pk>\d+)/purchasedelete_accounts/(?P<pk2>\d+)/date/(?P<pk3>\d+)/$',views.Purchase_accounts_deleteview.as_view(),name='purchasedelete_accounts'),
	url(r'^company/(?P<pk>\d+)/purchasedatewise_accounts/(?P<month>\d+)/date/(?P<pk3>\d+)/$',views.purchase_accounts_register_datewise,name='purchase_datewise_accounts'),


################################### Purchase Register Url #######################################

	url(r'^company/(?P<pk>\d+)/Purchase_Register_accounts/date/(?P<pk3>\d+)/$',views.Purchase_accounts_Register_view.as_view(),name='purchase_register_accounts'),



################################### Sale Register Url #######################################

	url(r'^company/(?P<pk>\d+)/Sale_Register_accounts/date/(?P<pk3>\d+)/$',views.Sales_accounts_Register_view.as_view(),name='sale_register_accounts'),

################################### Sales Url #######################################

	url(r'^company/(?P<pk>\d+)/date/(?P<pk3>\d+)/sales_accounts$',views.Sales_accounts_listview.as_view(),name='saleslist_accounts'),
	url(r'^company/(?P<pk1>\d+)/salesdetail_accounts/(?P<pk2>\d+)/date/(?P<pk3>\d+)/$',views.Sales_accounts_detailsview.as_view(),name='salesdetail_accounts'),
	url(r'^company/(?P<pk>\d+)/date/(?P<pk3>\d+)/salescreate_accounts/$',views.Sales_accounts_createview.as_view(),name='salescreate_accounts'),
	url(r'^company/(?P<pk1>\d+)/salesupdate_accounts/(?P<pk2>\d+)/date/(?P<pk3>\d+)/$',views.Sales_accounts_updateview.as_view(),name='salesupdate_accounts'),
	url(r'^company/(?P<pk>\d+)/salesdelete_accounts/(?P<pk2>\d+)/date/(?P<pk3>\d+)/$',views.Sales_accounts_deleteview.as_view(),name='salesdelete_accounts'),


	url(r'^company/(?P<pk>\d+)/salesdatewise_accounts/(?P<month>\d+)/date/(?P<pk3>\d+)/$',views.sales_accounts_register_datewise,name='sales_datewise_accounts'),
	
]