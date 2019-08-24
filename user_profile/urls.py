"""
URLs
"""
from django.conf.urls import url
from django.urls import path
from . import views

app_name = 'user_profile'

urlpatterns = [
    url(r'^$', views.ProfileDetailView.as_view(), name='profiledetail'),
    url(r'^user_profile/(?P<profile_pk>\d+)/$',
        views.specific_profile_view, name='specific_profile'),
    url(r'^profileupdate/$', views.ProfileUpdateView.as_view(), name='profileupdate'),

    url(r'^servicelist/$', views.ServiceListView.as_view(), name='servicelist'),
    url(r'^specificservicelist/(?P<profile_pk>\d+)/$',
        views.service_specific_profile_view, name='specificservicelist'),

    path('activate/<product_activation_id>',
         views.activate_subscription, name='activate'),
    path('deactivate/<product_activation_id>',
         views.deactivate_subscription, name='deactivate'),

    path('activate/product/<product_activation_id>',
         views.active_subscription_list_view, name='activate_product'),
    path('deactivate/product/<product_activation_id>',
         views.deactive_subscription_list_view, name='deactivate_product'),

    path('roleactivate/<product_activation_id>',
         views.activate_subscription_role_based_list_view, name='activate_roleproduct'),
    path('roledeactivate/<product_activation_id>',
         views.deactive_subscription_role_based_list_view, name='deactivate_roleproduct'),

    url(r'^profresult/$', views.search_professional_view, name='search'),

    url(r'^social/$', views.post_list_view, name='social'),
    url(r'^post_add/$', views.PostCreateView.as_view(), name='post_add'),
    url(r'^(?P<post_pk>\d+)/$', views.post_detail_view, name='post_details'),

    url(r'^postlike/$', views.liked_post_view, name="like_post"),

    url(r'^postcomment/(?P<post_pk>\d+)/update$',
        views.post_comment_update_view, name='postcommentupdate'),

    url(r'^postcomment/(?P<post_pk>\d+)/delete$',
        views.post_comment_delete_view, name='postcommentdelete'),

    ############################# Service Url ##############################################################

    url(r'^service/create/$', views.ServiceCreateView.as_view(), name='service_create'),
    url(r'^service/(?P<service_pk>\d+)/update/$', views.ServiceUpdateView.as_view(), name='service_update'),
    url(r'^service/(?P<service_pk>\d+)/details/$',
        views.service_detail_view, name='service_details'),
    url(r'^service/(?P<service_pk>\d+)/delete$',
        views.service_delete_view, name='servicedelete'),


    ############################# Achievements Url ##############################################################

    url(r'^case/create/$', views.CaseCreateView.as_view(), name='case_create'),
    url(r'^case/(?P<case_pk>\d+)/update/$',
        views.CaseUpdateView.as_view(), name='case_update'),
    url(r'^caselist/$', views.CaseListView.as_view(), name='case_list'),
    url(r'^case/(?P<case_pk>\d+)/details/$', views.case_detail_view, name='case_details'),
    url(r'^case/(?P<case_pk>\d+)/delete$', views.case_delete_view, name='casedelete'),

    url(r'^ProfessionalVeriry/create/$',
        views.ProVerifyCreateView.as_view(), name='ProfessionalVerify'),
]
