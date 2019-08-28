from django.contrib import admin

# Register your models here.

from .models import Comment, Comment_Files, Attachments 


class CommentAdmin(admin.ModelAdmin):
    """
    Model Admin class for CommentAdmin model
    """
    model = Comment
    list_display = ['company','case', 'comment', 'commented_by','commented_on']
    search_fields = ['company','case', 'comment']

class Comment_FilesAdmin(admin.ModelAdmin):
    """
    Model Admin class for Comment_FilesAdmin model
    """
    model = Comment_Files
    list_display = ['company', 'comment','comment_file','updated_on']
    search_fields = ['company','comment']


class AttachmentsAdmin(admin.ModelAdmin):
    """
    Model Admin class for AttachmentsAdmin model
    """
    model = Attachments
    list_display = ['company', 'created_by','file_name','attachment']
    search_fields = ['company','created_by', 'file_name']


admin.site.register(Comment, CommentAdmin)
admin.site.register(Comment_Files, Comment_FilesAdmin)
admin.site.register(Attachments, AttachmentsAdmin)

