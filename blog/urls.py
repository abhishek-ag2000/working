"""
Urls
"""
from django.conf.urls import url
from blog import views

app_name = 'blog'

urlpatterns = [
    url(r'^$', views.BlogCategoryListView.as_view(), name='bloglist'),
    url(r'^(?P<blog_pk>\d+)/$', views.post_detail, name='blogdetail'),
    url(r'^blogcreate/$', views.BlogCreateView.as_view(), name='blogcreate'),
    url(r'^blogupdate/(?P<blog_pk>\d+)/$', views.BlogUpdateView.as_view(), name='blogupdate'),
    url(r'^blogdelete/(?P<blog_pk>\d+)/$', views.BlogDeleteView.as_view(), name='blogdelete'),
    url(r'^bloglist/$', views.BlogAllListView.as_view(), name='allbloglist'),
    url(r'^latestbloglist/$', views.BlogLatestListView.as_view(), name='latestbloglist'),
    url(r'^likedbloglist/$', views.BlogLikedListView.as_view(), name='likebloglist'),
    url(r'^viewbloglist/$', views.BlogListView.as_view(), name='viewbloglist'),
    url(r'^like/$', views.like_post, name="like_post"),
    url(r'^categorylist/$', views.CategoryListView.as_view(), name='categoryList'),
    url(r'^categorylist/(?P<blog_pk>\d+)/$', views.HelpCategoryDetailView.as_view(), name='categoryDetail'),
    url(r'^result/$', views.search, name='search'),
]
