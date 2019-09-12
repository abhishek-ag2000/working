"""
URLs
"""
from django.conf.urls import url
from . import views

app_name = 'ecommerce_integration'

urlpatterns = [
    url(r'^product/list/$', views.product_list_view, name='productlist'),
    url(r'^product/list/(?P<order_item_pk>\d+)$', views.product_list_view, name='productlist'),

    url(r'^productsubscribed/$', views.subscribed_product_list_view, name='subscribedproductlist'),

    url(r'^product/(?P<product_pk>\d+)/$', views.product_detail_view, name='productdetail'),
    url(r'^reviews/(?P<product_pk>\d+)/delete$', views.review_delete, name='reviewdelete'),

    url(r'^services/$', views.service_list_view, name='servicelist'),
    url(r'^services/(?P<service_pk>\d+)/$', views.service_detail_view, name='servicedetail'),

    url(r'^apis/$', views.api_list_view, name='apilist'),
    url(r'^apis/(?P<api_pk>\d+)/$', views.api_detail_view, name='apidetail'),

    url(r'^roleproduct/(?P<product_pk>\d+)/$', views.role_product_detail_view, name='roleproductdetail'),

    url(r'^ajax/productprice/$', views.product_price_json, name='product_price_json'),
]
