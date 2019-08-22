"""
Bracketline (URLs)
"""
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.views.decorators.csrf import csrf_exempt
from . import views

app_name = 'bracketline'

urlpatterns = [
    url(r"login/$", (csrf_exempt(auth_views.LoginView.as_view)(template_name="bracketline/login.html")), name='login'),
    url(r"logout/$", csrf_exempt(auth_views.LogoutView.as_view()), name="logout"),
    url(r"signup/$", views.signup_view, name="signup"),
    url(r'^change_password/$', views.change_password_view, name="change_password"),
    url(r'^validate_gstin_ajax$', views.validate_gstin_ajax, name='validate_gstin_ajax'),
]
