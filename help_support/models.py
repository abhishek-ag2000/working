"""
Models
"""
import sys
from io import BytesIO
from PIL import Image
from sorl.thumbnail import ImageField
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.db.models.signals import pre_save
from django.utils.text import slugify
from django.urls import reverse
from ckeditor_uploader.fields import RichTextUploadingField

def file_size(value):  # add this to some file where you can import it from
    limit = 2 * 1024 * 1024 * 1024 * 1024 * 1024
    if value.size > limit:
        raise ValidationError('File too large. Size should not exceed 5 MB.')

def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.pdf', '.doc', '.docx', '.xlsx', '.xls']
    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Unsupported file extension.')

class HelpCategory(models.Model):
    """
    Help Category Model
    """
    # Name1 = (
    #     ('Getting Started', 'Getting Started'),
    #     ('Pricing', 'Pricing'),
    #     ('Integration', 'Integration'),
    #     ('Security', 'Security'),
    #     ('Product Professionals', 'Product Professionals'),
    #     ('About Products', 'About Products'),
    # )
    title = models.CharField(max_length=255, default='Getting Started')
    image = ImageField(upload_to='help_image', null=True, blank=True)
    desc = models.TextField(blank=True, null=True)
    slug = models.SlugField(max_length=255, blank=True, unique=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.image:
            tmp_image = Image.open(self.image).convert('RGBA')
            background = Image.new(
                'RGBA', tmp_image.size, (400, 400, 400))
            alpha_composite = Image.alpha_composite(background, tmp_image)
            output_stream = BytesIO()
            alpha_composite.save(output_stream, format='PNG', quality=300)
            output_stream.seek(0)
            self.image = InMemoryUploadedFile(output_stream, 'ImageField', "%s.png" % self.image.name.split('.')[0], 'image/png', sys.getsizeof(output_stream), None)
            super(HelpCategory, self).save(*args, **kwargs)

    # not working in templates
    def get_absolute_url(self):
        return reverse('CategoriesDetail', kwargs={"slug": self.slug})


def pre_save_help(sender, instance, *args, **kwargs):
    slug = slugify(instance.title)
    instance.slug = slug


pre_save.connect(pre_save_help, sender=HelpCategory)


class Articles(models.Model):
    """
    Articles
    """
    article_title = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, blank=True, unique=True)
    description = RichTextUploadingField(blank=True, null=True, config_name='special')
    article_category = models.ForeignKey(HelpCategory, on_delete=models.CASCADE, related_name='category')

    def __str__(self):
        return self.article_title

    def get_absolute_url(self):
        return reverse("help_support:ArticleDetail", kwargs={'slug': self.slug, 'slug1': self.article_category.slug})

    class Meta:
        ordering = ['-id']


def pre_save_article(sender, instance, *args, **kwargs):
    slug = slugify(instance.article_title)
    instance.slug = slug


pre_save.connect(pre_save_article, sender=Articles)


class ArticleQuestions(models.Model):
    """
    Artical Question Model
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    article = models.ForeignKey(Articles, on_delete=models.CASCADE, related_name='article')
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.article

    class Meta:
        ordering = ['-id']


class ArticleAnswers(models.Model):
    """
    Artical Answer Model
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.ForeignKey(Articles, on_delete=models.CASCADE, related_name='article_question')
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    answer = models.ForeignKey(ArticleQuestions, on_delete=models.CASCADE, related_name='article_answer')

    def __str__(self):
        return self.text

class SubmitRequest(models.Model):
    """
    Submit a request Model
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(max_length=70)
    subject = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    type_of_ticket = (
        ('Bugs', 'Bugs'),
        ('Complaint', 'Complaint'),
        ('Feedback', 'Feedback'),
        ('No Info', 'No Info'),
        ('Query', 'Query'),
        ('Request', 'Request'),
        ('Spam_ticket', 'Spam_ticket')
    )
    ticket_type = models.CharField(
        max_length=100, choices=type_of_ticket, blank=True)
    file_upload = models.FileField(
        upload_to="pro_verification", blank=True, validators=[file_size,validate_file_extension])
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL,
                                    on_delete=models.CASCADE, related_name='query_assigned', null=True, blank=True)
    status_choices = (
        ('pending','pending for verification'),
        ('verified','verified'),
        ('approached','approached the user for further details'),
        ('in progress', 'in progress'),
    )

    status = models.CharField(
        max_length=100, choices=status_choices, default='pending for verification')

    def __str__(self):
        return self.subject
