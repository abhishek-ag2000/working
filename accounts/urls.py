from django.conf.urls import url
from django.urls import reverse
from django.contrib.auth import views as auth_views
# from django.contrib.auth.views import (
#     								password_reset, password_reset_done, password_reset_confirm,
#     								password_reset_complete
# 									)

from . import views
from django.views.decorators.csrf import csrf_exempt

app_name = 'accounts'

urlpatterns = [
    url(r"login/$", (csrf_exempt(auth_views.LoginView.as_view)(template_name="accounts/Login.html")),name='login'),
    url(r"logout/$", csrf_exempt(auth_views.LogoutView.as_view()), name="logout"),
    url(r"signup/$", views.signup, name="signup"),
    
    url(r'^change-password/$', views.change_password, name="change_password"),


    # url(r'^password_reset/$', auth_views.password_reset, name='password_reset'),
    # url(r'^password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    # url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
    #     auth_views.password_reset_confirm, name='password_reset_confirm'),
    # url(r'^reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),

 ]


