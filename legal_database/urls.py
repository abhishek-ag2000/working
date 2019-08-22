"""
URLs
"""
from django.conf.urls import url
from legal_database import views

app_name = 'legal_database'

urlpatterns = [

    url(r'^$', views.HelpCategoryListView.as_view(), name='categorieslist'),
    url(r'^(?P<central_bare_act_pk>\d+)/central/$',
        views.central_bare_act_detail, name='central_act'),
    url(r'^(?P<state_bare_act_pk>\d+)/state/$',
        views.state_bare_act_detail, name='state_act'),
    url(r'^(?P<section_pk>\d+)/section/$',
        views.section_detail, name='section_act'),

]
