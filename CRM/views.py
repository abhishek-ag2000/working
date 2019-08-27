from django.shortcuts import render

import os
import json
import requests
import datetime


# Create your views here.
class HomeView(TemplateView):
    template_name = "CRMdashboard.html"

    def get_context_data(self, **kwargs):
