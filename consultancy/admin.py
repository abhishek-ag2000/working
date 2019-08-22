"""
Admin
"""
from django.contrib import admin
from .models import Consultancy, Answer

admin.site.register(Consultancy)
admin.site.register(Answer)
