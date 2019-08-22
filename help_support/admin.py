"""
Admin
"""
from django.contrib import admin
from .models import *


class HelpSupportAdmin(admin.ModelAdmin):
    model = HelpCategory
    list_display = ['title']
    #search_fields = ['Article_Question']
    #readonly_fields = ('User')


admin.site.register(HelpCategory, HelpSupportAdmin)


class Article(admin.ModelAdmin):
    model = Articles
    list_display = ['article_title', 'slug', 'article_category']


admin.site.register(Articles, Article)


class ArticleQuestion(admin.ModelAdmin):
    model = ArticleQuestions
    list_display = ['user', 'article', 'text']


admin.site.register(ArticleQuestions, ArticleQuestion)


class ArticleAnswer(admin.ModelAdmin):
    model = ArticleAnswers
    list_display = ['user', 'question', 'text', 'answer']


admin.site.register(ArticleAnswers, ArticleAnswer)

class SubmitRequestAdmin(admin.ModelAdmin):
    """
    Submit a Request Admin
    """
    model = SubmitRequest
    list_display = ['user','subject']
    search_fields = ['user','subject']

admin.site.register(SubmitRequest, SubmitRequestAdmin)
