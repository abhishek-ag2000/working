"""
URLs
"""
from django.conf.urls import url
from django.contrib import admin

#from .views import HomeView

urlpatterns = [
    url(r'^CRMdashboard/'$, HomeView.as_view() ,name="CRMdashboard"),

]