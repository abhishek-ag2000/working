
"""
Admin
"""
from django.contrib import admin
from blog.models import Blog, BlogCategories


class BlogAdmin(admin.ModelAdmin):
    """
    Blog Admin
    """
    model = Blog
    list_display = ['date', 'blog_title']
    search_fields = ['blog_title']
    readonly_fields = ('user',)


admin.site.register(Blog, BlogAdmin)
admin.site.register(BlogCategories)
