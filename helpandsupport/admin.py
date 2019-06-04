from django.contrib import admin
from .models import *
# Register your models here.
class HelpSupportAdmin(admin.ModelAdmin):
	model = HelpCategories
	list_display = ['Title']
	#search_fields = ['Article_Question']
	#readonly_fields = ('User')

admin.site.register(HelpCategories, HelpSupportAdmin)
#admin.site.register(Article_Answers, Article_Questions)