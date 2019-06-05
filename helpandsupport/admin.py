from django.contrib import admin
from .models import *
# Register your models here.
class HelpSupportAdmin(admin.ModelAdmin):
	model = HelpCategories
	list_display = ['Title']
	#search_fields = ['Article_Question']
	#readonly_fields = ('User')

admin.site.register(HelpCategories, HelpSupportAdmin)

class articles(admin.ModelAdmin):
	model = Articles
	list_display = ['Article_title','slug','Article_Category']

admin.site.register(Articles, articles)

class article_questions(admin.ModelAdmin):
	model = Article_Questions
	list_display = ['User','Article','Question_title','text']

admin.site.register(Article_Questions, article_questions)

class article_answers(admin.ModelAdmin):
	model = Article_Answers
	list_display = ['User','Questions','text','Answers']

admin.site.register(Article_Answers, article_answers)