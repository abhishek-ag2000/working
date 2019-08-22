"""
URLs
"""
from django.conf.urls import url
from . import views

app_name = 'messaging'

urlpatterns = [
    url(r'^messagecreate/$', views.MessageCreate.as_view(), name='messagecreate'),
    url(r'^messageinbox/$', views.MessageInbox.as_view(), name='messageinbox'),
    url(r'^messagesend/$', views.MessageSend.as_view(), name='messagesend'),
    url(r'^messagedetails/(?P<message_pk>\d+)/$', views.message_details, name='messagedetails'),
]
