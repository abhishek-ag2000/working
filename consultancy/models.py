"""
Models
"""
import datetime
from django.conf import settings
from django.db import models
from django.urls import reverse


class Consultancy(models.Model):
    """
    Consultancy model
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateField(auto_now=True)
    question = models.TextField()
    like = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='like', blank=True)

    def __str__(self):
        return self.question

    def get_absolute_url(self):
        return reverse("consultancy:consultancydetail", kwargs={'consultancy_pk': self.pk})

    def save(self):
        if self.id:
            self.modified_date = datetime.datetime.now()
        else:
            self.date = datetime.datetime.now()
        super(Consultancy, self).save()

    def total_like(self):
        return self.like.count()


class Answer(models.Model):
    """
    Answer model
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.ForeignKey(Consultancy, on_delete=models.CASCADE, related_name='consultancies')
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text
