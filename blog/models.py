"""
Models
"""
import sys
from io import BytesIO
from PIL import Image
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.urls import reverse
from ckeditor_uploader.fields import RichTextUploadingField
from sorl.thumbnail import ImageField


class BlogCategories(models.Model):
    """
    Blog Categories
    """
    title = models.CharField(max_length=40, default='Default')

    def __str__(self):
        return self.title


class Blog(models.Model):
    """
    Blog
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    blog_title = models.CharField(max_length=255, unique=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='user_likes', blank=True)
    description = RichTextUploadingField(blank=True, null=True, config_name='special')
    blog_image = ImageField(upload_to='blog_image', null=True, blank=True)
    category = models.ForeignKey(BlogCategories, on_delete=models.CASCADE, related_name='blogs')
    blog_views = models.IntegerField(default=0)

    def __str__(self):
        return self.blog_title

    def get_absolute_url(self):
        """
        Returns absolute url for a blog
        """
        return reverse("blog:blogdetail", kwargs={'blog_pk': self.pk})

    def total_likes(self):
        return self.likes.count()

    def save(self, *args, **kwargs):
        if self.blog_image:
            temp_image = Image.open(self.blog_image).convert('RGB')
            output_io_stream = BytesIO()
            temp_resized_image = temp_image.resize((1000, 400))
            temp_resized_image.save(output_io_stream, format='JPEG', quality=300)
            output_io_stream.seek(0)
            self.blog_image = InMemoryUploadedFile(output_io_stream,
                                                   'ImageField', "%s.jpg" % self.blog_image.name.split('.')[0], 'image/jpeg', sys.getsizeof(output_io_stream), None)
        super(Blog, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-id']


class BlogComments(models.Model):
    """
    Blog Comments
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, null=True, blank=True)
    questions = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='blog_comments')
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text
