from django.conf.urls import url
from django.urls import path
from Gst import views

app_name = 'Gst'

urlpatterns = [
	
	url(r'company/(?P<pk>\d+)/date/(?P<pk3>\d+)/gstr1/$',views.Gstr_1.as_view(),name='gstr_1'),
	url(r'company/(?P<pk>\d+)/date/(?P<pk3>\d+)/gstr2a$',views.Gstr_2A.as_view(),name='gstr_2A'),
	url(r'company/(?P<pk>\d+)/date/(?P<pk3>\d+)/gstr3b$',views.Gstr_3B.as_view(),name='gstr_3B'),
	url(r'company/(?P<pk>\d+)/date/(?P<pk3>\d+)/income_tax/$',views.income_tax.as_view(),name='income_tax'),

]