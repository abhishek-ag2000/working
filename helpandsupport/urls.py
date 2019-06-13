from django.conf.urls import url
from helpandsupport import views

app_name = 'helpandsupport'

urlpatterns = [
	url(r'^$',views.CategoriesListView.as_view(),name='CategoriesList'),
	url(r'^(?P<slug>[\w-]+)/$',views.CategoryDetailView.as_view(),name='CategoriesDetail'),
	url(r'^(?P<slug1>[\w-]+)/(?P<slug>[\w-]+)/$',views.ArticleDetailView,name='ArticleDetail'),
	# url(r'^question/create/$', views.question_create, name='question_create'),
]