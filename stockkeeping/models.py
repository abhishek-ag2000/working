from django.db import models
from accounting_double_entry.models import group1,ledger1,journal,selectdatefield,Pl_journal
from company.models import company
from django.conf import settings
from django.core.exceptions import ValidationError
import datetime
from django.db.models.signals import pre_save,post_save,pre_delete,post_delete
from django.dispatch import receiver
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.db.models.functions import Coalesce
from django.db.models import Value
from django.db.models import F
from sorl.thumbnail import ImageField, get_thumbnail
from decimal import Decimal,DecimalException
from django.db.models import Case, When, CharField, Value, Sum, Count, F, ExpressionWrapper, Subquery, OuterRef, FloatField
from accounting_double_entry.tasks import create_ledger_openingclosing_task
from django.db.models.fields import DecimalField
from django.db import transaction
# Create your models here.

class Stockgroup(models.Model):
	User       = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=True,blank=True)
	Company    = models.ForeignKey(company,on_delete=models.CASCADE,null=True,blank=True)
	counter    = models.IntegerField(blank=True,null=True)
	urlhash    = models.CharField(max_length=100, null=True, blank=True)
	name       = models.CharField(max_length=32)
	under      = models.ForeignKey("self",on_delete=models.CASCADE,related_name='Stock_group',null=True)
	quantities = models.BooleanField(default=False)

	def __str__(self):
		return self.name

	def save(self, **kwargs):
		super(Stockgroup, self).save()
		if not self.urlhash:
			if self.User.profile.user_type == 'Bussiness User':
				self.urlhash = 'BU'+ '-' + str(self.User.id) + '-'+ 'P' + '-' + '1' + '-'+ 'C' + str(self.Company.counter) + '-' + ('SSG') + str(self.counter)
				Stockgroup.objects.filter(pk=self.pk).update(urlhash=self.urlhash)
			else:
				self.urlhash = 'PU'+ '-' + str(self.User.id) + '-'+ 'P' + '-' + '1' + '-'+ 'C' + str(self.Company.counter) + '-' + ('SSG') + str(self.counter)
				Stockgroup.objects.filter(pk=self.pk).update(urlhash=self.urlhash)

@receiver(post_save, sender=company)
def user_created_stockgroup(sender, instance, created, **kwargs):
	if instance.maintain == 'Accounts with Inventory':
		c = Stockgroup.objects.filter(User=instance.User, Company=instance).count() + 1
		if created:
			Stockgroup.objects.create(counter=c, User=instance.User,Company=instance,name='Primary',quantities=False)


class Simpleunits(models.Model):
	User       	= models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=True,blank=True)
	Company    	= models.ForeignKey(company,on_delete=models.CASCADE,null=True,blank=True)
	counter 	= models.IntegerField(blank=True,null=True)
	urlhash		= models.CharField(max_length=100, null=True, blank=True)
	symbol     	= models.CharField(max_length=32)
	formal     	= models.CharField(max_length=32)

	def __str__(self):
		return self.symbol

	def save(self, **kwargs):
		super(Simpleunits, self).save()
		if not self.urlhash:
			if self.User.profile.user_type == 'Bussiness User':
				self.urlhash = 'BU'+ '-' + str(self.User.id) + '-'+ 'P' + '-' + '1' + '-'+ 'C' + str(self.Company.counter) + '-' + ('SSU') + str(self.counter)
				Simpleunits.objects.filter(pk=self.pk).update(urlhash=self.urlhash)
			else:
				self.urlhash = 'PU'+ '-' + str(self.User.id) + '-'+ 'P' + '-' + '1' + '-'+ 'C' + str(self.Company.counter) + '-' + ('SSU') + str(self.counter)
				Simpleunits.objects.filter(pk=self.pk).update(urlhash=self.urlhash)


class Compoundunits(models.Model):
	User       		= models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=True,blank=True)
	Company    		= models.ForeignKey(company,on_delete=models.CASCADE,null=True,blank=True)
	counter	 		= models.IntegerField(blank=True,null=True)
	urlhash 		= models.CharField(max_length=100, null=True, blank=True)
	firstunit  		= models.ForeignKey(Simpleunits,on_delete=models.CASCADE,related_name='firsts')
	conversion 		= models.DecimalField(max_digits=19,decimal_places=2)
	seconds_unit 	= models.ForeignKey(Simpleunits,on_delete=models.CASCADE,related_name='seconds')

	def __str__(self):
		return str(self.firstunit) +  '  of  '  + str(self.seconds_unit)

	def clean(self):
		if self.firstunit == self.seconds_unit:
			raise ValidationError('First Unit Should Not Be Equal To Second Unit')


	def save(self, **kwargs):
		super(Compoundunits, self).save()
		if not self.urlhash:
			if self.User.profile.user_type == 'Bussiness User':
				self.urlhash = 'BU'+ '-' + str(self.User.id) + '-'+ 'P' + '-' + '1' + '-'+ 'C' + str(self.Company.counter) + '-' + ('SCU') + str(self.counter)
				Compoundunits.objects.filter(pk=self.pk).update(urlhash=self.urlhash)
			else:
				self.urlhash = 'PU'+ '-' + str(self.User.id) + '-'+ 'P' + '-' + '1' + '-'+ 'C' + str(self.Company.counter) + '-' + ('SCU') + str(self.counter)
				Compoundunits.objects.filter(pk=self.pk).update(urlhash=self.urlhash)


class Stockdata(models.Model):
	User        = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=True,blank=True,related_name='user_stock')
	Company     = models.ForeignKey(company,on_delete=models.CASCADE,null=True,blank=True,related_name='Company_stock')
	counter 	= models.IntegerField(blank=True,null=True)
	urlhash 	= models.CharField(max_length=100, null=True, blank=True)
	Quantity    = models.PositiveIntegerField(null=True,blank=True,default=0)
	rate		= models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
	opening 	= models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
	stock_name  = models.CharField(max_length=32)
	batch_no	= models.PositiveIntegerField(blank=True, null=True)
	bar_code 	= ImageField(upload_to='stockmanagement', null=True, blank=True)
	mnf_date	= models.DateField(blank=True, null=True)
	exp_date	= models.DateField(blank=True, null=True)
	under       = models.ForeignKey(Stockgroup,on_delete=models.CASCADE,related_name='stocks')
	unitsimple  = models.ForeignKey(Simpleunits,on_delete=models.CASCADE,null=True,blank=True,related_name='firsts_unit')
	unitcomplex = models.ForeignKey(Compoundunits,on_delete=models.CASCADE,null=True,blank=True,related_name='seconds_unit_complex')
	gst_rate    = models.DecimalField(max_digits=4,decimal_places=2,default=5)
	hsn         = models.PositiveIntegerField()

	def __str__(self):
		return self.stock_name

	def clean(self):
		if self.unitsimple != None and self.unitcomplex != None:
			raise ValidationError({'unitcomplex':["You are not supposed to select both units!"],'unitsimple':["You are not supposed to select both units!"]})

	def save(self, *args, **kwargs):
		if self.bar_code:
			self.bar_code = get_thumbnail(self.bar_code, '128x128', quality=150, format='JPEG').url
		self.opening = self.Quantity * self.rate
		super(Stockdata, self).save(*args, **kwargs)

	def save(self, **kwargs):
		super(Stockdata, self).save()
		if not self.urlhash:
			if self.User.profile.user_type == 'Bussiness User':
				self.urlhash = 'BU'+ '-' + str(self.User.id) + '-'+ 'P' + '-' + '1' + '-'+ 'C' + str(self.Company.counter) + '-' + ('SSD') + str(self.counter)
				Stockdata.objects.filter(pk=self.pk).update(urlhash=self.urlhash)
			else:
				self.urlhash = 'PU'+ '-' + str(self.User.id) + '-'+ 'P' + '-' + '1' + '-'+ 'C' + str(self.Company.counter) + '-' + ('SSD') + str(self.counter)
				Stockdata.objects.filter(pk=self.pk).update(urlhash=self.urlhash)




class Purchase(models.Model):
	User         	= models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=True,blank=True)
	Company      	= models.ForeignKey(company,on_delete=models.CASCADE,null=True,blank=True,related_name='companypurchase')
	counter 	 	= models.IntegerField(blank=True,null=True)
	urlhash 	 	= models.CharField(max_length=100, null=True, blank=True)
	date         	= models.DateField(default=datetime.date.today,blank=False, null=True)
	ref_no       	= models.PositiveIntegerField()
	Party_ac     	= models.ForeignKey(ledger1,on_delete=models.CASCADE,related_name='partyledger')
	purchase     	= models.ForeignKey(ledger1,on_delete=models.CASCADE,related_name='purchaseledger')
	billname     	= models.CharField(max_length=32,default='Supplier')
	Address		 	= models.TextField(blank=True)
	GSTIN        	= models.CharField(max_length=32,blank=True)
	PAN          	= models.CharField(max_length=32,blank=True)
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
	State 		 	= models.CharField(max_length=100,choices=State_Name,default='Choose')
	Contact      	= models.BigIntegerField(blank=True,null=True)
	DeliveryNote 	= models.CharField(max_length=32,blank=True)
	Supplierref  	= models.CharField(max_length=32,blank=True)
	Mode         	= models.TextField(blank=True)
	sub_total 		= models.DecimalField(max_digits=10,decimal_places=2,blank=True, null=True)
	cgst_alltotal	= models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
	gst_alltotal	= models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
	tax_alltotal	= models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
	Total 		 	= models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)

	def __str__(self):
		return str(self.Party_ac)

	def get_absolute_url(self, **kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk1'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		return reverse("stockkeeping:purchasedetail", kwargs={'pk2':self.pk, 'pk1':company_details.pk, 'pk3':selectdatefield_details.pk })


	def save(self, **kwargs):
		super(Purchase, self).save()
		if not self.urlhash:
			if self.User.profile.user_type == 'Bussiness User':
				self.urlhash = 'BU'+ '-' + str(self.User.id) + '-'+ 'P' + '-' + '1' + '-'+ 'C' + str(self.Company.counter) + '-' + ('SP') + str(self.counter)
				Purchase.objects.filter(pk=self.pk).update(urlhash=self.urlhash)
			else:
				self.urlhash = 'PU'+ '-' + str(self.User.id) + '-'+ 'P' + '-' + '1' + '-'+ 'C' + str(self.Company.counter) + '-' + ('SP') + str(self.counter)
				Purchase.objects.filter(pk=self.pk).update(urlhash=self.urlhash)


class Sales(models.Model):
	User         	= models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=True,blank=True)
	Company      	= models.ForeignKey(company,on_delete=models.CASCADE,null=True,blank=True,related_name='companysales')
	counter 	 	= models.IntegerField(blank=True,null=True)
	urlhash 	 	= models.CharField(max_length=100, null=True, blank=True)
	ref_no       	= models.PositiveIntegerField()
	Party_ac     	= models.ForeignKey(ledger1,on_delete=models.CASCADE,related_name='partyledgersales')
	sales        	= models.ForeignKey(ledger1,on_delete=models.CASCADE,related_name='saleledger')
	billname     	= models.CharField(max_length=32,default='Customer')
	date         	= models.DateField(default=datetime.date.today,blank=False, null=True)
	Address		 	= models.TextField(blank=True)
	GSTIN        	= models.CharField(max_length=32,blank=True)
	PAN         	= models.CharField(max_length=32,blank=True)
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
	State 		 	= models.CharField(max_length=100,choices=State_Name,default='Choose')
	Contact      	= models.BigIntegerField(blank=True,null=True)
	DeliveryNote 	= models.CharField(max_length=32,blank=True)
	Supplierref  	= models.CharField(max_length=32,blank=True)
	Mode         	= models.TextField(blank=True)
	sub_total 	 	= models.DecimalField(max_digits=10,decimal_places=2,blank=True, null=True)
	cgst_alltotal	= models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
	gst_alltotal	= models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
	tax_alltotal	= models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
	Total 		 	= models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)

	def __str__(self):
		return str(self.Party_ac)

	def save(self, **kwargs):
		super(Sales, self).save()
		if not self.urlhash:
			if self.User.profile.user_type == 'Bussiness User':
				self.urlhash = 'BU'+ '-' + str(self.User.id) + '-'+ 'P' + '-' + '1' + '-'+ 'C' + str(self.Company.counter) + '-' + ('SS') + str(self.counter)
				Sales.objects.filter(pk=self.pk).update(urlhash=self.urlhash)
			else:
				self.urlhash = 'PU'+ '-' + str(self.User.id) + '-'+ 'P' + '-' + '1' + '-'+ 'C' + str(self.Company.counter) + '-' + ('SS') + str(self.counter)
				Sales.objects.filter(pk=self.pk).update(urlhash=self.urlhash)


class Stock_Total(models.Model):
	Company     = models.ForeignKey(company,on_delete=models.CASCADE,null=True,blank=True)
	purchases   = models.ForeignKey(Purchase,on_delete=models.CASCADE,null=True,blank=False,related_name='purchasetotal') 
	stockitem   = models.ForeignKey(Stockdata,on_delete=models.CASCADE,null=True,blank=True,related_name='purchasestock') 
	Quantity_p  = models.PositiveIntegerField(default=0)
	rate_p		= models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
	Disc_p    	= models.DecimalField(max_digits=10,decimal_places=2,default=0)
	gst_rate 	= models.DecimalField(default=0.00,max_digits=5,decimal_places=2,blank=True)
	tax 		= models.DecimalField(default=0.00,max_digits=5,decimal_places=2,blank=True)
	cgst 		= models.DecimalField(default=0.00,max_digits=5,decimal_places=2,blank=True)
	sgst 		= models.DecimalField(default=0.00,max_digits=5,decimal_places=2,blank=True)
	igst 		= models.DecimalField(default=0.00,max_digits=5,decimal_places=2,blank=True)
	ugst 		= models.DecimalField(default=0.00,max_digits=5,decimal_places=2,blank=True)
	cgst_total	= models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
	gst_total	= models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
	tax_total 	= models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
	Total_p     = models.DecimalField(max_digits=10,decimal_places=2,default=0.00,null=True,blank=True)
	grand_total = models.DecimalField(max_digits=10,decimal_places=2,default=0.00,null=True,blank=True)

	def __str__(self):
		return str(self.purchases)

	def save(self, **kwargs):
		if self.rate_p != None and self.Quantity_p != None and self.Disc_p != None:
			self.Total_p = self.rate_p * self.Quantity_p * (1 - (self.Disc_p/100))
		super(Stock_Total, self).save()

	def get_absolute_url(self, **kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk1'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		return reverse("stockkeeping:purchasedetail", kwargs={'pk2':self.purchases.pk, 'pk1':company_details.pk, 'pk3':selectdatefield_details.pk })




class Stock_Total_sales(models.Model):
	Company     = models.ForeignKey(company,on_delete=models.CASCADE,null=True,blank=True)
	sales       = models.ForeignKey(Sales,on_delete=models.CASCADE,null=True,blank=False,related_name='saletotal')
	stockitem   = models.ForeignKey(Stockdata,on_delete=models.CASCADE,null=True,blank=True,related_name='salestock') 
	Quantity    = models.PositiveIntegerField(null=True,blank=True)
	rate		= models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
	Disc    	= models.DecimalField(max_digits=10,decimal_places=2,default=0)
	gst_rate 	= models.DecimalField(default=0.00,max_digits=5,decimal_places=2,blank=True)
	cgst 		= models.DecimalField(default=0.00,max_digits=5,decimal_places=2,blank=True)
	tax 		= models.DecimalField(default=0.00,max_digits=5,decimal_places=2,blank=True)
	sgst 		= models.DecimalField(default=0.00,max_digits=5,decimal_places=2,blank=True)
	igst 		= models.DecimalField(default=0.00,max_digits=5,decimal_places=2,blank=True)
	ugst 		= models.DecimalField(default=0.00,max_digits=5,decimal_places=2,blank=True)
	cgst_total	= models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
	gst_total	= models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
	tax_total 	= models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
	Total 		= models.DecimalField(max_digits=10,decimal_places=2,default=0.00,null=True,blank=True)
	grand_total = models.DecimalField(max_digits=10,decimal_places=2,default=0.00,null=True,blank=True)

	def __str__(self):
		return str(self.sales)

	def save(self, **kwargs):
		if self.rate != None and self.Quantity != None and self.Disc != None:
			self.Total = self.rate * self.Quantity * (1 - (self.Disc/100))
		super(Stock_Total_sales, self).save()


class stock_journal(models.Model):
	User         		= models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=True,blank=True,related_name='user_closing')
	Company      		= models.ForeignKey(company,on_delete=models.CASCADE,null=True,blank=True,related_name='Company_stock_journal')
	date       			= models.DateField(default=datetime.date.today)
	stockitem 			= models.OneToOneField(Stockdata,on_delete=models.CASCADE,null=True,blank=True,related_name='closingstock')
	opening_stock   	= models.DecimalField(max_digits=10,decimal_places=2,null=True)
	closing_quantity 	= models.PositiveIntegerField(null=True,blank=True)
	closing_stock   	= models.DecimalField(max_digits=10,decimal_places=2,null=True)


	def __str__(self):
		return str(self.stockitem)

#########################  signals for the app accounting double entry(provided here due to django multiple import issue) ###################################

# signal implementation for accounting_double_entry.task module for celery implementation
@receiver(post_save, sender=ledger1)
def create_ledger_openingclosing(sender, instance, created, **kwargs):
	selectdatefield_details = get_object_or_404(selectdatefield, User=instance.User)
	create_ledger_openingclosing_task(instance.Company.pk,instance.pk,selectdatefield_details.pk)




##########################################################################################################

# @receiver(post_save, sender=Stockdata)
# def closing_stock_update(sender, instance, created, **kwargs):
# 	for obj in instance.User.user_closing.all():
# 		obj.save()

# @receiver(post_save, sender=Purchase)
# def update_ledger_closing_purchase(sender, instance, created, **kwargs):
# 	for obj in instance.User.user_ledger.all():
# 		obj.save()

# @receiver(post_save, sender=Sales)
# def update_ledger_closing_sales(sender, instance, created, **kwargs):
# 	for obj in instance.User.user_ledger.all():
# 		obj.save()

# @receiver(pre_save, sender=Purchase)
# def update_purchase_stocktotal(sender, instance, *args, **kwargs):
# 	for obj in instance.purchasetotal.all():
# 		obj.save()

# @receiver(pre_save, sender=Sales)
# def update_sales_stocktotal(sender, instance, *args, **kwargs):
# 	for obj in instance.saletotal.all():
# 		obj.save()


# @receiver(pre_save, sender=Stock_Total)
# def update_stockitem_purchase(sender, instance, *args, **kwargs):
# 	instance.stockitem.save()

# @receiver(pre_save, sender=Stock_Total_sales)
# def update_stockitem_sales(sender, instance, *args, **kwargs):
# 	instance.stockitem.save()

@receiver(post_save, sender=Purchase)
def update_ledgerpurchase(sender, instance, created, **kwargs):
	instance.Party_ac.save()
	grp_gst = ledger1.objects.filter(group1_Name__group_Name__icontains='GST')
	for g in grp_gst:
		g.save()


@receiver(post_save, sender=Sales)
def update_ledgersales(sender, instance, created, **kwargs):
	instance.Party_ac.save()
	grp_gst_1 = ledger1.objects.filter(group1_Name__group_Name__icontains='GST')
	for g in grp_gst_1:
		g.save()


@receiver(post_save, sender=Purchase)
def update_ledgerpurchase_group(sender, instance, created, **kwargs):
	instance.Party_ac.group1_Name.save()


@receiver(post_save, sender=Sales)
def update_ledgersales_group(sender, instance, created, **kwargs):
	instance.Party_ac.group1_Name.save()


@receiver(post_save, sender=Purchase)
def update_purchase_stockitems(sender, instance, created, **kwargs):
	purchase_stock = Stock_Total.objects.filter(purchases=instance)
	for obj in purchase_stock:
		if obj.stockitem:
			obj.stockitem.save()

@receiver(post_save, sender=Sales)
def update_sales_stockitems(sender, instance, created, **kwargs):
	sales_stock = Stock_Total_sales.objects.filter(sales=instance)
	for obj in sales_stock:
		if obj.stockitem:
			obj.stockitem.save()

@receiver(post_save, sender=Purchase)
def update_purchase_stockclosing(sender, instance, created, **kwargs):
	purchase_stock = Stock_Total.objects.filter(purchases=instance)
	for obj in purchase_stock:
		if obj.stockitem:
			obj.stockitem.closingstock.save()


@receiver(post_save, sender=Sales)
def update_sales_stockclosing(sender, instance, created, **kwargs):
	sales_stock = Stock_Total_sales.objects.filter(sales=instance)
	for obj in sales_stock:
		if obj.stockitem:
			obj.stockitem.closingstock.save()



@receiver(pre_save, sender=Stock_Total)
def update_gst_rate_purchase(sender, instance, *args, **kwargs):
	if instance.purchases.Company.gst_enabled == True:
		if instance.gst_rate == None or instance.gst_rate == 0:
			if instance.purchases.Company.composite_enable == False:
				if instance.purchases.State == instance.purchases.Company.State:
					instance.cgst = instance.stockitem.gst_rate / 2
					instance.sgst = instance.stockitem.gst_rate / 2
					instance.igst = 0
					instance.ugst = 0
				elif instance.purchases.Company.State == 'Andaman & Nicobar Islands' and instance.purchases.State == 'Andaman & Nicobar Islands':
					instance.cgst = instance.stockitem.gst_rate / 2
					instance.ugst = instance.stockitem.gst_rate / 2
					instance.igst = 0
					instance.sgst = 0
				elif instance.purchases.Company.State == 'Chandigarh' and instance.purchases.State == 'Chandigarh':
					instance.cgst = instance.stockitem.gst_rate / 2
					instance.ugst = instance.stockitem.gst_rate / 2
					instance.igst = 0
					instance.sgst = 0
				elif instance.purchases.Company.State == 'Dadra and Nagar Haveli' and instance.purchases.State == 'Dadra and Nagar Haveli':
					instance.cgst = instance.stockitem.gst_rate / 2
					instance.ugst = instance.stockitem.gst_rate / 2
					instance.igst = 0
					instance.sgst = 0
				elif instance.purchases.Company.State == 'Daman and Diu' and instance.purchases.State == 'Daman and Diu':
					instance.cgst = instance.stockitem.gst_rate / 2
					instance.ugst = instance.stockitem.gst_rate / 2
					instance.igst = 0
					instance.sgst = 0
				elif instance.purchases.Company.State == 'Lakshadweep' and instance.purchases.State == 'Lakshadweep':
					instance.cgst = instance.stockitem.gst_rate / 2
					instance.ugst = instance.stockitem.gst_rate / 2
					instance.igst = 0
					instance.sgst = 0
				else:
					instance.cgst = 0
					instance.igst = instance.stockitem.gst_rate 
					instance.ugst = 0
					instance.sgst = 0
			else:
				instance.tax = instance.stockitem.gst_rate 
		else:
			if instance.purchases.Company.composite_enable == False:
				if instance.purchases.State == instance.purchases.Company.State:
					instance.cgst = instance.gst_rate / 2
					instance.sgst = instance.gst_rate / 2
					instance.igst = 0
					instance.ugst = 0
				elif instance.purchases.Company.State == 'Andaman & Nicobar Islands' and instance.purchases.State == 'Andaman & Nicobar Islands':
					instance.cgst = instance.gst_rate / 2
					instance.ugst = instance.gst_rate / 2
					instance.igst = 0
					instance.sgst = 0
				elif instance.purchases.Company.State == 'Chandigarh' and instance.purchases.State == 'Chandigarh':
					instance.cgst = instance.gst_rate / 2
					instance.ugst = instance.gst_rate / 2
					instance.igst = 0
					instance.sgst = 0
				elif instance.purchases.Company.State == 'Dadra and Nagar Haveli' and instance.purchases.State == 'Dadra and Nagar Haveli':
					instance.cgst = instance.gst_rate / 2
					instance.ugst = instance.gst_rate / 2
					instance.igst = 0
					instance.sgst = 0
				elif instance.purchases.Company.State == 'Daman and Diu' and instance.purchases.State == 'Daman and Diu':
					instance.cgst = instance.gst_rate / 2
					instance.ugst = instance.gst_rate / 2
					instance.igst = 0
					instance.sgst = 0
				elif instance.purchases.Company.State == 'Lakshadweep' and instance.purchases.State == 'Lakshadweep':
					instance.cgst = instance.gst_rate / 2
					instance.ugst = instance.gst_rate / 2
					instance.igst = 0
					instance.sgst = 0
				else:
					instance.cgst = 0
					instance.igst = instance.gst_rate 
					instance.ugst = 0
					instance.sgst = 0
			else:
				instance.tax = instance.gst_rate 


@receiver(pre_save, sender=Stock_Total)
def update_gst_rate_purchasetotal(sender, instance, *args, **kwargs):
	if instance.purchases.Company.gst_enabled == True:
		if instance.purchases.Company.composite_enable == False:
			if instance.purchases.State == instance.purchases.Company.State:
				instance.cgst_total = instance.cgst * instance.Total_p / 100
				instance.gst_total 	= instance.sgst * instance.Total_p / 100
			elif instance.purchases.Company.State == 'Andaman & Nicobar Islands' and instance.purchases.State == 'Andaman & Nicobar Islands':
				instance.cgst_total = instance.cgst * instance.Total_p / 100
				instance.gst_total = instance.ugst * instance.Total_p / 100

			elif instance.purchases.Company.State == 'Chandigarh' and instance.purchases.State == 'Chandigarh':
				instance.cgst_total = instance.cgst * instance.Total_p / 100
				instance.gst_total = instance.ugst * instance.Total_p / 100

			elif instance.purchases.Company.State == 'Dadra and Nagar Haveli' and instance.purchases.State == 'Dadra and Nagar Haveli':
				instance.cgst_total = instance.cgst * instance.Total_p / 100
				instance.gst_total = instance.ugst * instance.Total_p / 100

			elif instance.purchases.Company.State == 'Daman and Diu' and instance.purchases.State == 'Daman and Diu':
				instance.cgst_total = instance.cgst * instance.Total_p / 100
				instance.gst_total = instance.ugst * instance.Total_p / 100

			elif instance.purchases.Company.State == 'Lakshadweep' and instance.purchases.State == 'Lakshadweep':
				instance.cgst_total = instance.cgst * instance.Total_p / 100
				instance.gst_total = instance.ugst * instance.Total_p / 100

			else:
				instance.gst_total = instance.igst * instance.Total_p / 100
			if instance.cgst_total == None:
				instance.grand_total = instance.Total_p + instance.gst_total 
			else:
				instance.grand_total = instance.Total_p + instance.cgst_total + instance.gst_total 
		else:
			instance.gst_total = instance.tax * instance.Total_p / 100
			instance.tax_total = instance.tax * instance.Total_p / 100
			instance.grand_total = instance.Total_p + instance.gst_total 


@receiver(pre_save, sender=Stock_Total_sales)
def update_gst_rate(sender, instance, *args, **kwargs):
	if instance.sales.Company.gst_enabled == True:
		if instance.gst_rate == None or instance.gst_rate == 0:
			if instance.sales.Company.composite_enable == False:
				if instance.sales.State == instance.sales.Company.State:
					instance.cgst = instance.stockitem.gst_rate / 2
					instance.sgst = instance.stockitem.gst_rate / 2
					instance.igst = 0
					instance.ugst = 0
				elif instance.sales.Company.State == 'Andaman & Nicobar Islands' and instance.sales.State == 'Andaman & Nicobar Islands':
					instance.cgst = instance.stockitem.gst_rate / 2
					instance.ugst = instance.stockitem.gst_rate / 2
					instance.igst = 0
					instance.sgst = 0
				elif instance.sales.Company.State == 'Chandigarh' and instance.sales.State == 'Chandigarh':
					instance.cgst = instance.stockitem.gst_rate / 2
					instance.ugst = instance.stockitem.gst_rate / 2
					instance.igst = 0
					instance.sgst = 0
				elif instance.sales.Company.State == 'Dadra and Nagar Haveli' and instance.sales.State == 'Dadra and Nagar Haveli':
					instance.cgst = instance.stockitem.gst_rate / 2
					instance.ugst = instance.stockitem.gst_rate / 2
					instance.igst = 0
					instance.sgst = 0
				elif instance.sales.Company.State == 'Daman and Diu' and instance.sales.State == 'Daman and Diu':
					instance.cgst = instance.stockitem.gst_rate / 2
					instance.ugst = instance.stockitem.gst_rate / 2
					instance.igst = 0
					instance.sgst = 0
				elif instance.sales.Company.State == 'Lakshadweep' and instance.sales.State == 'Lakshadweep':
					instance.cgst = instance.stockitem.gst_rate / 2
					instance.ugst = instance.stockitem.gst_rate / 2
					instance.igst = 0
					instance.sgst = 0
				else:
					instance.cgst = 0
					instance.igst = instance.stockitem.gst_rate 
					instance.ugst = 0
					instance.sgst = 0
			else:
				instance.tax = instance.stockitem.gst_rate 
		else:
			if instance.sales.Company.composite_enable == False:
				if instance.sales.State == instance.sales.Company.State:
					instance.cgst = instance.gst_rate / 2
					instance.sgst = instance.gst_rate / 2
					instance.igst = 0
					instance.ugst = 0
				elif instance.sales.Company.State == 'Andaman & Nicobar Islands' and instance.sales.State == 'Andaman & Nicobar Islands':
					instance.cgst = instance.gst_rate / 2
					instance.ugst = instance.gst_rate / 2
					instance.igst = 0
					instance.sgst = 0
				elif instance.sales.Company.State == 'Chandigarh' and instance.sales.State == 'Chandigarh':
					instance.cgst = instance.gst_rate / 2
					instance.ugst = instance.gst_rate / 2
					instance.igst = 0
					instance.sgst = 0
				elif instance.sales.Company.State == 'Dadra and Nagar Haveli' and instance.sales.State == 'Dadra and Nagar Haveli':
					instance.cgst = instance.gst_rate / 2
					instance.ugst = instance.gst_rate / 2
					instance.igst = 0
					instance.sgst = 0
				elif instance.sales.Company.State == 'Daman and Diu' and instance.sales.State == 'Daman and Diu':
					instance.cgst = instance.gst_rate / 2
					instance.ugst = instance.gst_rate / 2
					instance.igst = 0
					instance.sgst = 0
				elif instance.sales.Company.State == 'Lakshadweep' and instance.sales.State == 'Lakshadweep':
					instance.cgst = instance.gst_rate / 2
					instance.ugst = instance.gst_rate / 2
					instance.igst = 0
					instance.sgst = 0
				else:
					instance.cgst = 0
					instance.igst = instance.gst_rate
					instance.ugst = 0
					instance.sgst = 0
			else:
				instance.tax = instance.gst_rate 	


@receiver(pre_save, sender=Stock_Total_sales)
def update_gst_rate_saletotal(sender, instance, *args, **kwargs):
	if instance.sales.Company.gst_enabled == True:
		if instance.sales.Company.composite_enable == False:
			if instance.sales.State == instance.sales.Company.State:
				instance.cgst_total = instance.cgst * instance.Total / 100
				instance.gst_total 	= instance.sgst * instance.Total / 100
				
			elif instance.sales.Company.State == 'Andaman & Nicobar Islands' and instance.sales.State == 'Andaman & Nicobar Islands':
				instance.cgst_total = instance.cgst * instance.Total / 100
				instance.gst_total = instance.ugst * instance.Total / 100

			elif instance.sales.Company.State == 'Chandigarh' and instance.sales.State == 'Chandigarh':
				instance.cgst_total = instance.cgst * instance.Total / 100
				instance.gst_total = instance.ugst * instance.Total / 100

			elif instance.sales.Company.State == 'Dadra and Nagar Haveli' and instance.sales.State == 'Dadra and Nagar Haveli':
				instance.cgst_total = instance.cgst * instance.Total / 100
				instance.gst_total = instance.ugst * instance.Total / 100

			elif instance.sales.Company.State == 'Daman and Diu' and instance.sales.State == 'Daman and Diu':
				instance.cgst_total = instance.cgst * instance.Total / 100
				instance.gst_total = instance.ugst * instance.Total / 100

			elif instance.sales.Company.State == 'Lakshadweep' and instance.sales.State == 'Lakshadweep':
				instance.cgst_total = instance.cgst * instance.Total / 100
				instance.gst_total = instance.ugst * instance.Total / 100

			else:
				instance.gst_total = instance.igst * instance.Total / 100
			if instance.cgst_total == None:
				instance.grand_total = instance.Total + instance.gst_total 
			else:
				instance.grand_total = instance.Total + instance.cgst_total + instance.gst_total
		else:
			instance.gst_total = instance.tax * instance.Total / 100
			instance.tax_total = instance.tax * instance.Total / 100
			instance.grand_total = instance.Total + instance.gst_total 
			
	
@receiver(pre_save, sender=Purchase)
def update_subtotal(sender,instance,*args,**kwargs):
	total = instance.purchasetotal.aggregate(the_sum=Coalesce(Sum('Total_p'), Value(0)))['the_sum']
	instance.sub_total = total

@receiver(pre_save, sender=Purchase)
def update_totalgst(sender,instance,*args,**kwargs):
	total_cgst = instance.purchasetotal.aggregate(the_sum=Coalesce(Sum('cgst_total'), Value(0)))['the_sum']
	total_gst = instance.purchasetotal.aggregate(the_sum=Coalesce(Sum('gst_total'), Value(0)))['the_sum']
	total 	= instance.purchasetotal.aggregate(the_sum=Coalesce(Sum('grand_total'), Value(0)))['the_sum']
	instance.cgst_alltotal = total_cgst
	instance.gst_alltotal = total_gst
	instance.Total = total



@receiver(pre_save, sender=Purchase)
def update_total_tax(sender,instance,*args,**kwargs):
	total_tax = instance.purchasetotal.aggregate(the_sum=Coalesce(Sum('tax_total'), Value(0)))['the_sum']
	instance.tax_alltotal = total_tax

@receiver(pre_save, sender=Sales)
def update_total_tax_sales(sender,instance,*args,**kwargs):
	total_tax = instance.saletotal.aggregate(the_sum=Coalesce(Sum('tax_total'), Value(0)))['the_sum']
	instance.tax_alltotal = total_tax



@receiver(pre_save, sender=Sales)
def update_total_sales(sender,instance,*args,**kwargs):
	total1 = instance.saletotal.aggregate(the_sum=Coalesce(Sum('Total'), Value(0)))['the_sum']
	instance.sub_total = total1

@receiver(pre_save, sender=Sales)
def update_totalgst_sales(sender,instance,*args,**kwargs):
	total_cgst = instance.saletotal.aggregate(the_sum=Coalesce(Sum('cgst_total'), Value(0)))['the_sum']
	total_gst = instance.saletotal.aggregate(the_sum=Coalesce(Sum('gst_total'), Value(0)))['the_sum']
	total 	= instance.saletotal.aggregate(the_sum=Coalesce(Sum('grand_total'), Value(0)))['the_sum']
	instance.cgst_alltotal = total_cgst
	instance.gst_alltotal = total_gst
	instance.Total = total


@receiver(pre_save, sender=Purchase)
def user_created(sender,instance,*args,**kwargs):
	c = journal.objects.filter(User=instance.User, Company=instance.Company).count() + 1
	if instance.sub_total != None:
		journal.objects.update_or_create(
			By = instance.purchase,
			voucher_id=instance.id,
			defaults={
				'counter' : c,
				'User' : instance.User,
				'Company' : instance.Company,
				'Date': instance.date,
				'To' : instance.Party_ac,
				'voucher_type' : "Purchase",
				'Debit': instance.sub_total,
				'Credit': instance.sub_total}
			)

@receiver(pre_delete, sender=Purchase)
def delete_related_journal(sender, instance, **kwargs):
	journal.objects.filter(User=instance.User,Company=instance.Company,voucher_id=instance.id).delete()

@receiver(pre_save, sender=Purchase)
def user_created_plpurchase(sender,instance,*args,**kwargs):
	c = Pl_journal.objects.filter(User=instance.User, Company=instance.Company).count() + 1
	if instance.sub_total != None:
		Pl_journal.objects.update_or_create(
			By = ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='Profit & Loss A/c').first(),
			voucher_id=instance.id,
			defaults={
				'counter' : c,
				'User' : instance.User,
				'Company' : instance.Company,
				'Date': instance.date,
				'To' : instance.purchase,
				'voucher_type' : "Purchase",
				'Debit': instance.sub_total,
				'Credit': instance.sub_total,
				'tax_expense':True,
				'it_head': 'Profit_&_Gains_of_Business_and_Professions'}
			)

@receiver(pre_delete, sender=Purchase)
def delete_related_pljournal(sender, instance, **kwargs):
	Pl_journal.objects.filter(User=instance.User,Company=instance.Company,voucher_id=instance.id).delete()


@receiver(pre_save, sender=Purchase)
def user_created_purchase_cgst(sender,instance,*args,**kwargs):
	c = journal.objects.filter(User=instance.User, Company=instance.Company).count() + 1
	if instance.cgst_alltotal != None and instance.cgst_alltotal != 0:
		journal.objects.update_or_create(
				By = ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='CGST').first(),
				voucher_id=instance.id,
				defaults={
					'counter' : c,
					'User' : instance.User,
					'Company' : instance.Company,
					'Date': instance.date,
					'To' : instance.Party_ac,
					'voucher_type' : "Journal",
					'Debit': instance.gst_alltotal,
					'Credit': instance.gst_alltotal}
				)


@receiver(pre_save, sender=Purchase)
def user_created_purchase_stategst(sender,instance,*args,**kwargs):
	c = journal.objects.filter(User=instance.User, Company=instance.Company).count() + 1
	if instance.Company.composite_enable == False:
		if instance.gst_alltotal != None and instance.State == instance.Company.State:
			journal.objects.update_or_create(
				By = ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='SGST').first(),
				voucher_id=instance.id,
				defaults={
					'counter' : c,
					'User' : instance.User,
					'Company' : instance.Company,
					'Date': instance.date,
					'To' : instance.Party_ac,
					'voucher_type' : "Journal",
					'Debit': instance.gst_alltotal,
					'Credit': instance.gst_alltotal}
				)
		elif instance.gst_alltotal != None and instance.Company.State == 'Andaman & Nicobar Islands' and instance.State == 'Andaman & Nicobar Islands':
			journal.objects.update_or_create(
				By = ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='UTGST').first(),
				voucher_id=instance.id,
				defaults={
					'counter' : c,
					'User' : instance.User,
					'Company' : instance.Company,
					'Date': instance.date,
					'To' : instance.Party_ac,
					'voucher_type' : "Journal",
					'Debit': instance.gst_alltotal,
					'Credit': instance.gst_alltotal}
				)
		elif instance.gst_alltotal != None and instance.Company.State == 'Chandigarh' and instance.State == 'Chandigarh':
			journal.objects.update_or_create(
				By = ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='UTGST').first(),
				voucher_id=instance.id,
				defaults={
					'counter' : c,
					'User' : instance.User,
					'Company' : instance.Company,
					'Date': instance.date,
					'To' : instance.Party_ac,
					'voucher_type' : "Journal",
					'Debit': instance.gst_alltotal,
					'Credit': instance.gst_alltotal}
				)
		elif instance.gst_alltotal != None and instance.Company.State == 'Dadra and Nagar Haveli' and instance.State == 'Dadra and Nagar Haveli':
			journal.objects.update_or_create(
				By = ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='UTGST').first(),
				voucher_id=instance.id,
				defaults={
					'counter' : c,
					'User' : instance.User,
					'Company' : instance.Company,
					'Date': instance.date,
					'To' : instance.Party_ac,
					'voucher_type' : "Journal",
					'Debit': instance.gst_alltotal,
					'Credit': instance.gst_alltotal}
				)
		elif instance.gst_alltotal != None and instance.Company.State == 'Daman and Diu' and instance.State == 'Daman and Diu':
			journal.objects.update_or_create(
				By = ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='UTGST').first(),
				voucher_id=instance.id,
				defaults={
					'counter' : c,
					'User' : instance.User,
					'Company' : instance.Company,
					'Date': instance.date,
					'To' : instance.Party_ac,
					'voucher_type' : "Journal",
					'Debit': instance.gst_alltotal,
					'Credit': instance.gst_alltotal}
				)
		elif instance.gst_alltotal != None and instance.Company.State == 'Lakshadweep' and instance.State == 'Lakshadweep':
			journal.objects.update_or_create(
				By = ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='UTGST').first(),
				voucher_id=instance.id,
				defaults={
					'counter' : c,
					'User' : instance.User,
					'Company' : instance.Company,
					'Date': instance.date,
					'To' : instance.Party_ac,
					'voucher_type' : "Journal",
					'Debit': instance.gst_alltotal,
					'Credit': instance.gst_alltotal}
				)
		else:
			if instance.gst_alltotal != None:
				journal.objects.update_or_create(
				By = ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='IGST').first(),
				voucher_id=instance.id,
				defaults={
					'counter' : c,
					'User' : instance.User,
					'Company' : instance.Company,
					'Date': instance.date,
					'To' : instance.Party_ac,
					'voucher_type' : "Journal",
					'Debit': instance.gst_alltotal,
					'Credit': instance.gst_alltotal}
				)
	else:
		if instance.gst_alltotal != None:
			journal.objects.update_or_create(
					By = ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='Tax').first(),
					voucher_id=instance.id,
					defaults={
						'counter' : c,
						'User' : instance.User,
						'To' : instance.Party_ac,
						'Date': instance.date,
						'voucher_type' : "Journal",
						'Debit': instance.gst_alltotal,
						'Credit': instance.gst_alltotal}
					)



@receiver(pre_save, sender=Sales)
def user_created_sales(sender,instance,*args,**kwargs):
	c = journal.objects.filter(User=instance.User, Company=instance.Company).count() + 1
	if instance.sub_total != None:
		journal.objects.update_or_create(
			To = instance.sales,
			voucher_id=instance.id,
			defaults={
				'counter' : c,
				'User' : instance.User,
				'Company' : instance.Company,
				'Date': instance.date,
				'By' : instance.Party_ac,
				'voucher_type' : "Sales",
				'Debit': instance.sub_total,
				'Credit': instance.sub_total}
			)

@receiver(pre_delete, sender=Sales)
def delete_related_journal_sales(sender, instance, **kwargs):
	journal.objects.filter(User=instance.User,Company=instance.Company,voucher_id=instance.id).delete()

@receiver(pre_save, sender=Sales)
def user_created_plsales(sender,instance,*args,**kwargs):
	c = Pl_journal.objects.filter(User=instance.User, Company=instance.Company).count() + 1
	if instance.sub_total != None:
		Pl_journal.objects.update_or_create(
			To = ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='Profit & Loss A/c').first(),
			voucher_id=instance.id,
			defaults={
				'counter' : c,
				'User' : instance.User,
				'Company' : instance.Company,
				'Date': instance.date,
				'By' : instance.sales,
				'voucher_type' : "Sales", 
				'Debit': instance.sub_total,
				'Credit': instance.sub_total}
			)

@receiver(pre_delete, sender=Sales)
def delete_related_pljournal_sales(sender, instance, **kwargs):
	Pl_journal.objects.filter(User=instance.User,Company=instance.Company,voucher_id=instance.id).delete()

@receiver(pre_save, sender=Sales)
def user_created_sales_cgst(sender,instance,*args,**kwargs):
	c = journal.objects.filter(User=instance.User, Company=instance.Company).count() + 1
	if instance.cgst_alltotal != None and instance.cgst_alltotal != 0:
		journal.objects.update_or_create(
				To = ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='CGST').first(),
				voucher_id=instance.id,
				defaults={
					'counter' : c,
					'User' : instance.User,
					'Company' : instance.Company,
					'By' : instance.Party_ac,
					'Date': instance.date,
					'voucher_type' : "Journal", 
					'Debit': instance.gst_alltotal,
					'Credit': instance.gst_alltotal}
				)

@receiver(pre_save, sender=Sales)
def user_created_sales_stategst(sender,instance,*args,**kwargs):
	c = journal.objects.filter(User=instance.User, Company=instance.Company).count() + 1
	if instance.Company.composite_enable == False:
		if instance.gst_alltotal != None and instance.State == instance.Company.State:
			journal.objects.update_or_create(
				To = ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='SGST').first(),
				voucher_id=instance.id,
				defaults={
					'counter' : c,
					'User' : instance.User,
					'Company' : instance.Company,
					'By' : instance.Party_ac,
					'Date': instance.date,
					'voucher_type' : "Journal", 
					'Debit': instance.gst_alltotal,
					'Credit': instance.gst_alltotal}
				)	
		elif instance.gst_alltotal != None and instance.Company.State == 'Andaman & Nicobar Islands' and instance.State == 'Andaman & Nicobar Islands':
			journal.objects.update_or_create(
				To = ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='UTGST').first(),
				voucher_id=instance.id,
				defaults={
					'counter' : c,
					'User' : instance.User,
					'Company' : instance.Company,
					'By' : instance.Party_ac,
					'Date': instance.date,
					'voucher_type' : "Journal", 
					'Debit': instance.gst_alltotal,
					'Credit': instance.gst_alltotal}
				)
		elif instance.gst_alltotal != None and instance.Company.State == 'Chandigarh' and instance.State == 'Chandigarh':
			journal.objects.update_or_create(
				To = ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='UTGST').first(),
				voucher_id=instance.id,
				defaults={
					'counter' : c,
					'User' : instance.User,
					'Company' : instance.Company,
					'By' : instance.Party_ac,
					'Date': instance.date,
					'voucher_type' : "Journal", 
					'Debit': instance.gst_alltotal,
					'Credit': instance.gst_alltotal}
				)
		elif instance.gst_alltotal != None and instance.Company.State == 'Dadra and Nagar Haveli' and instance.State == 'Dadra and Nagar Haveli':
			journal.objects.update_or_create(
				To = ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='UTGST').first(),
				voucher_id=instance.id,
				defaults={
					'counter' : c,
					'User' : instance.User,
					'Company' : instance.Company,
					'By' : instance.Party_ac,
					'Date': instance.date,
					'voucher_type' : "Journal", 
					'Debit': instance.gst_alltotal,
					'Credit': instance.gst_alltotal}
				)
		elif instance.gst_alltotal != None and instance.Company.State == 'Daman and Diu' and instance.State == 'Daman and Diu':
			journal.objects.update_or_create(
				To = ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='UTGST').first(),
				voucher_id=instance.id,
				defaults={
					'counter' : c,
					'User' : instance.User,
					'Company' : instance.Company,
					'By' : instance.Party_ac,
					'Date': instance.date,
					'voucher_type' : "Journal", 
					'Debit': instance.gst_alltotal,
					'Credit': instance.gst_alltotal}
				)
		elif instance.gst_alltotal != None and instance.Company.State == 'Lakshadweep' and instance.State == 'Lakshadweep':
			journal.objects.update_or_create(
				To = ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='UTGST').first(),
				voucher_id=instance.id,
				defaults={
					'counter' : c,
					'User' : instance.User,
					'Company' : instance.Company,
					'By' : instance.Party_ac,
					'Date': instance.date,
					'voucher_type' : "Journal", 
					'Debit': instance.gst_alltotal,
					'Credit': instance.gst_alltotal}
				)
		else:
			if instance.gst_alltotal != None:
				journal.objects.update_or_create(
				To = ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='IGST').first(),
				voucher_id=instance.id,
				defaults={
					'counter' : c,
					'User' : instance.User,
					'Company' : instance.Company,
					'By' : instance.Party_ac,
					'Date': instance.date,
					'voucher_type' : "Journal", 
					'Debit': instance.gst_alltotal,
					'Credit': instance.gst_alltotal}
				)
	else:
		if instance.gst_alltotal != None:
				journal.objects.update_or_create(
				To = ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='Tax').first(),
				voucher_id=instance.id,
				defaults={
					'counter' : c,
					'User' : instance.User,
					'Company' : instance.Company,
					'By' : instance.Party_ac,
					'Date': instance.date,
					'voucher_type' : "Journal", 
					'Debit': instance.gst_alltotal,
					'Credit': instance.gst_alltotal}
				)


@receiver(post_save, sender=Stockdata)
def create_default_stock_ledger(sender, instance, created, **kwargs):
	if created:
		stock_journal.objects.create(User=instance.User,Company=instance.Company,stockitem=instance)

	

@receiver(post_save, sender=stock_journal) # shall be triggered when the above signal is passed since stock journal model is created and is the sender here.
def create_stock_ledger(sender, instance, created, **kwargs):
	selectdatefield_details = get_object_or_404(selectdatefield,User=instance.User)
	c = Pl_journal.objects.filter(User=instance.User, Company=instance.Company).count() + 1
	if instance.closing_stock != None:
		Pl_journal.objects.update_or_create(
			By = ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='Stock A/c').first(),
			To = ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='Profit & Loss A/c').first(),
			stock = instance.stockitem.stock_name,
			voucher_id = instance.id,
			defaults={
				'counter' : c,
				'User' : instance.User,
				'Company' : instance.Company,
				'Date': selectdatefield_details.End_Date,
				'voucher_type' : "Journal", 
				'Debit': instance.closing_stock,
				'Credit': instance.closing_stock}
			)

@receiver(post_save, sender=stock_journal) # shall be triggered when the above signal is passed since stock journal model is created and is the sender here.
def create_stock_ledger_opening(sender, instance, created, **kwargs):
	selectdatefield_details = get_object_or_404(selectdatefield,User=instance.User)
	c = Pl_journal.objects.filter(User=instance.User, Company=instance.Company).count() + 1
	if instance.opening_stock != None:
		Pl_journal.objects.update_or_create(
			By = ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='Profit & Loss A/c').first(),
			To = ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='Stock A/c').first(),
			stock = instance.stockitem.stock_name,
			voucher_id = instance.id,
			defaults={
				'counter' : c,
				'User' 	: instance.User,
				'Company' : instance.Company,
				'Date': selectdatefield_details.Start_Date,
				'voucher_type' : "Journal", 
				'Debit': instance.opening_stock,
				'Credit': instance.opening_stock}
			)


@receiver(pre_delete, sender=stock_journal)
def delete_related_journal_stock(sender, instance, **kwargs):
	Pl_journal.objects.filter(User=instance.User,Company=instance.Company,voucher_id=instance.id).delete()