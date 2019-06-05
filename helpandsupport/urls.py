from django.conf.urls import url
from helpandsupport import views

app_name = 'helpandsupport'

urlpatterns = [
	url(r'^$',views.CategoriesListView.as_view(),name='CategoriesList'),
	url(r'^(?P<slug>[\w-]+)/$',views.CategoryDetailView.as_view(),name='CategoriesDetail'),
]