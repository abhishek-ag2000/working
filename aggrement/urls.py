"""
Urls
"""
from django.conf.urls import url
from . import views

app_name = 'aggrement'

urlpatterns = [
    url(r'^$', views.AggrementListView.as_view(), name='aggrementlist'),
    url(r'^(?P<aggrement_pk>\d+)/aggrementupdate/', views.AggrementUpdateView.as_view(), name='aggrementupdate'),
    url(r'^create/$', views.AggrementCreateView.as_view(), name='create_aggrement'),
    url(r'^aggrementresult/$', views.search, name='search'),
    url(r'^saved_aggrement/$', views.SavedAggrementListView.as_view(), name='saved_aggrement'),
    url(r'^(?P<aggrement_pk>\d+)/user_aggrement/$', views.add_user_aggrement, name='add_user_aggrement'),
    url(r'^object/$', views.get_aggrement_object, name='aggrement_backup'),
    url(r'^object/agreement/$', views.aggrement_upload, name='aggrement_import'),
]
