from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
from django.conf import settings
from sorl.thumbnail import ImageField, get_thumbnail
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys
from django.db.models.signals import pre_save,post_save
from django.utils.text import slugify
from django.urls import reverse
# Create your models here.
class HelpCategories(models.Model):
	Name1 = (
		('Getting Started','Getting Started'),
		('Pricing','Pricing'),
		('Integration','Integration'),
		('Security','Security'),
		('Product Professionals','Product Professionals'),
		('About Products','About Products'),

		)
	Title = models.CharField(max_length=40, default='Getting Started')
	image = ImageField(upload_to='help_image', null=True, blank=True)
	desc  = models.TextField(blank=True, null=True)
	slug  = models.SlugField(blank=True)

	def __str__(self):
		return self.Title

	def save(self, *args, **kwargs):
		if self.image:
			imageTemporary = Image.open(self.image).convert('RGB')
			outputIoStream = BytesIO()
			imageTemporaryResized = imageTemporary.resize( (400,400) ) 
			imageTemporaryResized.save(outputIoStream , format='PNG', quality=300)
			outputIoStream.seek(0)
			self.image = InMemoryUploadedFile(outputIoStream,'ImageField', "%s.png" %self.image.name.split('.')[0], 'image/png', sys.getsizeof(outputIoStream), None)
			super(HelpCategories, self).save(*args, **kwargs)

	# not working in templates
	def get_absolute_url(self):
		return reverse('CategoriesDetail',kwargs={"slug":self.slug})

def pre_save_help(sender, instance, *args, **kwargs):
	slug =slugify(instance.Title)
	instance.slug = slug
pre_save.connect(pre_save_help, sender=HelpCategories)




class Articles(models.Model):
	Article_title   	= models.CharField(max_length=255,unique=True)
	slug 				= models.SlugField(blank=True)
	Description 		= RichTextUploadingField(blank=True, null=True,config_name='special')
	Article_Category 	= models.ForeignKey(HelpCategories,on_delete=models.CASCADE,related_name='category')

	def __str__(self):
		return self.Article_title

	class Meta:
		ordering = ['-id']

def pre_save_article(sender, instance, *args, **kwargs):
	slug =slugify(instance.Article_title)
	instance.slug = slug
pre_save.connect(pre_save_article, sender=Articles)



class Article_Questions(models.Model):
	User 				= models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=True,blank=True)
	Article  	    	= models.ForeignKey(Articles,on_delete=models.CASCADE,related_name='Article')
	text 				= models.TextField()
	Date 				= models.DateTimeField(auto_now_add=True)
	Question_title 		= models.CharField(max_length=255,unique=True)
	def __str__(self):
		return self.text

	class Meta:
		ordering = ['-id']

class Article_Answers(models.Model):
	User 			     = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=True,blank=True)
	Questions  			 = models.ForeignKey(Articles,on_delete=models.CASCADE,related_name='Article_Question')
	text  	 			 = models.TextField()
	Date 	 			 = models.DateTimeField(auto_now_add=True)
	#Article         	 = models.ForeignKey(Articles,on_delete=models.CASCADE,related_name='category')
	Answers 	        = models.ForeignKey(Article_Questions,on_delete=models.CASCADE,related_name='answers')
	def __str__(self):
		return self.text
