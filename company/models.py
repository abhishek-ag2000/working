from django.db import models
from datetime import datetime
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
import datetime
from django.conf import settings
from django.db.models import Case, When, CharField, Value, Sum, F, ExpressionWrapper, Subquery, OuterRef, Count
from django.db.models.functions import Coalesce 


from django.contrib.auth import get_user_model
User = get_user_model()



class company(models.Model):
	User = models.ForeignKey(User,related_name="Company_Owner",on_delete=models.CASCADE,null=True,blank=True)
	counter = models.IntegerField(blank=True,null=True)
	urlhash = models.CharField(max_length=100, null=True, blank=True)
	created_date = models.DateField(auto_now_add=True)
	modified_date = models.DateField(auto_now=True)
	Name = models.CharField(max_length=50,blank=False)
	types = (   ('Individual','Individual'),
				('HUF','HUF'),
				('Partnership','Partnership'),
				('Trust','Trust'),
				('Private Company','Private Company'),
				('Public Company','Public Company'),
				('LLP','LLP'),
			)
	nature = (   ('Service Provider','Service Provider'),
				('Retail','Retail'),
				('Wholesale','Wholesale'),
				('Works Contract','Works Contract'),
				('Leasing','Leasing'),
				('Factory Manufacturing','Factory Manufacturing'),
				('Bonded Warehouse','Bonded Warehouse'),
			)
	bussiness_nature = models.CharField(max_length=32,choices=nature,default='Retail')
	invetory = (
				('Accounts Only','Accounts Only'),
				('Accounts with Inventory','Accounts with Inventory'),
			)
	maintain  = models.CharField(max_length=32,choices=invetory,default='Accounts with Inventory')
	Type_of_company = models.CharField(max_length=32,choices=types,default='Individual')
	Address = models.TextField()
	Country = models.CharField(max_length=32,default='India')
	State_Name 		= (
		('Choose','Choose'),
		('Andhra Pradesh','Andhra Pradesh'),
		('Andaman & Nicobar Islands','Andaman & Nicobar Islands'),
		('Arunachal Pradesh','Arunachal Pradesh'),
		('Assam','Assam'),
		('Bihar','Bihar'),
		('Chandigarh','Chandigarh'),
		('Chhattisgarh','Chhattisgarh'),
		('Dadra and Nagar Haveli','Dadra and Nagar Haveli'),
		('Daman and Diu','Daman and Diu'),
		('Delhi','Delhi '),
		('Goa','Goa'),
		('Gujrat','Gujrat'),
		('Haryana','Haryana'),
		('Himachal Pradesh','Himachal Pradesh'),
		('Jammu and Kashmir','Jammu and Kashmir'),
		('Jharkhand','Jharkhand'),
		('Karnataka','Karnataka'),
		('Kerala','Kerala'),
		('Lakshadweep','Lakshadweep'),
		('Madhya Pradesh','Madhya Pradesh'),
		('Maharashtra','Maharashtra'),
		('Manipur','Manipur'),
		('Meghalaya','Meghalaya'),
		('Mizoram','Mizoram'),
		('Nagaland','Nagaland'),
		('Odisha','Odisha'),
		('Puducherry','Puducherry'),
		('Punjab','Punjab'),
		('Rajasthan','Rajasthan'),
		('Sikkim','Sikkim'),
		('Tamil Nadu','Tamil Nadu'),
		('Telangana','Telangana'),
		('Tripura','Tripura'),	
		('Uttar Pradesh','Uttar Pradesh'),
		('Uttarakhand','Uttarakhand'),
		('West Bengal','West Bengal'),
		)   		
	State = models.CharField(max_length=100,choices=State_Name,default='Choose')
	Pincode = models.CharField(max_length=32)
	Telephone_No = models.BigIntegerField(blank=True,null=True)
	Mobile_No = models.BigIntegerField(blank=True,null=True)

	financial_date = (
			("1st:April-31st:March","1st:April-31st:March"),
			("1st:Jan-31st:December","1st:Jan-31st:December")
		)


	Financial_Year_From = models.CharField(max_length=100,choices=financial_date,default="1st:April-31st:March", blank=False)
	Books_Begining_From = models.DateField(default=datetime.date(2018,4,1), blank=False)
	gst  				= models.CharField(max_length=20,blank=True,null=True)
	gst_enabled 		= models.BooleanField(default=False)
	composite_enable 	= models.BooleanField(default=False)
	pan  				= models.CharField(max_length=18,blank=True,null=True)
	auditor 			= models.ManyToManyField(settings.AUTH_USER_MODEL,related_name='main_auditor',blank=True)
	accountant 			= models.ManyToManyField(settings.AUTH_USER_MODEL,related_name='main_accountant',blank=True)
	purchase_personal 	= models.ManyToManyField(settings.AUTH_USER_MODEL,related_name='main_purchase',blank=True)
	sales_personal 		= models.ManyToManyField(settings.AUTH_USER_MODEL,related_name='main_sales',blank=True)
	cb_personal 		= models.ManyToManyField(settings.AUTH_USER_MODEL,related_name='main_cb',blank=True)
	capital 			= models.DecimalField(max_digits=10,decimal_places=2,default=0.0,null=True)
	asset 				= models.DecimalField(max_digits=10,decimal_places=2,default=0.0,null=True)
	pl 					= models.DecimalField(max_digits=10,decimal_places=2,default=0.0,null=True)

	def __str__(self):
		return self.Name

	def clean(self):
		if self.gst_enabled == False and self.composite_enable == True:
			raise ValidationError({'gst_enabled':["To enable composite billing GST should be enabled"],'composite_enable':["To enable composite billing GST should be enabled"]})

	def save(self):
		if self.id:
			self.modified_date = datetime.datetime.now()
		else:
			self.created_date = datetime.datetime.now()
		super(company,self).save()

	def save(self, **kwargs):
		super(company, self).save()
		if not self.urlhash:
			if self.User.profile.user_type == 'Bussiness User':
				self.urlhash = 'BU'+ '-' + str(self.User.id) + '-'+ 'P' + '-' + '1' + '-'+ 'C' + str(self.counter) 
				company.objects.filter(pk=self.pk).update(urlhash=self.urlhash)
			else:
				self.urlhash = 'PU'+ '-' + str(self.User.id) + '-'+ 'P' + '-' + '1' + '-'+ 'C' + str(self.counter) 
				company.objects.filter(pk=self.pk).update(urlhash=self.urlhash)

	class Meta:
		ordering = ["Name"]


@receiver(pre_save, sender=company)
def total_capital(sender,instance,*args,**kwargs):
	total_m = instance.Company_group.filter(Master__group_Name='Capital A/c').aggregate(the_sum=Coalesce(Sum('ledgergroups__Closing_balance'), Value(0)))['the_sum']
	total = instance.Company_group.filter(group_Name='Capital A/c').aggregate(the_sum=Coalesce(Sum('ledgergroups__Closing_balance'), Value(0)))['the_sum']
	if total == None and total_m == None:
		instance.capital = 0
	elif total == None:
		instance.capital = total_m
	elif total_m == None:
		instance.capital = total
	else:
		instance.capital = total + total_m

@receiver(pre_save, sender=company)
def total_asset(sender,instance,*args,**kwargs):
	total_f = instance.Company_group.filter(Master__group_Name='Fixed Assets').aggregate(the_sum=Coalesce(Sum('ledgergroups__Closing_balance'), Value(0)))['the_sum']
	total_fl 	= instance.Companys.filter(group1_Name__group_Name='Fixed Assets').aggregate(the_sum=Coalesce(Sum('Closing_balance'), Value(0)))['the_sum']
	total_c = instance.Company_group.filter(Master__group_Name='Current Assets').aggregate(the_sum=Coalesce(Sum('ledgergroups__Closing_balance'), Value(0)))['the_sum']
	total_cl 	= instance.Companys.filter(group1_Name__group_Name='Current Assets').aggregate(the_sum=Coalesce(Sum('Closing_balance'), Value(0)))['the_sum']
	if total_f == None:
		total_f = 0
	if total_fl == None:
		total_fl = 0
	if total_c == None:
		total_c = 0
	if total_cl == None:
		total_cl = 0
	instance.asset = total_c + total_cl + total_f + total_fl

@receiver(pre_save, sender=company)
def total_pl(sender,instance,*args,**kwargs):
	total = instance.Companys.filter(name='Profit & Loss A/c').aggregate(the_sum=Coalesce(Sum('Closing_balance'), Value(0)))['the_sum']
	if total == None:
		total = int(0)
	instance.pl = total