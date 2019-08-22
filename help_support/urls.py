from django.conf.urls import url
from help_support import views

app_name = 'help_support'

urlpatterns = [
	url(r'^$',views.HelpCategoryListView.as_view(),name='CategoriesList'),
	url(r'^(?P<slug>[\w-]+)/$',views.HelpCategoryDetailView.as_view(),name='CategoriesDetail'),
	url(r'^(?P<slug1>[\w-]+)/(?P<slug>[\w-]+)/$',views.article_detail_view,name='ArticleDetail'),
	# url(r'^question/create/$', views.question_create, name='question_create'),
	url(r'^submit/request/user/$', views.RequestSubmitCreateView.as_view(), name='submit_request'),
	url(r'^submit/request/list/$', views.RequestSubmitListView.as_view(), name='submit_request_list'),
]