from django.conf.urls import url
from aggrement import views

app_name = 'aggrement'

urlpatterns = [

	url(r'^$',views.Aggrement_List_View.as_view(),name='aggrementlist'),    
    url(r'^(?P<pk1>\d+)/aggrementupdate/(?P<pk>\d+)/$',views.Aggrement_update_view.as_view(),name='aggrementupdate'),
    url(r'^create/$', views.Aggrement_createview.as_view(), name='create_aggrement'),
    url(r'^aggrementresult/$', views.search, name='search'),
    url(r'^saved_aggrement/$',views.Saved_aggrement_List_View.as_view(),name='saved_aggrement'),
    url(r'^(?P<pk>\d+)/user_aggrement/$',views.add_user_aggrement,name='add_user_aggrement'),
    url(r'^object/$',views.get_aggrement_Object,name='aggrement_backup'),
    url(r'^object/agreement/$',views.aggrement_upload,name='aggrement_import'),

]