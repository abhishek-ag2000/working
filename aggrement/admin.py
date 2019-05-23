from django.contrib import admin
from aggrement.models import Aggrement, User_aggrement

# Register your models here.

class Aggrement_admin(admin.ModelAdmin):
	model = Aggrement
	list_display = ['title','date','act', 'section','category']
	search_fields = ['title','act']


admin.site.register(Aggrement,Aggrement_admin)
admin.site.register(User_aggrement)