from django.shortcuts import render
from django.views.generic import (
    CreateView, UpdateView, DetailView, TemplateView, View, DeleteView)
import os
import json
import requests
import datetime
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, ListView, DetailView, CreateView, UpdateView, DeleteView

# Create your views here.
class HomeView(LoginRequiredMixin,TemplateView):
    template_name = "CRMtemplates/CRMdashboard.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context["accounts"] = 'accounts'
        return context