from django.db import models
import datetime
from datetime import datetime
from django.utils import timezone
from django.conf import settings
from ckeditor_uploader.fields import RichTextUploadingField
from django.urls import reverse
# Create your models here.

class Categories(models.Model):
	types 	= (
			('Forex & Banking','Forex & Banking'),
			('Capital Market','Capital Market'),
			('Corporate Laws','Corporate Laws'),
			('Competition Laws','Competition Laws'),
			('Indirect Taxation','Indirect Taxation'),
			('Direct Taxation','Direct Taxation'),
			('VAT','VAT'),
			('Sales Tax','Sales Tax'),
			('Compliance Almanac','Compliance Almanac'),
			('Employment Laws','Employment Laws'),
			('Labour','Labour'),
			('Criminal Laws','Criminal Laws'),
			('Insurance','Insurance'),
			('Industrial & Service','Industrial & Service'),
			('Human Rights','Human Rights'),
			('Foreign Trade Policy','Foreign Trade Policy'),
			('Indian Industrial Policy','Indian Industrial Policy'),
			('Environment','Environment'),
			('Intellectual Property Rights','Intellectual Property Rights'),
			('Cyber & IT Laws','Cyber & IT Laws'),
			('Media & Communication','Media & Communication'),
			('Anti-Dumping','Anti-Dumping'),
			('WTO','WTO'),
			('Power & Energy','Power & Energy'),
			('Mines & Minerals','Mines & Minerals'),
			)
	title 	= models.CharField(max_length=32,choices=types,default='Forex & Banking',unique=True)

	def __str__(self):
		return self.title

class Cases(models.Model):
	date        = models.DateTimeField(auto_now_add=True,null=True)
	title 		= models.TextField(null=True, blank=True)
	bare_body 	= RichTextUploadingField(blank=True, null=True,config_name='special')
	summary     = models.TextField(null=True, blank=True)
	facts 		= models.TextField(null=True, blank=True)
	issues 		= models.TextField(null=True, blank=True)
	ratio 		= models.TextField(null=True, blank=True)
	arguments 	= models.TextField(null=True, blank=True)
	judgement 	= models.TextField(null=True, blank=True)
	critics 	= models.TextField(null=True, blank=True)
	court 		= models.CharField(max_length=100,blank=True,null=True)
	sitations 	= models.TextField(null=True, blank=True)
	categories 	= models.ForeignKey(Categories,on_delete=models.CASCADE,related_name='Case_cat', null=True, blank=True)


	def __str__(self):
		return self.title


class Central_bare_act(models.Model):
	date        = models.DateTimeField(auto_now_add=True,null=True)
	title 		= models.TextField(null=True, blank=True)
	bare_body 	= RichTextUploadingField(blank=True, null=True,config_name='special')
	categories 	= models.ForeignKey(Categories,on_delete=models.CASCADE,related_name='cb_acts', null=True, blank=True)
	cases 		= models.ForeignKey(Cases,on_delete=models.CASCADE,related_name='cb_acts_cases', null=True, blank=True)

	def __str__(self):
		return self.title


class State_bare_act(models.Model):
	date        = models.DateTimeField(auto_now_add=True,null=True)
	title 		= models.TextField(null=True, blank=True)
	bare_body 	= RichTextUploadingField(blank=True, null=True,config_name='special')
	categories 	= models.ForeignKey(Categories,on_delete=models.CASCADE,related_name='sb_acts')
	cases 		= models.ForeignKey(Cases,on_delete=models.CASCADE,related_name='sb_acts_cases', null=True, blank=True)

	def __str__(self):
		return self.title

class Chapter(models.Model):
	state_act 	= models.ForeignKey(State_bare_act,on_delete=models.CASCADE,related_name='sb_acts_chap', null=True, blank=True)
	central_act = models.ForeignKey(Central_bare_act,on_delete=models.CASCADE,related_name='cb_acts_chap', null=True, blank=True)
	number 		= models.CharField(max_length=100)
	title 		= models.TextField(null=True, blank=True)

	def __str__(self):
		return self.number

class Section(models.Model):
	number 		= models.IntegerField(blank=True,null=True)
	state_act 	= models.ForeignKey(State_bare_act,on_delete=models.CASCADE,related_name='sb_acts_sec', null=True, blank=True)
	central_act = models.ForeignKey(Central_bare_act,on_delete=models.CASCADE,related_name='cb_acts_sec', null=True, blank=True)
	title 		= models.TextField(null=True, blank=True)
	body 		= RichTextUploadingField(blank=True, null=True,config_name='special')
	chapter     = models.ForeignKey(Chapter,on_delete=models.CASCADE,related_name='chapters', null=True, blank=True)
	cases 		= models.ForeignKey(Cases,on_delete=models.CASCADE,related_name='section_cases', null=True, blank=True)
	citations 	= RichTextUploadingField(blank=True, null=True,config_name='special')

	def __str__(self):
		return self.title

class Sub_section(models.Model):
	section 	= models.ForeignKey(Section,on_delete=models.CASCADE,related_name='sections', null=True, blank=True)
	title 		= models.TextField(null=True, blank=True)
	body 		= RichTextUploadingField(blank=True, null=True,config_name='special')
	sitations 	= RichTextUploadingField(blank=True, null=True,config_name='special')

	def __str__(self):
		return self.title


class Order(models.Model):
	title 		= models.TextField(null=True, blank=True)
	body 		= RichTextUploadingField(blank=True, null=True,config_name='special')
	sitations 	= models.TextField(null=True, blank=True)
	category 	= models.ForeignKey(Categories,on_delete=models.CASCADE,related_name='order_category', null=True, blank=True)
	cases 		= models.ForeignKey(Cases,on_delete=models.CASCADE,related_name='order_cases', null=True, blank=True)
	state_act 	= models.ForeignKey(State_bare_act,on_delete=models.CASCADE,related_name='sb_acts_order', null=True, blank=True)
	central_act = models.ForeignKey(Central_bare_act,on_delete=models.CASCADE,related_name='cb_acts_order', null=True, blank=True)

	def __str__(self):
		return self.title

class Notifications(models.Model):
	title 		= models.TextField(null=True, blank=True)
	body 		= RichTextUploadingField(blank=True, null=True,config_name='special')
	sitations 	= models.TextField(null=True, blank=True)
	category 	= models.ForeignKey(Categories,on_delete=models.CASCADE,related_name='noti_category', null=True, blank=True)
	cases 		= models.ForeignKey(Cases,on_delete=models.CASCADE,related_name='noti_cases', null=True, blank=True)
	state_act 	= models.ForeignKey(State_bare_act,on_delete=models.CASCADE,related_name='sb_acts_noti', null=True, blank=True)
	central_act = models.ForeignKey(Central_bare_act,on_delete=models.CASCADE,related_name='cb_acts_noti', null=True, blank=True)

	def __str__(self):
		return self.title