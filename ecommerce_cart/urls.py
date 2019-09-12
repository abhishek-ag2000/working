"""
URLs
"""
from django.conf.urls import url
from ecommerce_cart import views

app_name = 'ecommerce_cart'

urlpatterns = [
    url(r'^cart/(?P<price_model_id>\d+)/count/(?P<month_count>\d+)/$', views.add_to_cart, name="add_to_cart"),
    url(r'^ajax/cart/$', views.apply_ref_code_cart_json, name='apply_ref_code_cart_json'),
    url(r'^order-summary/$', views.order_summary_view, name="order_summary"),
    url(r'^order-summary/(?P<command>\w+)$', views.order_summary_view, name="order_summary"),
    url(r'^item/delete/(?P<item_id>[-\w]+)/$', views.delete_from_cart, name='delete_item'),
    url(r'^checkout/$', views.check_out_view, name='checkout'),
    url(r'^finish/payment/$', views.payment_submit_view, name='payment_submit_view'),
    url(r'^finish/zero/(?P<order_id>\d+)/$', views.finish_submit_view, name='finish_submit_view'),
]
