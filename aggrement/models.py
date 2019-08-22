"""
Models
"""
from django.conf import settings
from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField


class Aggrement(models.Model):
    """
    Aggrement
    """
    date = models.DateTimeField(auto_now_add=True, null=True)
    title = models.TextField(max_length=100, null=True, blank=True)
    act = models.CharField(max_length=100, null=True, blank=True)
    section = models.CharField(max_length=100, null=True, blank=True)
    category_ls = (
        ('General', 'General'),
        ('Specific', 'Specific'),
    )
    types = (
        ('Agreement', 'Agreement'),
        ('Affidavit', 'Affidavit'),
        ('Form', 'Form'),
    )
    form_type = models.CharField(
        max_length=32, choices=types, default='Agreement')
    category = models.CharField(
        max_length=32, choices=category_ls, default='General')
    textbody = RichTextUploadingField(
        blank=True, null=True, config_name='special')
    guideline = models.TextField(max_length=100, null=True, blank=True)

    def __str__(self):
        return str(self.act)


class UserAggrements(models.Model):
    """
    User Aggrements
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="users_aggrement", on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    aggrement = models.ForeignKey(
        Aggrement, related_name="users_aggrement_control", on_delete=models.CASCADE, null=True, blank=True)
    textbody = RichTextUploadingField(blank=True, null=True, config_name='special')
    special_note = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return str(self.id)
