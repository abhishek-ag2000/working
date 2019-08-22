"""
URLs
"""
from django.conf.urls import url
from . import views

app_name = 'consultancy'

urlpatterns = [
    url(r'^$', views.ConsultancyListView.as_view(), name='consultancylist'),
    url(r'^(?P<consultancy_pk>\d+)/$', views.consultancy_detail, name='consultancydetail'),
    url(r'^ConsultancyCreateView/$', views.ConsultancyCreateView.as_view(), name='consultancycreate'),

    url(r'^ConsultancyUpdateView/(?P<consultancy_pk>\d+)/$', views.query_update, name='consultancyupdate'),
    url(r'^consultancydelete/(?P<consultancy_pk>\d+)/$', views.query_delete, name='consultancydelete'),

    url(r'^consultancylike/$', views.liked_post, name="like_question"),

    url(r'^myquestions/$', views.MyConsultancyListView.as_view(), name='myquestions'),

    url(r'^answers/(?P<answer_pk>\d+)/update$', views.answer_update, name='answersupdate'),

    url(r'^answers/(?P<answer_pk>\d+)/delete$', views.answer_delete, name='answersdelete'),

    url(r'^consultancyresult/$', views.search, name='search'),
]
