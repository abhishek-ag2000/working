from django.db import models
from django.conf import settings
import datetime
from userprofile.models import Product_activation
from django.db.models.signals import pre_save,post_save,post_delete,pre_delete
from accounting_double_entry.models import Pl_journal,journal,group1,ledger1,selectdatefield
from django.dispatch import receiver
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.db.models.functions import Coalesce 
from django.db.models import Case, When, CharField, Value, Sum, F, ExpressionWrapper, Subquery, OuterRef, Count
from company.models import company
from django.shortcuts import get_object_or_404
from datetime import datetime
from django.utils import timezone
from stockkeeping.models import Stockdata,Stock_Total
from stockkeeping.tasks import user_created_stock_ledger_task

# Create your models here.	

class Purchase_accounts(models.Model):
	User         	= models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=True,blank=True,related_name='Userpurchase_account')
	Company      	= models.ForeignKey(company,on_delete=models.CASCADE,null=True,blank=True,related_name='Companypurchase_account')
	counter 	 	= models.IntegerField(blank=True,null=True)
	urlhash 	 	= models.CharField(max_length=100, null=True, blank=True)
	date         	= models.DateField(default=timezone.now,blank=False, null=True)
	ref_no       	= models.PositiveIntegerField()
	Party_ac     	= models.ForeignKey(ledger1,on_delete=models.CASCADE,related_name='partyledger_account')
	purchase     	= models.ForeignKey(ledger1,on_delete=models.CASCADE,related_name='purchaseledger_account')
	billname     	= models.CharField(max_length=32,default='Supplier')
	Address		 	= models.CharField(max_length=32,blank=True)
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
	Total 		 	= models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)

	def __str__(self):
		return str(self.Party_ac) 

	def save(self, **kwargs):
		super(Purchase, self).save()
		if not self.urlhash:
			if self.User.profile.user_type == 'Bussiness User':
				self.urlhash = 'BU'+ '-' + str(self.User.id) + '-'+ 'P' + '-' + '1' + '-'+ 'C' + str(self.Company.counter) + '-' + ('SP') + str(self.counter)
				Purchase.objects.filter(pk=self.pk).update(urlhash=self.urlhash)
			else:
				self.urlhash = 'PU'+ '-' + str(self.User.id) + '-'+ 'P' + '-' + '1' + '-'+ 'C' + str(self.Company.counter) + '-' + ('SP') + str(self.counter)
				Purchase.objects.filter(pk=self.pk).update(urlhash=self.urlhash)

class Sales_accounts(models.Model):
	User         	= models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=True,blank=True,related_name='Usersales_account')
	Company      	= models.ForeignKey(company,on_delete=models.CASCADE,null=True,blank=True,related_name='Companysales_account')
	counter 	 	= models.IntegerField(blank=True,null=True)
	urlhash 	 	= models.CharField(max_length=100, null=True, blank=True)
	ref_no       	= models.PositiveIntegerField()
	Party_ac     	= models.ForeignKey(ledger1,on_delete=models.CASCADE,related_name='partyledgersales_account')
	sales        	= models.ForeignKey(ledger1,on_delete=models.CASCADE,related_name='saleledger_account')
	billname     	= models.CharField(max_length=32,default='Customer')
	date         	= models.DateField(default=timezone.now,blank=False, null=True)
	Address		 	= models.CharField(max_length=32,blank=True)
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


class Purchase_Total(models.Model):
	purchases   	= models.ForeignKey(Purchase_accounts,on_delete=models.CASCADE,null=True,blank=False,related_name='purchasetotal_accounts') 
	purchase_ledger	= models.ForeignKey(ledger1,on_delete=models.CASCADE,null=True,blank=True,related_name='purchasestock_accounts') 
	Quantity_p  	= models.PositiveIntegerField(default=0)
	rate_p			= models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
	gst_rate 		= models.DecimalField(default=0.00,max_digits=5,decimal_places=2,blank=True)
	Disc_p    		= models.DecimalField(max_digits=10,decimal_places=2,default=0)
	cgst 			= models.DecimalField(default=0.00,max_digits=5,decimal_places=2,blank=True)
	sgst 			= models.DecimalField(default=0.00,max_digits=5,decimal_places=2,blank=True)
	igst 			= models.DecimalField(default=0.00,max_digits=5,decimal_places=2,blank=True)
	ugst 			= models.DecimalField(default=0.00,max_digits=5,decimal_places=2,blank=True)
	cgst_total		= models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
	gst_total		= models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
	Total_p     	= models.DecimalField(max_digits=10,decimal_places=2,default=0.00,null=True,blank=True)
	grand_total 	= models.DecimalField(max_digits=10,decimal_places=2,default=0.00,null=True,blank=True)

	def __str__(self):
		return str(self.purchases)



class Sales_total(models.Model):
	sales       	= models.ForeignKey(Sales_accounts,on_delete=models.CASCADE,null=True,blank=False,related_name='saletotal_accounts')
	sales_ledger   	= models.ForeignKey(ledger1,on_delete=models.CASCADE,null=True,blank=True,related_name='salestock_accounts') 
	Quantity    	= models.PositiveIntegerField(null=True,blank=True)
	rate			= models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
	gst_rate 		= models.DecimalField(default=0.00,max_digits=5,decimal_places=2,blank=True)
	Disc    		= models.DecimalField(max_digits=10,decimal_places=2,default=0)
	cgst 			= models.DecimalField(default=0.00,max_digits=5,decimal_places=2,blank=True)
	sgst 			= models.DecimalField(default=0.00,max_digits=5,decimal_places=2,blank=True)
	igst 			= models.DecimalField(default=0.00,max_digits=5,decimal_places=2,blank=True)
	ugst 			= models.DecimalField(default=0.00,max_digits=5,decimal_places=2,blank=True)
	cgst_total		= models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
	gst_total		= models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
	Total 			= models.DecimalField(max_digits=10,decimal_places=2,default=0.00,null=True,blank=True)
	grand_total 	= models.DecimalField(max_digits=10,decimal_places=2,default=0.00,null=True,blank=True)

	def __str__(self):
		return str(self.sales)


@receiver(pre_save, sender=Purchase_Total)
def update_gst_rate_purchase_account(sender, instance, *args, **kwargs):
	if instance.purchases.State == instance.purchases.Company.State:
		instance.cgst = instance.gst_rate / 2
		instance.sgst = instance.gst_rate / 2
		instance.igst = 0
		instance.ugst = 0
	elif instance.purchases.State == 'Delhi':
		instance.cgst = instance.gst_rate / 2
		instance.sgst = instance.gst_rate / 2
		instance.igst = 0
		instance.ugst = 0
	elif instance.purchases.State == 'Puducherry':
		instance.cgst = instance.gst_rate / 2
		instance.sgst = instance.gst_rate / 2
		instance.igst = 0
		instance.ugst = 0
	elif instance.purchases.State == 'Andaman & Nicobar Islands':
		instance.cgst = instance.gst_rate / 2
		instance.ugst = instance.gst_rate / 2
		instance.igst = 0
		instance.sgst = 0
	elif instance.purchases.State == 'Chandigarh':
		instance.cgst = instance.gst_rate / 2
		instance.ugst = instance.gst_rate / 2
		instance.igst = 0
		instance.sgst = 0
	elif instance.purchases.State == 'Dadra and Nagar Haveli':
		instance.cgst = instance.gst_rate / 2
		instance.ugst = instance.gst_rate / 2
		instance.igst = 0
		instance.sgst = 0
	elif instance.purchases.State == 'Daman and Diu':
		instance.cgst = instance.gst_rate / 2
		instance.ugst = instance.gst_rate / 2
		instance.igst = 0
		instance.sgst = 0
	elif instance.purchases.State == 'Lakshadweep':
		instance.cgst = instance.gst_rate / 2
		instance.ugst = instance.gst_rate / 2
		instance.igst = 0
		instance.sgst = 0
	else:
		instance.cgst = 0
		instance.igst = instance.gst_rate 
		instance.ugst = 0
		instance.sgst = 0



@receiver(pre_save, sender=Purchase_Total)
def update_amount_purchase_account(sender, instance, *args, **kwargs):
	instance.Total_p = instance.rate_p * instance.Quantity_p * (1 - (instance.Disc_p/100))

@receiver(pre_save, sender=Purchase_Total)
def update_gst_rate_purchasetotal_account(sender, instance, *args, **kwargs):
	if instance.purchases.State == instance.purchases.Company.State:
		instance.cgst_total = instance.cgst * instance.Total_p / 100
		instance.gst_total 	= instance.sgst * instance.Total_p / 100

	elif instance.purchases.State == 'Delhi':
		instance.cgst_total = instance.cgst * instance.Total_p / 100
		instance.gst_total 	= instance.sgst * instance.Total_p / 100

	elif instance.purchases.State == 'Puducherry':
		instance.cgst_total = instance.cgst * instance.Total_p / 100
		instance.gst_total 	= instance.sgst * instance.Total_p / 100

	elif instance.purchases.State == 'Andaman & Nicobar Islands':
		instance.cgst_total = instance.cgst * instance.Total_p / 100
		instance.gst_total = instance.ugst * instance.Total_p / 100

	elif instance.purchases.State == 'Chandigarh':
		instance.cgst_total = instance.cgst * instance.Total_p / 100
		instance.gst_total = instance.ugst * instance.Total_p / 100

	elif instance.purchases.State == 'Dadra and Nagar Haveli':
		instance.cgst_total = instance.cgst * instance.Total_p / 100
		instance.gst_total = instance.ugst * instance.Total_p / 100

	elif instance.purchases.State == 'Daman and Diu':
		instance.cgst_total = instance.cgst * instance.Total_p / 100
		instance.gst_total = instance.ugst * instance.Total_p / 100

	elif instance.purchases.State == 'Lakshadweep':
		instance.cgst_total = instance.cgst * instance.Total_p / 100
		instance.gst_total = instance.ugst * instance.Total_p / 100

	else:
		instance.gst_total = instance.igst * instance.Total_p / 100
	if instance.cgst_total == None:
		instance.grand_total = instance.Total_p + instance.gst_total 
	else:
		instance.grand_total = instance.Total_p + instance.cgst_total + instance.gst_total 



@receiver(pre_save, sender=Sales_total)
def update_gst_rate_account(sender, instance, *args, **kwargs):
	if instance.sales.State == instance.sales.Company.State:
		instance.cgst = instance.gst_rate / 2
		instance.sgst = instance.gst_rate / 2
		instance.igst = 0
		instance.ugst = 0
	elif instance.sales.State == 'Delhi':
		instance.cgst = instance.gst_rate / 2
		instance.sgst = instance.gst_rate / 2
		instance.igst = 0
		instance.ugst = 0
	elif instance.sales.State == 'Puducherry':
		instance.cgst = instance.gst_rate / 2
		instance.sgst = instance.gst_rate / 2
		instance.igst = 0
		instance.ugst = 0
	elif instance.sales.State == 'Andaman & Nicobar Islands':
		instance.cgst = instance.gst_rate / 2
		instance.ugst = instance.gst_rate / 2
		instance.igst = 0
		instance.sgst = 0
	elif instance.sales.State == 'Chandigarh':
		instance.cgst = instance.gst_rate / 2
		instance.ugst = instance.gst_rate / 2
		instance.igst = 0
		instance.sgst = 0
	elif instance.sales.State == 'Dadra and Nagar Haveli':
		instance.cgst = instance.gst_rate / 2
		instance.ugst = instance.gst_rate / 2
		instance.igst = 0
		instance.sgst = 0
	elif instance.sales.State == 'Daman and Diu':
		instance.cgst = instance.gst_rate / 2
		instance.ugst = instance.gst_rate / 2
		instance.igst = 0
		instance.sgst = 0
	elif instance.sales.State == 'Lakshadweep':
		instance.cgst = instance.gst_rate / 2
		instance.ugst = instance.gst_rate / 2
		instance.igst = 0
		instance.sgst = 0
	else:
		instance.cgst = 0
		instance.igst = instance.gst_rate 
		instance.ugst = 0
		instance.sgst = 0

@receiver(pre_save, sender=Sales_total)
def update_amount_account(sender, instance, *args, **kwargs):
	instance.Total = instance.rate * instance.Quantity * (1 - (instance.Disc/100))


@receiver(pre_save, sender=Sales_total)
def update_gst_rate_saletotal_account(sender, instance, *args, **kwargs):
	if instance.sales.State == instance.sales.Company.State:
		instance.cgst_total = instance.cgst * instance.Total / 100
		instance.gst_total 	= instance.sgst * instance.Total / 100

	elif instance.sales.State == 'Delhi':
		instance.cgst_total = instance.cgst * instance.Total / 100
		instance.gst_total 	= instance.sgst * instance.Total / 100

	elif instance.sales.State == 'Puducherry':
		instance.cgst_total = instance.cgst * instance.Total / 100
		instance.gst_total 	= instance.sgst * instance.Total / 100

	elif instance.sales.State == 'Andaman & Nicobar Islands':
		instance.cgst_total = instance.cgst * instance.Total / 100
		instance.gst_total = instance.ugst * instance.Total / 100

	elif instance.sales.State == 'Chandigarh':
		instance.cgst_total = instance.cgst * instance.Total / 100
		instance.gst_total = instance.ugst * instance.Total / 100

	elif instance.sales.State == 'Dadra and Nagar Haveli':
		instance.cgst_total = instance.cgst * instance.Total / 100
		instance.gst_total = instance.ugst * instance.Total / 100

	elif instance.sales.State == 'Daman and Diu':
		instance.cgst_total = instance.cgst * instance.Total / 100
		instance.gst_total = instance.ugst * instance.Total / 100

	elif instance.sales.State == 'Lakshadweep':
		instance.cgst_total = instance.cgst * instance.Total / 100
		instance.gst_total = instance.ugst * instance.Total / 100

	else:
		instance.gst_total = instance.igst * instance.Total / 100
	if instance.cgst_total == None:
		instance.grand_total = instance.Total + instance.gst_total 
	else:
		instance.grand_total = instance.Total + instance.cgst_total + instance.gst_total 
			
	
@receiver(pre_save, sender=Purchase_accounts)
def update_subtotal_account(sender,instance,*args,**kwargs):
	total = instance.purchasetotal_accounts.aggregate(the_sum=Coalesce(Sum('Total_p'), Value(0)))['the_sum']
	instance.sub_total = total

@receiver(pre_save, sender=Purchase_accounts)
def update_totalgst_account(sender,instance,*args,**kwargs):
	total_cgst = instance.purchasetotal_accounts.aggregate(the_sum=Coalesce(Sum('cgst_total'), Value(0)))['the_sum']
	total_gst = instance.purchasetotal_accounts.aggregate(the_sum=Coalesce(Sum('gst_total'), Value(0)))['the_sum']
	total 	= instance.purchasetotal_accounts.aggregate(the_sum=Coalesce(Sum('grand_total'), Value(0)))['the_sum']
	instance.cgst_alltotal = total_cgst
	instance.gst_alltotal = total_gst
	instance.Total = total

@receiver(pre_save, sender=Sales_accounts)
def update_total_sales_account(sender,instance,*args,**kwargs):
	total1 = instance.saletotal_accounts.aggregate(the_sum=Coalesce(Sum('Total'), Value(0)))['the_sum']
	instance.sub_total = total1

@receiver(pre_save, sender=Sales_accounts)
def update_totalgst_sales_account(sender,instance,*args,**kwargs):
	total_cgst = instance.saletotal_accounts.aggregate(the_sum=Coalesce(Sum('cgst_total'), Value(0)))['the_sum']
	total_gst = instance.saletotal_accounts.aggregate(the_sum=Coalesce(Sum('gst_total'), Value(0)))['the_sum']
	total 	= instance.saletotal_accounts.aggregate(the_sum=Coalesce(Sum('grand_total'), Value(0)))['the_sum']
	instance.cgst_alltotal = total_cgst
	instance.gst_alltotal = total_gst
	instance.Total = total

@receiver(pre_save, sender=Purchase_accounts)
def user_created_account(sender,instance,*args,**kwargs):
	c = journal.objects.filter(User=instance.User, Company=instance.Company).count() + 1
	if instance.sub_total != None:
		journal.objects.update_or_create(
			User=instance.User,
			Company=instance.Company,
			By=instance.purchase,
			To=instance.Party_ac,
			voucher_id=instance.id,
			defaults={
				'counter' : c,
				'Date': instance.date,
				'voucher_type' : "Purchase",
				'Debit': instance.sub_total,
				'Credit': instance.sub_total}
			)

@receiver(pre_delete, sender=Purchase_accounts)
def delete_related_journal_account(sender, instance, **kwargs):
	journal.objects.filter(User=instance.User,Company=instance.Company,voucher_id=instance.id).delete()

@receiver(pre_save, sender=Purchase_accounts)
def user_created_plpurchase_account(sender,instance,*args,**kwargs):
	c = Pl_journal.objects.filter(User=instance.User, Company=instance.Company).count() + 1
	if instance.sub_total != None:
		Pl_journal.objects.update_or_create(
			User=instance.User,
			Company=instance.Company,
			By=ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='Profit & Loss A/c').first(),
			To=instance.purchase,
			voucher_id=instance.id,
			defaults={
				'counter' : c,
				'Date': instance.date,
				'voucher_type' : "Purchase",
				'Debit': instance.sub_total,
				'Credit': instance.sub_total,
				'tax_expense':True,
				'it_head': 'Profit_&_Gains_of_Business_and_Professions'}
			)

@receiver(pre_delete, sender=Purchase_accounts)
def delete_related_pljournal_account(sender, instance, **kwargs):
	Pl_journal.objects.filter(User=instance.User,Company=instance.Company,voucher_id=instance.id).delete()


@receiver(pre_save, sender=Purchase_accounts)
def user_created_purchase_cgst_account(sender,instance,*args,**kwargs):
	c = journal.objects.filter(User=instance.User, Company=instance.Company).count() + 1
	if instance.cgst_alltotal != None and instance.cgst_alltotal != 0:
		journal.objects.update_or_create(
			User=instance.User,
			Company=instance.Company,
			By=ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='CGST').first(),
			To=instance.Party_ac,
			voucher_id=instance.id,
			defaults={
				'counter' : c,
				'Date': instance.date,
				'voucher_type' : "Journal",
				'Debit': instance.cgst_alltotal,
				'Credit': instance.cgst_alltotal}
			)


@receiver(pre_save, sender=Purchase_accounts)
def user_created_purchase_stategst_account(sender,instance,*args,**kwargs):
	c = journal.objects.filter(User=instance.User, Company=instance.Company).count() + 1
	if instance.gst_alltotal != None and instance.State == instance.Company.State:
		journal.objects.update_or_create(
			User=instance.User,
			Company=instance.Company,
			By=ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='SGST').first(),
			To=instance.Party_ac,
			voucher_id=instance.id,
			defaults={
				'counter' : c,
				'Date': instance.date,
				'voucher_type' : "Journal",
				'Debit': instance.gst_alltotal,
				'Credit': instance.gst_alltotal}
			)
	elif instance.gst_alltotal != None and instance.State == 'Delhi':
		journal.objects.update_or_create(
			User=instance.User,
			Company=instance.Company,
			By=ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='SGST').first(),
			To=instance.Party_ac,
			voucher_id=instance.id,
			defaults={
				'counter' : c,
				'Date': instance.date,
				'voucher_type' : "Journal",
				'Debit': instance.gst_alltotal,
				'Credit': instance.gst_alltotal}
			)
	elif instance.gst_alltotal != None and instance.State == 'Puducherry':
		journal.objects.update_or_create(
			User=instance.User,
			Company=instance.Company,
			By=ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='SGST').first(),
			To=instance.Party_ac,
			voucher_id=instance.id,
			defaults={
				'counter' : c,
				'Date': instance.date,
				'voucher_type' : "Journal",
				'Debit': instance.gst_alltotal,
				'Credit': instance.gst_alltotal}
			)
	elif instance.gst_alltotal != None and instance.State == 'Andaman & Nicobar Islands':
		journal.objects.update_or_create(
			User=instance.User,
			Company=instance.Company,
			By=ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='UTGST').first(),
			To=instance.Party_ac,
			voucher_id=instance.id,
			defaults={
				'counter' : c,
				'Date': instance.date,
				'voucher_type' : "Journal",
				'Debit': instance.gst_alltotal,
				'Credit': instance.gst_alltotal}
			)
	elif instance.gst_alltotal != None and instance.State == 'Chandigarh':
		journal.objects.update_or_create(
			User=instance.User,
			Company=instance.Company,
			By=ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='UTGST').first(),
			To=instance.Party_ac,
			voucher_id=instance.id,
			defaults={
				'counter' : c,
				'Date': instance.date,
				'voucher_type' : "Journal",
				'Debit': instance.gst_alltotal,
				'Credit': instance.gst_alltotal}
			)
	elif instance.gst_alltotal != None and instance.State == 'Dadra and Nagar Haveli':
		journal.objects.update_or_create(
			User=instance.User,
			Company=instance.Company,
			By=ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='UTGST').first(),
			To=instance.Party_ac,
			voucher_id=instance.id,
			defaults={
				'counter' : c,
				'Date': instance.date,
				'voucher_type' : "Journal",
				'Debit': instance.gst_alltotal,
				'Credit': instance.gst_alltotal}
			)
	elif instance.gst_alltotal != None and instance.State == 'Daman and Diu':
		journal.objects.update_or_create(
			User=instance.User,
			Company=instance.Company,
			By=ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='UTGST').first(),
			To=instance.Party_ac,
			voucher_id=instance.id,
			defaults={
				'counter' : c,
				'Date': instance.date,
				'voucher_type' : "Journal",
				'Debit': instance.gst_alltotal,
				'Credit': instance.gst_alltotal}
			)
	elif instance.gst_alltotal != None and instance.State == 'Lakshadweep':
		journal.objects.update_or_create(
			User=instance.User,
			Company=instance.Company,
			By=ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='UTGST').first(),
			To=instance.Party_ac,
			voucher_id=instance.id,
			defaults={
				'counter' : c,
				'Date': instance.date,
				'voucher_type' : "Journal",
				'Debit': instance.gst_alltotal,
				'Credit': instance.gst_alltotal}
			)
	else:
		if instance.gst_alltotal != None:
			journal.objects.update_or_create(
			User=instance.User,
			Company=instance.Company,
			By=ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='IGST').first(),
			To=instance.Party_ac,
			voucher_id=instance.id,
			defaults={
				'counter' : c,
				'Date': instance.date,
				'voucher_type' : "Journal",
				'Debit': instance.gst_alltotal,
				'Credit': instance.gst_alltotal}
			)



@receiver(pre_save, sender=Sales_accounts)
def user_created_sales_account(sender,instance,*args,**kwargs):
	c = journal.objects.filter(User=instance.User, Company=instance.Company).count() + 1
	if instance.sub_total != None:
		journal.objects.update_or_create(
			User=instance.User,
			Company=instance.Company,
			By=instance.Party_ac,
			To=instance.sales,
			voucher_id=instance.id,
			defaults={
				'counter' : c,
				'Date': instance.date,
				'voucher_type' : "Sales",
				'Debit': instance.sub_total,
				'Credit': instance.sub_total}
			)

@receiver(pre_delete, sender=Sales_accounts)
def delete_related_journal_sales_account(sender, instance, **kwargs):
	journal.objects.filter(User=instance.User,Company=instance.Company,voucher_id=instance.id).delete()

@receiver(pre_save, sender=Sales_accounts)
def user_created_plsales_account(sender,instance,*args,**kwargs):
	c = Pl_journal.objects.filter(User=instance.User, Company=instance.Company).count() + 1
	if instance.sub_total != None:
		Pl_journal.objects.update_or_create(
			User=instance.User,
			Company=instance.Company,
			By=instance.sales,
			To=ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='Profit & Loss A/c').first(),
			voucher_id=instance.id,
			defaults={
				'counter' : c,
				'Date': instance.date,
				'voucher_type' : "Sales", 
				'Debit': instance.sub_total,
				'Credit': instance.sub_total}
			)

@receiver(pre_delete, sender=Sales_accounts)
def delete_related_pljournal_sales_account(sender, instance, **kwargs):
	Pl_journal.objects.filter(User=instance.User,Company=instance.Company,voucher_id=instance.id).delete()

@receiver(pre_save, sender=Sales_accounts)
def user_created_sales_cgst_account(sender,instance,*args,**kwargs):
	c = journal.objects.filter(User=instance.User, Company=instance.Company).count() + 1
	if instance.cgst_alltotal != None and instance.cgst_alltotal != 0:
		journal.objects.update_or_create(
			User=instance.User,
			Company=instance.Company,
			By=instance.Party_ac,
			To=ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='CGST').first(),
			voucher_id=instance.id,
			defaults={
				'counter' : c,
				'Date': instance.date,
				'voucher_id' : instance.id,
				'voucher_type' : "Journal", 
				'Debit': instance.cgst_alltotal,
				'Credit': instance.cgst_alltotal}
			)

@receiver(pre_save, sender=Sales_accounts)
def user_created_sales_stategst_account(sender,instance,*args,**kwargs):
	c = journal.objects.filter(User=instance.User, Company=instance.Company).count() + 1
	if instance.gst_alltotal != None and instance.State == instance.Company.State:
		journal.objects.update_or_create(
			User=instance.User,
			Company=instance.Company,
			Date=instance.date,
			By=instance.Party_ac,
			To=ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='SGST').first(),
			voucher_id=instance.id,
			defaults={
				'counter' : c,
				'Date': instance.date,
				'voucher_type' : "Journal", 
				'Debit': instance.gst_alltotal,
				'Credit': instance.gst_alltotal}
			)
	elif instance.gst_alltotal != None and instance.State == 'Delhi':
		journal.objects.update_or_create(
			User=instance.User,
			Company=instance.Company,
			Date=instance.date,
			By=instance.Party_ac,
			To=ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='SGST').first(),
			voucher_id=instance.id,
			defaults={
				'counter' : c,
				'Date': instance.date,
				'voucher_type' : "Journal", 
				'Debit': instance.gst_alltotal,
				'Credit': instance.gst_alltotal}
			)
	elif instance.gst_alltotal != None and instance.State == 'Puducherry':
		journal.objects.update_or_create(
			User=instance.User,
			Company=instance.Company,
			Date=instance.date,
			By=instance.Party_ac,
			To=ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='SGST').first(),
			voucher_id=instance.id,
			defaults={
				'counter' : c,
				'Date': instance.date,
				'voucher_type' : "Journal", 
				'Debit': instance.gst_alltotal,
				'Credit': instance.gst_alltotal}
			)	
	elif instance.gst_alltotal != None and instance.State == 'Andaman & Nicobar Islands':
		journal.objects.update_or_create(
			User=instance.User,
			Company=instance.Company,
			Date=instance.date,
			By=instance.Party_ac,
			To=ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='UTGST').first(),
			voucher_id=instance.id,
			defaults={
				'counter' : c,
				'Date': instance.date,
				'voucher_type' : "Journal", 
				'Debit': instance.gst_alltotal,
				'Credit': instance.gst_alltotal}
			)
	elif instance.gst_alltotal != None and instance.State == 'Chandigarh':
		journal.objects.update_or_create(
			User=instance.User,
			Company=instance.Company,
			Date=instance.date,
			By=instance.Party_ac,
			To=ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='UTGST').first(),
			voucher_id=instance.id,
			defaults={
				'counter' : c,
				'Date': instance.date,
				'voucher_type' : "Journal", 
				'Debit': instance.gst_alltotal,
				'Credit': instance.gst_alltotal}
			)
	elif instance.gst_alltotal != None and instance.State == 'Dadra and Nagar Haveli':
		journal.objects.update_or_create(
			User=instance.User,
			Company=instance.Company,
			Date=instance.date,
			By=instance.Party_ac,
			To=ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='UTGST').first(),
			voucher_id=instance.id,
			defaults={
				'counter' : c,
				'Date': instance.date,
				'voucher_type' : "Journal", 
				'Debit': instance.gst_alltotal,
				'Credit': instance.gst_alltotal}
			)
	elif instance.gst_alltotal != None and instance.State == 'Daman and Diu':
		journal.objects.update_or_create(
			User=instance.User,
			Company=instance.Company,
			Date=instance.date,
			By=instance.Party_ac,
			To=ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='UTGST').first(),
			voucher_id=instance.id,
			defaults={
				'counter' : c,
				'Date': instance.date,
				'voucher_type' : "Journal", 
				'Debit': instance.gst_alltotal,
				'Credit': instance.gst_alltotal}
			)
	elif instance.gst_alltotal != None and instance.State == 'Lakshadweep':
		journal.objects.update_or_create(
			User=instance.User,
			Company=instance.Company,
			Date=instance.date,
			By=instance.Party_ac,
			To=ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='UTGST').first(),
			voucher_id=instance.id,
			defaults={
				'counter' : c,
				'Date': instance.date,
				'voucher_type' : "Journal", 
				'Debit': instance.gst_alltotal,
				'Credit': instance.gst_alltotal}
			)
	else:
		if instance.gst_alltotal != None:
			journal.objects.update_or_create(
			User=instance.User,
			Company=instance.Company,
			Date=instance.date,
			By=instance.Party_ac,
			To=ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='IGST').first(),
			voucher_id=instance.id,
			defaults={
				'counter' : c,
				'Date': instance.date,
				'voucher_type' : "Journal", 
				'Debit': instance.gst_alltotal,
				'Credit': instance.gst_alltotal}
				)

####################################### signals for the app stockkeeping(provided here due to django multiple import issue) ##############################

@receiver(post_save, sender=Stockdata)
def user_created_stock_ledger(sender, instance, created, **kwargs):
	user_created_stock_ledger_task(instance.pk)
