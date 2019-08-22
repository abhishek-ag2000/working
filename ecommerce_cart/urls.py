"""
URLs
"""
from django.conf.urls import url
from ecommerce_cart import views

app_name = 'ecommerce_cart'


urlpatterns = [
    url(r'^add-to-cart/(?P<item_id>[-\w]+)/$', views.add_to_cart, name="add_to_cart"),
    url(r'^order-summary/$', views.order_detail_view, name="order_summary"),
    url(r'^item/delete/(?P<item_id>[-\w]+)/$', views.delete_from_cart, name='delete_item'),
    url(r'^update-transaction/$', views.update_tran_record, name='update_records'),
    url(r'^checkout/$', views.check_out_view, name='checkout'),
]
