from django.conf import settings
from django.db import models
import datetime
from userprofile.models import Product_activation
from django.db.models.signals import pre_save,post_save,post_delete,pre_delete
from django.dispatch import receiver
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from django.db.models.functions import Coalesce 
from django.db.models import Case, When, CharField, Value, Sum, F, ExpressionWrapper, Subquery, OuterRef, Count
from company.models import company
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime
import datetime
import string
import random
from functools import wraps
from django.utils import timezone
from django.db import transaction


class selectdatefield(models.Model):
	User       = models.OneToOneField(settings.AUTH_USER_MODEL,related_name="Users",on_delete=models.CASCADE,null=True,blank=True)
	Start_Date = models.DateField(default=timezone.now,blank=True, null=True)
	End_Date   = models.DateField(default=timezone.now,blank=True, null=True)

	def __str__(self):
		return str(self.Start_Date)

	def clean(self):
		if self.Start_Date > self.End_Date:
			raise ValidationError({'Start_Date':["Start Date Cannot Be Greater Than End Date"],'End_Date':["Start Date Cannot Be Greater Than End Date"]})

@receiver(pre_save, sender=Product_activation)
def daterange_autocreate(sender,instance,*args,**kwargs):
	if instance.product.id == 1 and instance.is_active == True:
		selectdatefield.objects.update_or_create(
					User=instance.User,
					defaults= {
					'Start_Date' : datetime.date((datetime.datetime.now().year),4,1),
					'End_Date' :datetime.date((datetime.datetime.now().year) + 1,3,31)
					}
				)		

@receiver(post_save, sender=selectdatefield)
def update_stockitems(sender, instance, created, **kwargs):
	for obj in instance.User.user_stock.all():
		obj.save()


@receiver(post_save, sender=selectdatefield)
def update_stockitems_closing(sender, instance, created, **kwargs):
	for obj in instance.User.user_closing.all():
		obj.save()

@receiver(post_save, sender=selectdatefield)
def update_ledger_date(sender, instance, created, **kwargs):
	for obj in instance.User.user_ledger.all():
		obj.save()

class group1(models.Model):
	counter = models.IntegerField(blank=True,null=True)
	urlhash = models.CharField(max_length=100, null=True, blank=True)
	User = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=True,blank=True)
	group_Name = models.CharField(max_length=32)
	Company = models.ForeignKey(company,on_delete=models.CASCADE,null=True,blank=True,related_name='Company_group')  		
	Master = models.ForeignKey("self",on_delete=models.CASCADE,related_name='master_group',null=True)

	Name1 = (
		('Assets','Assets'),
		('Expenses','Expenses'),
		('Income','Income'),
		('Liabilities','Liabilities'),
		('Not Applicable','Not Applicable'),
		)

	Nature_of_group1 = models.CharField(max_length=32,choices=Name1,default='Assets')

	Nature = (
		('Debit','Debit'),
		('Credit','Credit'),
		('Not Applicable','Not Applicable'),
		)

	balance_nature = models.CharField(max_length=32,choices=Nature,default='Debit',blank=False)
	Group_behaves_like_a_Sub_Group = models.BooleanField(default=False)
	Nett_Debit_or_Credit_Balances_for_Reporting = models.BooleanField(default=False)
	negative_opening = models.DecimalField(max_digits=10,default=0,decimal_places=2,null=True)
	positive_opening = models.DecimalField(max_digits=10,default=0,decimal_places=2,null=True)
	negative_closing = models.DecimalField(max_digits=10,default=0,decimal_places=2,null=True)
	positive_closing = models.DecimalField(max_digits=10,default=0,decimal_places=2,null=True)
	# Total_Debit = models.DecimalField(max_digits=10,decimal_places=2,null=True)
	# Total_Credit = models.DecimalField(max_digits=10,decimal_places=2,null=True)

	def __str__(self):
		return self.group_Name


	def get_absolute_url(self, **kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk1'])
		return reverse("accounting_double_entry:groupdetail", kwargs={'pk2':self.pk, 'pk1':company_details.pk})

	def save(self, **kwargs):
		super(group1, self).save()
		if not self.urlhash:
			if self.User.profile.user_type == 'Bussiness User':
				self.urlhash = 'BU'+ '-' + str(self.User.id) + '-'+ 'P' + '-' + '1' + '-'+ 'C' + str(self.Company.counter) + '-' + ('AG') + str(self.counter)
				group1.objects.filter(pk=self.pk).update(urlhash=self.urlhash)
			else:
				self.urlhash = 'PU'+ '-' + str(self.User.id) + '-'+ 'P' + '-' + '1' + '-'+ 'C' + str(self.Company.counter) + '-' + ('AG') + str(self.counter)
				group1.objects.filter(pk=self.pk).update(urlhash=self.urlhash)



@receiver(post_save, sender=company)
def create_default_groups1(sender, instance, created, **kwargs):
	if not group1.objects.filter(User=instance.User, Company=instance,group_Name='Primary').exists():
		c = group1.objects.filter(User=instance.User, Company=instance).count() + 1
		if created:
			group1.objects.create(counter=c,User=instance.User,Company=instance,group_Name='Primary',Nature_of_group1='Not Applicable',balance_nature='Not Applicable',Group_behaves_like_a_Sub_Group=False,Nett_Debit_or_Credit_Balances_for_Reporting=False)


@receiver(post_save, sender=company)
def create_default_groups2(sender, instance, created, **kwargs):
	c = group1.objects.filter(User=instance.User, Company=instance).count() + 1
	if not group1.objects.filter(counter=c,User=instance.User, Company=instance).exists():
		if created:
			group1.objects.create(counter=c,User=instance.User,Company=instance,group_Name='Branch/Divisions',Master=instance.Company_group.get(group_Name='Primary'),Nature_of_group1='Liabilities',balance_nature='Credit',Group_behaves_like_a_Sub_Group=False,Nett_Debit_or_Credit_Balances_for_Reporting=False)

@receiver(post_save, sender=company)
def create_default_groups3(sender, instance, created, **kwargs):
	c = group1.objects.filter(User=instance.User, Company=instance).count() + 1
	if not group1.objects.filter(counter=c,User=instance.User, Company=instance).exists():
		if created:
			group1.objects.create(counter=c,User=instance.User,Company=instance,group_Name='Capital A/c',Master=instance.Company_group.get(group_Name='Primary'),Nature_of_group1='Liabilities',balance_nature='Credit',Group_behaves_like_a_Sub_Group=False,Nett_Debit_or_Credit_Balances_for_Reporting=False)

@receiver(post_save, sender=company)
def create_default_groups4(sender, instance, created, **kwargs):
	c = group1.objects.filter(User=instance.User, Company=instance).count() + 1
	if not group1.objects.filter(counter=c,User=instance.User, Company=instance).exists():
		if created:
			group1.objects.create(counter=c,User=instance.User,Company=instance,group_Name='Current Assets',Master=instance.Company_group.get(group_Name='Primary'),Nature_of_group1='Assets',balance_nature='Debit',Group_behaves_like_a_Sub_Group=False,Nett_Debit_or_Credit_Balances_for_Reporting=False)


@receiver(post_save, sender=company)
def create_default_groups5(sender, instance, created, **kwargs):
	c = group1.objects.filter(User=instance.User, Company=instance).count() + 1
	if not group1.objects.filter(counter=c,User=instance.User, Company=instance).exists():
		if created:
			group1.objects.create(counter=c,User=instance.User,Company=instance,group_Name='Current Liabilities',Master=instance.Company_group.get(group_Name='Primary'),Nature_of_group1='Liabilities',balance_nature='Credit',Group_behaves_like_a_Sub_Group=False,Nett_Debit_or_Credit_Balances_for_Reporting=False)


@receiver(post_save, sender=company)
def create_default_groups6(sender, instance, created, **kwargs):
	c = group1.objects.filter(User=instance.User, Company=instance).count() + 1
	if not group1.objects.filter(counter=c,User=instance.User, Company=instance).exists():
		if created:
			group1.objects.create(counter=c,User=instance.User,Company=instance,group_Name='Direct Expenses',Master=instance.Company_group.get(group_Name='Primary'),Nature_of_group1='Expenses',balance_nature='Debit',Group_behaves_like_a_Sub_Group=False,Nett_Debit_or_Credit_Balances_for_Reporting=False)


@receiver(post_save, sender=company)
def create_default_groups7(sender, instance, created, **kwargs):
	c = group1.objects.filter(User=instance.User, Company=instance).count() + 1
	if not group1.objects.filter(counter=c,User=instance.User, Company=instance).exists():
		if created:
			group1.objects.create(counter=c,User=instance.User,Company=instance,group_Name='Direct Incomes',Master=instance.Company_group.get(group_Name='Primary'),Nature_of_group1='Income',balance_nature='Credit',Group_behaves_like_a_Sub_Group=False,Nett_Debit_or_Credit_Balances_for_Reporting=False)


@receiver(post_save, sender=company)
def create_default_groups8(sender, instance, created, **kwargs):
	c = group1.objects.filter(User=instance.User, Company=instance).count() + 1
	if not group1.objects.filter(counter=c,User=instance.User, Company=instance).exists():
		if created:
			group1.objects.create(counter=c,User=instance.User,Company=instance,group_Name='Fixed Assets',Master=instance.Company_group.get(group_Name='Primary'),Nature_of_group1='Assets',balance_nature='Debit',Group_behaves_like_a_Sub_Group=False,Nett_Debit_or_Credit_Balances_for_Reporting=False)

@receiver(post_save, sender=company)
def create_default_groups9(sender, instance, created, **kwargs):
	c = group1.objects.filter(User=instance.User, Company=instance).count() + 1
	if not group1.objects.filter(counter=c,User=instance.User, Company=instance).exists():
		if created:
			group1.objects.create(counter=c,User=instance.User,Company=instance,group_Name='Indirect Income',Master=instance.Company_group.get(group_Name='Primary'),Nature_of_group1='Income',balance_nature='Credit',Group_behaves_like_a_Sub_Group=False,Nett_Debit_or_Credit_Balances_for_Reporting=True)

@receiver(post_save, sender=company)
def create_default_groups10(sender, instance, created, **kwargs):
	c = group1.objects.filter(User=instance.User, Company=instance).count() + 1
	if not group1.objects.filter(counter=c,User=instance.User, Company=instance).exists():
		if created:
			group1.objects.create(counter=c,User=instance.User,Company=instance,group_Name='Indirect Expense',Master=instance.Company_group.get(group_Name='Primary'),Nature_of_group1='Expenses',balance_nature='Debit',Group_behaves_like_a_Sub_Group=False,Nett_Debit_or_Credit_Balances_for_Reporting=True)


@receiver(post_save, sender=company)
def create_default_groups11(sender, instance, created, **kwargs):
	c = group1.objects.filter(User=instance.User, Company=instance).count() + 1
	if not group1.objects.filter(counter=c,User=instance.User, Company=instance).exists():
		if created:
			group1.objects.create(counter=c,User=instance.User,Company=instance,group_Name='Investments',Master=instance.Company_group.get(group_Name='Primary'),Nature_of_group1='Assets',balance_nature='Debit',Group_behaves_like_a_Sub_Group=False,Nett_Debit_or_Credit_Balances_for_Reporting=False)

@receiver(post_save, sender=company)
def create_default_groups12(sender, instance, created, **kwargs):
	c = group1.objects.filter(User=instance.User, Company=instance).count() + 1
	if not group1.objects.filter(counter=c,User=instance.User, Company=instance).exists():	
		if created:
			group1.objects.create(counter=c,User=instance.User,Company=instance,group_Name='Loans (Liability)',Master=instance.Company_group.get(group_Name='Primary'),Nature_of_group1='Liabilities',balance_nature='Credit',Group_behaves_like_a_Sub_Group=False,Nett_Debit_or_Credit_Balances_for_Reporting=False)

@receiver(post_save, sender=company)
def create_default_groups13(sender, instance, created, **kwargs):
	c = group1.objects.filter(User=instance.User, Company=instance).count() + 1
	if not group1.objects.filter(counter=c,User=instance.User, Company=instance).exists():
		if created:
			group1.objects.create(counter=c,User=instance.User,Company=instance,group_Name='Misc Expenses (ASSET)',Master=instance.Company_group.get(group_Name='Primary'),Nature_of_group1='Assets',balance_nature='Debit',Group_behaves_like_a_Sub_Group=False,Nett_Debit_or_Credit_Balances_for_Reporting=False)


@receiver(post_save, sender=company)
def create_default_groups14(sender, instance, created, **kwargs):
	c = group1.objects.filter(User=instance.User, Company=instance).count() + 1
	if not group1.objects.filter(counter=c,User=instance.User, Company=instance).exists():
		if created:
			group1.objects.create(counter=c,User=instance.User,Company=instance,group_Name='Purchase Accounts',Master=instance.Company_group.get(group_Name='Primary'),Nature_of_group1='Expenses',balance_nature='Debit',Group_behaves_like_a_Sub_Group=False,Nett_Debit_or_Credit_Balances_for_Reporting=False)


@receiver(post_save, sender=company)
def create_default_groups15(sender, instance, created, **kwargs):
	c = group1.objects.filter(User=instance.User, Company=instance).count() + 1
	if not group1.objects.filter(counter=c,User=instance.User, Company=instance).exists():
		if created:
			group1.objects.create(counter=c,User=instance.User,Company=instance,group_Name='Sales Account',Master=instance.Company_group.get(group_Name='Primary'),Nature_of_group1='Income',balance_nature='Credit',Group_behaves_like_a_Sub_Group=False,Nett_Debit_or_Credit_Balances_for_Reporting=False)


@receiver(post_save, sender=company)
def create_default_groups16(sender, instance, created, **kwargs):
	c = group1.objects.filter(User=instance.User, Company=instance).count() + 1
	if not group1.objects.filter(counter=c,User=instance.User, Company=instance).exists():
		if created:
			group1.objects.create(counter=c,User=instance.User,Company=instance,group_Name='Suspense A/c',Master=instance.Company_group.get(group_Name='Primary'),Nature_of_group1='Liabilities',balance_nature='Credit',Group_behaves_like_a_Sub_Group=False,Nett_Debit_or_Credit_Balances_for_Reporting=False)


@receiver(post_save, sender=company)
def create_default_groups17(sender, instance, created, **kwargs):
	c = group1.objects.filter(User=instance.User, Company=instance).count() + 1
	if not group1.objects.filter(counter=c,User=instance.User, Company=instance).exists():
		if created:
			group1.objects.create(counter=c,User=instance.User,Company=instance,group_Name='Bank Accounts',Master=instance.Company_group.get(group_Name='Current Assets'),Nature_of_group1='Not Applicable',balance_nature='Debit',Group_behaves_like_a_Sub_Group=False,Nett_Debit_or_Credit_Balances_for_Reporting=False)


@receiver(post_save, sender=company)
def create_default_groups18(sender, instance, created, **kwargs):
	c = group1.objects.filter(User=instance.User, Company=instance).count() + 1
	if not group1.objects.filter(counter=c,User=instance.User, Company=instance).exists():
		if created:
			group1.objects.create(counter=c,User=instance.User,Company=instance,group_Name='Bank OD A/c',Master=instance.Company_group.get(group_Name='Loans (Liability)'),Nature_of_group1='Not Applicable',balance_nature='Credit',Group_behaves_like_a_Sub_Group=False,Nett_Debit_or_Credit_Balances_for_Reporting=False)


@receiver(post_save, sender=company)
def create_default_groups19(sender, instance, created, **kwargs):
	c = group1.objects.filter(User=instance.User, Company=instance).count() + 1
	if not group1.objects.filter(counter=c,User=instance.User, Company=instance).exists():
		if created:
			group1.objects.create(counter=c,User=instance.User,Company=instance,group_Name='Cash-in-hand',Master=instance.Company_group.get(group_Name='Current Assets'),Nature_of_group1='Not Applicable',balance_nature='Debit',Group_behaves_like_a_Sub_Group=False,Nett_Debit_or_Credit_Balances_for_Reporting=False),

@receiver(post_save, sender=company)
def create_default_groups20(sender, instance, created, **kwargs):
	c = group1.objects.filter(User=instance.User, Company=instance).count() + 1
	if not group1.objects.filter(counter=c,User=instance.User, Company=instance).exists():
		if created:
			group1.objects.create(counter=c,User=instance.User,Company=instance,group_Name='Deposits(Asset)',Master=instance.Company_group.get(group_Name='Current Assets'),Nature_of_group1='Not Applicable',balance_nature='Debit',Group_behaves_like_a_Sub_Group=False,Nett_Debit_or_Credit_Balances_for_Reporting=False),

@receiver(post_save, sender=company)
def create_default_groups21(sender, instance, created, **kwargs):
	c = group1.objects.filter(User=instance.User, Company=instance).count() + 1
	if not group1.objects.filter(counter=c,User=instance.User, Company=instance).exists():
		if created:
			group1.objects.create(counter=c,User=instance.User,Company=instance,group_Name='Duties & Taxes',Master=instance.Company_group.get(group_Name='Current Liabilities'),Nature_of_group1='Not Applicable',balance_nature='Credit',Group_behaves_like_a_Sub_Group=False,Nett_Debit_or_Credit_Balances_for_Reporting=False),

@receiver(post_save, sender=company)
def create_default_groups22(sender, instance, created, **kwargs):
	c = group1.objects.filter(User=instance.User, Company=instance).count() + 1
	if not group1.objects.filter(counter=c,User=instance.User, Company=instance).exists():
		if created:
			group1.objects.create(counter=c,User=instance.User,Company=instance,group_Name='Loans & Advances(Asset)',Master=instance.Company_group.get(group_Name='Current Assets'),Nature_of_group1='Not Applicable',balance_nature='Debit',Group_behaves_like_a_Sub_Group=False,Nett_Debit_or_Credit_Balances_for_Reporting=False)

@receiver(post_save, sender=company)
def create_default_groups23(sender, instance, created, **kwargs):
	c = group1.objects.filter(User=instance.User, Company=instance).count() + 1
	if not group1.objects.filter(counter=c,User=instance.User, Company=instance).exists():
		if created:
			group1.objects.create(counter=c,User=instance.User,Company=instance,group_Name='Provisions',Master=instance.Company_group.get(group_Name='Current Liabilities'),Nature_of_group1='Not Applicable',balance_nature='Credit',Group_behaves_like_a_Sub_Group=False,Nett_Debit_or_Credit_Balances_for_Reporting=False)


@receiver(post_save, sender=company)
def create_default_groups24(sender, instance, created, **kwargs):
	c = group1.objects.filter(User=instance.User, Company=instance).count() + 1
	if not group1.objects.filter(counter=c,User=instance.User, Company=instance).exists():
		if created:
			group1.objects.create(counter=c,User=instance.User,Company=instance,group_Name='Reserves & Surplus',Master=instance.Company_group.get(group_Name='Capital A/c'),Nature_of_group1='Not Applicable',balance_nature='Credit',Group_behaves_like_a_Sub_Group=False,Nett_Debit_or_Credit_Balances_for_Reporting=False)


@receiver(post_save, sender=company)
def create_default_groups25(sender, instance, created, **kwargs):
	c = group1.objects.filter(User=instance.User, Company=instance).count() + 1
	if not group1.objects.filter(counter=c,User=instance.User, Company=instance).exists():
		if created:
			group1.objects.create(counter=c,User=instance.User,Company=instance,group_Name='Secured Loans',Master=instance.Company_group.get(group_Name='Loans (Liability)'),Nature_of_group1='Not Applicable',balance_nature='Credit',Group_behaves_like_a_Sub_Group=False,Nett_Debit_or_Credit_Balances_for_Reporting=False)

@receiver(post_save, sender=company)
def create_default_groups26(sender, instance, created, **kwargs):
	c = group1.objects.filter(User=instance.User, Company=instance).count() + 1
	if not group1.objects.filter(counter=c,User=instance.User, Company=instance).exists():
		if created:
			group1.objects.create(counter=c,User=instance.User,Company=instance,group_Name='Stock-in-hand',Master=instance.Company_group.get(group_Name='Primary'),Nature_of_group1='Not Applicable',balance_nature='Debit',Group_behaves_like_a_Sub_Group=False,Nett_Debit_or_Credit_Balances_for_Reporting=False)

@receiver(post_save, sender=company)
def create_default_groups27(sender, instance, created, **kwargs):
	c = group1.objects.filter(User=instance.User, Company=instance).count() + 1
	if not group1.objects.filter(counter=c,User=instance.User, Company=instance).exists():
		if created:
			group1.objects.create(counter=c,User=instance.User,Company=instance,group_Name='Sundry Creditors',Master=instance.Company_group.get(group_Name='Current Liabilities'),Nature_of_group1='Not Applicable',balance_nature='Credit',Group_behaves_like_a_Sub_Group=False,Nett_Debit_or_Credit_Balances_for_Reporting=False)


@receiver(post_save, sender=company)
def create_default_groups28(sender, instance, created, **kwargs):
	c = group1.objects.filter(User=instance.User, Company=instance).count() + 1
	if not group1.objects.filter(counter=c,User=instance.User, Company=instance).exists():
		if created:
			group1.objects.create(counter=c,User=instance.User,Company=instance,group_Name='Sundry Debtors',Master=instance.Company_group.get(group_Name='Current Assets'),Nature_of_group1='Not Applicable',balance_nature='Debit',Group_behaves_like_a_Sub_Group=False,Nett_Debit_or_Credit_Balances_for_Reporting=False)


@receiver(post_save, sender=company)
def create_default_groups30(sender, instance, created, **kwargs):
	c = group1.objects.filter(User=instance.User, Company=instance).count() + 1
	if not group1.objects.filter(counter=c,User=instance.User, Company=instance).exists():
		if created:
			group1.objects.create(counter=c,User=instance.User,Company=instance,group_Name='Unsecured Loans',Master=instance.Company_group.get(group_Name='Loans (Liability)'),Nature_of_group1='Not Applicable',balance_nature='Credit',Group_behaves_like_a_Sub_Group=False,Nett_Debit_or_Credit_Balances_for_Reporting=False)

@receiver(post_save, sender=company)
def create_default_groups32(sender, instance, created, **kwargs):
	c = group1.objects.filter(User=instance.User, Company=instance).count() + 1
	if not group1.objects.filter(counter=c,User=instance.User, Company=instance).exists():
		if created:
			group1.objects.create(counter=c,User=instance.User,Company=instance,group_Name='GST',Master=instance.Company_group.get(group_Name='Current Liabilities'),Nature_of_group1='Not Applicable',balance_nature='Credit',Group_behaves_like_a_Sub_Group=False,Nett_Debit_or_Credit_Balances_for_Reporting=False)


class ledger1(models.Model):
	User 			= models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=True,blank=True,related_name='user_ledger')
	Company 		= models.ForeignKey(company,on_delete=models.CASCADE,null=True,blank=True,related_name='Companys')
	counter 		= models.IntegerField(blank=True,null=True)
	urlhash			= models.CharField(max_length=100, null=True, blank=True)
	name 			= models.CharField(max_length=32)
	group1_Name 	= models.ForeignKey(group1,on_delete=models.CASCADE,null=True,related_name='ledgergroups')
	Opening_Balance = models.DecimalField(default=0.00,max_digits=19,decimal_places=2,null=True)
	Balance_opening = models.DecimalField(default=0.00,max_digits=19,decimal_places=2,null=True)
	User_Name 		= models.CharField(max_length=100,blank=True)
	Address 		= models.TextField(blank=True)
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
	State 			= models.CharField(max_length=100,choices=State_Name,default='Choose',blank=True)
	Pin_Code 		= models.BigIntegerField(blank=True,null=True)
	PanIt_No 		= models.CharField(max_length=100,blank=True)
	GST_No 			= models.CharField(max_length=100,blank=True)
	Closing_balance = models.DecimalField(default=0.00,max_digits=10,decimal_places=2,blank=True)
	To_pl_debit 	= models.DecimalField(max_digits=10,default=0,decimal_places=2,null=True)
	To_pl_credit 	= models.DecimalField(max_digits=10,default=0,decimal_places=2,null=True)
	# Total_Debit 	= models.DecimalField(max_digits=10,decimal_places=2,null=True)
	# Total_Credit 	= models.DecimalField(max_digits=10,decimal_places=2,null=True)

	def __str__(self):
		return self.name

	class Meta:
		ordering = ['-id']

	def get_absolute_url(self, **kwargs):
		company_details = get_object_or_404(company, pk=kwargs['pk'])
		return reverse("accounting_double_entry:ledgerdetail", kwargs={'pk2':self.pk, 'pk1':company_details.pk})

	def save(self, **kwargs):
		super(ledger1, self).save()
		if not self.urlhash:
			if self.User.profile.user_type == 'Bussiness User':
				self.urlhash = 'BU'+ '-' + str(self.User.id) + '-'+ 'P' + '-' + '1' + '-'+ 'C' + str(self.Company.counter) + '-' + ('AL') + str(self.counter)
				ledger1.objects.filter(pk=self.pk).update(urlhash=self.urlhash)
			else:
				self.urlhash = 'PU'+ '-' + str(self.User.id) + '-'+ 'P' + '-' + '1' + '-'+ 'C' + str(self.Company.counter) + '-' + ('AL') + str(self.counter)
				ledger1.objects.filter(pk=self.pk).update(urlhash=self.urlhash)





@receiver(post_save, sender=company)
def create_default_ledger01(sender, instance, created, **kwargs):
	c = ledger1.objects.filter(User=instance.User, Company=instance).count() + 1
	if not ledger1.objects.filter(counter=c,User=instance.User, Company=instance).exists():
		if created:
			ledger1.objects.create(counter=c, User=instance.User,Company=instance,group1_Name=instance.Company_group.get(group_Name='Primary'),name='Cash',Opening_Balance=0)


@receiver(post_save, sender=company)
def create_default_ledger02(sender, instance, created, **kwargs):
	c = ledger1.objects.filter(User=instance.User, Company=instance).count() + 1
	if not ledger1.objects.filter(counter=c,User=instance.User, Company=instance).exists():
		if created:
			ledger1.objects.create(counter=c, User=instance.User,Company=instance,group1_Name=instance.Company_group.get(group_Name='Primary'),name='Profit & Loss A/c',Opening_Balance=0)


@receiver(post_save, sender=company)
def create_default_ledger03(sender, instance, created, **kwargs):
	c = ledger1.objects.filter(User=instance.User, Company=instance).count() + 1
	if not ledger1.objects.filter(counter=c,User=instance.User, Company=instance).exists():
		if created:
			ledger1.objects.create(counter=c, User=instance.User,Company=instance,group1_Name=instance.Company_group.get(group_Name='Stock-in-hand'),name='Stock A/c',Opening_Balance=0)


@receiver(post_save, sender=company)
def create_default_ledger04(sender, instance, created, **kwargs):
	c = ledger1.objects.filter(User=instance.User, Company=instance).count() + 1
	if not ledger1.objects.filter(counter=c,User=instance.User, Company=instance).exists():
		if created:
			ledger1.objects.create(counter=c, User=instance.User,Company=instance,group1_Name=instance.Company_group.get(group_Name='Purchase Accounts'),name='Purchase A/c(Interstate)',Opening_Balance=0)

@receiver(post_save, sender=company)
def create_default_ledger05(sender, instance, created, **kwargs):
	c = ledger1.objects.filter(User=instance.User, Company=instance).count() + 1
	if not ledger1.objects.filter(counter=c,User=instance.User, Company=instance).exists():
		if created:
			ledger1.objects.create(counter=c, User=instance.User,Company=instance,group1_Name=instance.Company_group.get(group_Name='Purchase Accounts'),name='Purchase A/c(Intrastate)',Opening_Balance=0)

@receiver(post_save, sender=company)
def create_default_ledger06(sender, instance, created, **kwargs):
	c = ledger1.objects.filter(User=instance.User, Company=instance).count() + 1
	if not ledger1.objects.filter(counter=c,User=instance.User, Company=instance).exists():
		if created:
			ledger1.objects.create(counter=c, User=instance.User,Company=instance,group1_Name=instance.Company_group.get(group_Name='Sales Account'),name='Sales A/c(Interstate)',Opening_Balance=0)


@receiver(post_save, sender=company)
def create_default_ledger07(sender, instance, created, **kwargs):
	c = ledger1.objects.filter(User=instance.User, Company=instance).count() + 1
	if not ledger1.objects.filter(counter=c,User=instance.User, Company=instance).exists():
		if created:
			ledger1.objects.create(counter=c, User=instance.User,Company=instance,group1_Name=instance.Company_group.get(group_Name='Sales Account'),name='Sales A/c(Intrastate)',Opening_Balance=0)	


@receiver(post_save, sender=company)
def create_default_ledger08(sender, instance, created, **kwargs):
	c = ledger1.objects.filter(User=instance.User, Company=instance).count() + 1
	if not ledger1.objects.filter(counter=c,User=instance.User, Company=instance).exists():
		if created:
			ledger1.objects.create(counter=c, User=instance.User,Company=instance,group1_Name=instance.Company_group.get(group_Name='GST'),name='CGST',Opening_Balance=0)

@receiver(post_save, sender=company)
def create_default_ledger09(sender, instance, created, **kwargs):
	c = ledger1.objects.filter(User=instance.User, Company=instance).count() + 1
	if not ledger1.objects.filter(counter=c,User=instance.User, Company=instance).exists():
		if created:
			ledger1.objects.create(counter=c, User=instance.User,Company=instance,group1_Name=instance.Company_group.get(group_Name='GST'),name='SGST',Opening_Balance=0)

@receiver(post_save, sender=company)
def create_default_ledger10(sender, instance, created, **kwargs):
	c = ledger1.objects.filter(User=instance.User, Company=instance).count() + 1
	if not ledger1.objects.filter(counter=c,User=instance.User, Company=instance).exists():
		if created:
			ledger1.objects.create(counter=c, User=instance.User,Company=instance,group1_Name=instance.Company_group.get(group_Name='GST'),name='IGST',Opening_Balance=0)

@receiver(post_save, sender=company)
def create_default_ledger11(sender, instance, created, **kwargs):
	c = ledger1.objects.filter(User=instance.User, Company=instance).count() + 1
	if not ledger1.objects.filter(counter=c,User=instance.User, Company=instance).exists():
		if created:
			ledger1.objects.create(counter=c, User=instance.User,Company=instance,group1_Name=instance.Company_group.get(group_Name='GST'),name='UTGST',Opening_Balance=0)

@receiver(post_save, sender=company)
def create_default_ledger12(sender, instance, created, **kwargs):
	c = ledger1.objects.filter(User=instance.User, Company=instance).count() + 1
	if not ledger1.objects.filter(counter=c,User=instance.User, Company=instance).exists():
		if created:
			ledger1.objects.create(counter=c, User=instance.User,Company=instance,group1_Name=instance.Company_group.get(group_Name='Indirect Expense'),name='Tax',Opening_Balance=0)


@receiver(pre_save, sender=group1)
def total_closing_group1(sender,instance,*args,**kwargs):
	total_group_closing_deb_po = instance.master_group.filter(ledgergroups__Closing_balance__gte=0,balance_nature='Debit').aggregate(the_sum=Coalesce(Sum('ledgergroups__Closing_balance'), Value(0)))['the_sum']
	total_group_closing_deb_neg = instance.master_group.filter(ledgergroups__Closing_balance__lt=0,balance_nature='Debit').aggregate(the_sum=Coalesce(Sum('ledgergroups__Closing_balance'), Value(0)))['the_sum']
	total_group_closing_po_cre = instance.master_group.filter(ledgergroups__Closing_balance__gte=0,balance_nature='Credit').aggregate(the_sum=Coalesce(Sum('ledgergroups__Closing_balance'), Value(0)))['the_sum']
	total_group_closing_neg_cre = instance.master_group.filter(ledgergroups__Closing_balance__lt=0,balance_nature='Credit').aggregate(the_sum=Coalesce(Sum('ledgergroups__Closing_balance'), Value(0)))['the_sum']
	total_closing_deb_po = instance.ledgergroups.filter(Closing_balance__gte=0,group1_Name__balance_nature='Debit').aggregate(the_sum=Coalesce(Sum('Closing_balance'), Value(0)))['the_sum']
	total_closing_deb_ne = instance.ledgergroups.filter(Closing_balance__lt=0,group1_Name__balance_nature='Debit').aggregate(the_sum=Coalesce(Sum('Closing_balance'), Value(0)))['the_sum']
	total_closing_cre_po = instance.ledgergroups.filter(Closing_balance__gte=0,group1_Name__balance_nature='Credit').aggregate(the_sum=Coalesce(Sum('Closing_balance'), Value(0)))['the_sum']
	total_closing_cre_ne = instance.ledgergroups.filter(Closing_balance__lt=0,group1_Name__balance_nature='Credit').aggregate(the_sum=Coalesce(Sum('Closing_balance'), Value(0)))['the_sum']
	if total_group_closing_deb_po != None and total_group_closing_neg_cre != None and total_closing_deb_po != None and total_closing_cre_ne != None:
		instance.positive_closing = total_group_closing_deb_po + abs(total_group_closing_neg_cre) + total_closing_deb_po + abs(total_closing_cre_ne)
	if total_group_closing_po_cre != None and total_group_closing_deb_neg != None and total_closing_cre_po != None and total_closing_deb_ne != None:	
		instance.negative_closing = total_group_closing_po_cre + abs(total_group_closing_deb_neg) + total_closing_cre_po + abs(total_closing_deb_ne)


@receiver(pre_save, sender=group1)
def total_opening_group1(sender,instance,*args,**kwargs):
	total_group_opening_deb_po = instance.master_group.filter(ledgergroups__Balance_opening__gte=0,balance_nature='Debit').aggregate(the_sum=Coalesce(Sum('ledgergroups__Balance_opening'), Value(0)))['the_sum']
	total_group_opening_deb_ne = instance.master_group.filter(ledgergroups__Balance_opening__lt=0,balance_nature='Debit').aggregate(the_sum=Coalesce(Sum('ledgergroups__Balance_opening'), Value(0)))['the_sum']
	total_group_opening_cre_po = instance.master_group.filter(ledgergroups__Balance_opening__gte=0,balance_nature='Credit').aggregate(the_sum=Coalesce(Sum('ledgergroups__Balance_opening'), Value(0)))['the_sum']
	total_group_opening_cre_ne = instance.master_group.filter(ledgergroups__Balance_opening__lt=0,balance_nature='Credit').aggregate(the_sum=Coalesce(Sum('ledgergroups__Balance_opening'), Value(0)))['the_sum']
	total_opening_deb_po = instance.ledgergroups.filter(Balance_opening__gte=0,group1_Name__balance_nature='Debit').aggregate(the_sum=Coalesce(Sum('Balance_opening'), Value(0)))['the_sum']
	total_opening_deb_ne = instance.ledgergroups.filter(Balance_opening__lt=0,group1_Name__balance_nature='Debit').aggregate(the_sum=Coalesce(Sum('Balance_opening'), Value(0)))['the_sum']
	total_opening_cre_po = instance.ledgergroups.filter(Balance_opening__gte=0,group1_Name__balance_nature='Credit').aggregate(the_sum=Coalesce(Sum('Balance_opening'), Value(0)))['the_sum']
	total_opening_cre_ne = instance.ledgergroups.filter(Balance_opening__lt=0,group1_Name__balance_nature='Credit').aggregate(the_sum=Coalesce(Sum('Balance_opening'), Value(0)))['the_sum']
	if total_group_opening_deb_po != None and total_group_opening_cre_ne != None:	
		instance.positive_opening = total_group_opening_deb_po + total_group_opening_cre_ne + total_opening_deb_po + total_opening_cre_ne
	if total_group_opening_cre_po != None and total_group_opening_deb_ne != None:	
		instance.negative_opening = total_group_opening_cre_po + total_group_opening_deb_ne + total_opening_cre_po + total_opening_deb_ne





# @receiver(post_save, sender=ledger1)
# def update_groups_per_ledger_master(sender, instance, created, **kwargs):
# 	if instance.group1_Name.Master != None:
# 		instance.group1_Name.Master.save()	


class journal(models.Model):
	User       		= models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=True,blank=True,related_name='user_journal')
	Company    		= models.ForeignKey(company,on_delete=models.CASCADE,null=True,blank=True,related_name='Companyname')
	counter 		= models.IntegerField(blank=True,null=True)
	urlhash 		= models.CharField(max_length=100, null=True, blank=True)
	Date       		= models.DateField(default=datetime.date.today)
	voucher_id		= models.PositiveIntegerField(blank=True,null=True)
	voucher_type	= models.CharField(max_length=100,blank=True)
	By         		= models.ForeignKey(ledger1,on_delete=models.CASCADE,related_name='Debitledgers')
	To         		= models.ForeignKey(ledger1,on_delete=models.CASCADE,related_name='Creditledgers')
	Debit      		= models.DecimalField(max_digits=10,decimal_places=2,null=True)
	Credit     		= models.DecimalField(max_digits=10,decimal_places=2,null=True)
	narration  		= models.TextField(blank=True)


	def __str__(self):
		return str(self.By)

	def get_absolute_url(self):
		return reverse("accounting_double_entry:detail", kwargs={'pk':self.pk})

	def clean(self):
		if self.Debit != self.Credit:
			raise ValidationError('Debit Amount Should Be Equal To Credit Amount')
		elif self.To == self.By:
			raise ValidationError('Particular Entry Cannot be same')

	def save(self, **kwargs):
		self.voucher_type = 'Journal'
		super(journal, self).save()
		if not self.urlhash:
			if self.User.profile.user_type == 'Bussiness User':
				self.urlhash = 'BU'+ '-' + str(self.User.id) + '-'+ 'P' + '-' + '1' + '-'+ 'C' + str(self.Company.counter) + '-' + ('AJ') + str(self.counter)
				journal.objects.filter(pk=self.pk).update(urlhash=self.urlhash)
			else:
				self.urlhash = 'PU'+ '-' + str(self.User.id) + '-'+ 'P' + '-' + '1' + '-'+ 'C' + str(self.Company.counter) + '-' + ('AJ') + str(self.counter)
				journal.objects.filter(pk=self.pk).update(urlhash=self.urlhash)



class Pl_journal(models.Model):
	User       		= models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=True,blank=True)
	Company    		= models.ForeignKey(company,on_delete=models.CASCADE,null=True,blank=True,related_name='Companynamepl')
	counter 		= models.IntegerField(blank=True,null=True)
	urlhash 		= models.CharField(max_length=100, null=True, blank=True)
	Date       		= models.DateField(default=datetime.date.today)
	voucher_id		= models.PositiveIntegerField(blank=True,null=True)
	voucher_type	= models.CharField(max_length=100,blank=True)
	stock 			= models.CharField(max_length=100, null=True, blank=True)
	By         		= models.ForeignKey(ledger1,on_delete=models.CASCADE,related_name='Debitledgerspl',null=True)
	To         		= models.ForeignKey(ledger1,on_delete=models.CASCADE,related_name='Creditledgerspl',null=True)
	Debit      		= models.DecimalField(max_digits=10,decimal_places=2,null=True)
	Credit     		= models.DecimalField(max_digits=10,decimal_places=2,null=True)
	tax_expense		= models.BooleanField(default=True)
	it 				= (
			('Salaries','Salaries'),
			('Income_from_house_property','Income_from_house_property'),
			('Profit_&_Gains_of_Business_and_Professions','Profit_&_Gains_of_Business_and_Professions'),
			('Capital_Gains','Capital_Gains'),
			('Income_from_other_sources','Income_from_other_sources'),
			)
	it_head			= models.CharField(max_length=32,choices=it,default='Profit_&_Gains_of_Business_and_Professions',blank=False)

	def __str__(self):
		return str(self.By)

	def clean(self):
		if self.Debit != self.Credit:
			raise ValidationError('Debit Amount Should Be Equal To Credit Amount')
		elif self.To == self.By:
			raise ValidationError('Particular Entry Cannot be same')

	def save(self, **kwargs):
		super(Pl_journal, self).save()
		if not self.urlhash:
			if self.User.profile.user_type == 'Bussiness User':
				self.urlhash = 'BU'+ '-' + str(self.User.id) + '-'+ 'P' + '-' + '1' + '-'+ 'C' + str(self.Company.counter) + '-' + ('AJ') + str(self.counter)
				Pl_journal.objects.filter(pk=self.pk).update(urlhash=self.urlhash)
			else:
				self.urlhash = 'PU'+ '-' + str(self.User.id) + '-'+ 'P' + '-' + '1' + '-'+ 'C' + str(self.Company.counter) + '-' + ('AJ') + str(self.counter)
				Pl_journal.objects.filter(pk=self.pk).update(urlhash=self.urlhash)

@receiver(pre_save, sender=journal)
def create_pl_indirectexp(sender,instance,*args,**kwargs):
	c = Pl_journal.objects.filter(User=instance.User, Company=instance.Company).count() + 1
	if instance.Debit != None and  instance.Credit != None:
		if instance.By.group1_Name.group_Name == 'Indirect Expense':
			Pl_journal.objects.update_or_create(
				By   = ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='Profit & Loss A/c').first(),
				voucher_id=instance.id,
				defaults={
					'User' : instance.User,
					'Company' : instance.Company,
					'counter' : c,
					'Date' : instance.Date,
					'To'   : instance.By,
					'voucher_type' : "Journal",
					'Debit' : instance.Debit,
					'Credit' : instance.Credit,
					'tax_expense' : True,
					'it_head' : 'Profit_&_Gains_of_Business_and_Professions'
				}
			)
		if instance.To.group1_Name.group_Name == 'Indirect Expense':
			Pl_journal.objects.update_or_create(
				To   = ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='Profit & Loss A/c').first(),
				voucher_id=instance.id,
				defaults={
					'User' : instance.User,
					'Company' : instance.Company,
					'counter' : c,
					'Date' : instance.Date,
					'By' : instance.To,
					'voucher_type' : "Journal",
					'Debit' : instance.Debit,
					'Credit' : instance.Credit,
					'tax_expense' : True,
					'it_head' : 'Profit_&_Gains_of_Business_and_Professions'
				}
			)


@receiver(pre_save, sender=journal)
def create_pl_purchase(sender,instance,*args,**kwargs):
	c = Pl_journal.objects.filter(User=instance.User, Company=instance.Company).count() + 1
	if instance.Debit != None and  instance.Credit != None:
		if instance.To.group1_Name.group_Name == 'Purchase Accounts':
			Pl_journal.objects.update_or_create(counter=c,
				User=instance.User,
				Company=instance.Company,
				voucher_id=instance.id,
				By=ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='Profit & Loss A/c').first(),
				defaults={
					'Date' : instance.Date,
					'To'   : instance.To,
					'voucher_type' : "Journal",
					'Debit' : instance.Debit,
					'Credit' : instance.Credit,
					'tax_expense' : True,
					'it_head' : 'Profit_&_Gains_of_Business_and_Professions'
				}
			)

@receiver(pre_save, sender=journal)
def create_pl_directexp(sender,instance,*args,**kwargs):
	c = Pl_journal.objects.filter(User=instance.User, Company=instance.Company).count() + 1
	if instance.Debit != None and  instance.Credit != None:
		if instance.By.group1_Name.group_Name == 'Direct Expenses':
			Pl_journal.objects.update_or_create(counter=c,
				User=instance.User,
				Company=instance.Company,
				voucher_id=instance.id,
				By=ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='Profit & Loss A/c').first(),
				defaults={
					'Date' : instance.Date,
					'To'   : instance.By,
					'voucher_type' : "Journal",
					'Debit' : instance.Debit,
					'Credit' : instance.Credit,
					'tax_expense' : True,
					'it_head' : 'Profit_&_Gains_of_Business_and_Professions'
				}
			)

@receiver(pre_save, sender=journal)
def create_pl_sales(sender,instance,*args,**kwargs):
	c = Pl_journal.objects.filter(User=instance.User, Company=instance.Company).count() + 1
	if instance.Debit != None and  instance.Credit != None:
		if instance.By.group1_Name.group_Name == 'Sales Account':
			Pl_journal.objects.update_or_create(counter=c,
				User=instance.User,
				Company=instance.Company,
				voucher_id=instance.id,
				To=ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='Profit & Loss A/c').first(),
				defaults={
					'Date' : instance.Date,
					'voucher_type' : "Journal",
					'By' : instance.By,
					'Debit' : instance.Debit,
					'Credit' : instance.Credit,
					'tax_expense' : True,
					'it_head' : 'Profit_&_Gains_of_Business_and_Professions'  
				}
			)


@receiver(pre_save, sender=journal)
def create_pl_directinc(sender,instance,*args,**kwargs):
	c = Pl_journal.objects.filter(User=instance.User, Company=instance.Company).count() + 1
	if instance.Debit != None and  instance.Credit != None:
		if instance.To.group1_Name.group_Name == 'Direct Incomes':
			Pl_journal.objects.update_or_create(counter=c,
				User=instance.User,
				Company=instance.Company,
				voucher_id=instance.id,
				To=ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='Profit & Loss A/c').first(),
				defaults={
					'Date' : instance.Date,
					'voucher_type' : "Journal",
					'By' : instance.To,
					'Debit' : instance.Debit,
					'Credit' : instance.Credit,
					'tax_expense' : True,
					'it_head' : 'Profit_&_Gains_of_Business_and_Professions'  
				}
			)

@receiver(pre_save, sender=journal)
def create_pl_indirectinc(sender,instance,*args,**kwargs):
	c = Pl_journal.objects.filter(User=instance.User, Company=instance.Company).count() + 1
	if instance.Debit != None and  instance.Credit != None:
		if instance.To.group1_Name.group_Name == 'Indirect Income':
			Pl_journal.objects.update_or_create(counter=c,
				User=instance.User,
				Company=instance.Company,
				voucher_id=instance.id,
				To=ledger1.objects.filter(User=instance.User,Company=instance.Company,name__icontains='Profit & Loss A/c').first(),
				defaults={
					'Date' : instance.Date,
					'voucher_type' : "Journal",
					'By' : instance.To,
					'Debit' : instance.Debit,
					'Credit' : instance.Credit,
					'tax_expense' : True,
					'it_head' : 'Profit_&_Gains_of_Business_and_Professions'  
				}
			)

@receiver(pre_delete, sender=journal)
def delete_related_pljournal02(sender, instance, **kwargs):
	Pl_journal.objects.filter(Company=instance.Company,voucher_id=instance.id).delete()

# @receiver(pre_save, sender=ledger1)
# def total_debit_ledger(sender,instance,*args,**kwargs):
# 	total = instance.Debitledgers.aggregate(the_sum=Coalesce(Sum('Debit'), Value(0)))['the_sum']
# 	total_pl = instance.Debitledgerspl.aggregate(the_sum=Coalesce(Sum('Debit'), Value(0)))['the_sum']
# 	instance.Total_Debit = total + total_pl

# @receiver(pre_save, sender=ledger1)
# def total_credit_ledger(sender,instance,*args,**kwargs):
# 	total_2 = instance.Creditledgers.aggregate(the_sum=Coalesce(Sum('Credit'), Value(0)))['the_sum']
# 	total_2_pl = instance.Creditledgerspl.aggregate(the_sum=Coalesce(Sum('Credit'), Value(0)))['the_sum']
# 	instance.Total_Credit = total_2 + total_2_pl

# @receiver(pre_save, sender=group1)
# def total_debit_group(sender,instance,*args,**kwargs):
# 	total_3 = instance.ledgergroups.aggregate(the_sum=Coalesce(Sum('Total_Debit'), Value(0)))['the_sum']
# 	total_4 = instance.master_group.aggregate(the_sum=Coalesce(Sum('Total_Debit'), Value(0)))['the_sum']
# 	instance.Total_Debit = total_3 + total_4

# @receiver(pre_save, sender=group1)
# def total_credit_group(sender,instance,*args,**kwargs):
# 	total_5 = instance.ledgergroups.aggregate(the_sum=Coalesce(Sum('Total_Credit'), Value(0)))['the_sum']
# 	total_6 = instance.master_group.aggregate(the_sum=Coalesce(Sum('Total_Credit'), Value(0)))['the_sum']
# 	instance.Total_Credit = total_5 + total_6


@receiver(pre_save, sender=ledger1)
def total_topl_credit(sender,instance,*args,**kwargs):
	total_pl_3 = instance.Creditledgerspl.aggregate(the_sum=Coalesce(Sum('Credit'), Value(0)))['the_sum']
	if instance.group1_Name.group_Name == 'Purchase Accounts' or instance.group1_Name.group_Name == 'Indirect Expense' or instance.group1_Name.group_Name == 'Direct Expenses':
		if total_pl_3:
			instance.To_pl_debit = total_pl_3 + instance.Balance_opening
		else:
			instance.To_pl_debit = instance.Balance_opening
	else:
		instance.To_pl_debit = 0

@receiver(pre_save, sender=ledger1)
def total_topl_debit(sender,instance,*args,**kwargs):
	totalpl_4 = instance.Debitledgerspl.aggregate(the_sum=Coalesce(Sum('Debit'), Value(0)))['the_sum']
	if instance.group1_Name.group_Name == 'Sales Account' or instance.group1_Name.group_Name == 'Indirect Income' or instance.group1_Name.group_Name == 'Direct Incomes':
		if totalpl_4:
			instance.To_pl_credit = totalpl_4 + instance.Balance_opening
		else:
			instance.To_pl_credit = instance.Balance_opening
	else:
		instance.To_pl_credit = 0


@receiver(post_save, sender=journal)
def update_ledger_closing_by(sender, instance, created, **kwargs):
	instance.By.save()

@receiver(post_save, sender=journal)
def update_ledger_closing_to(sender, instance, created, **kwargs):
	instance.To.save()

@receiver(post_save, sender=Pl_journal)
def update_ledger_closingpl_by(sender, instance, created, **kwargs):
	instance.By.save()

@receiver(post_save, sender=Pl_journal)
def update_ledger_closingpl_to(sender, instance, created, **kwargs):
	instance.To.save()

@receiver(post_save, sender=ledger1)
def update_groups_per_ledger(sender, instance, created, **kwargs):
	gs = group1.objects.get(pk=instance.group1_Name.pk)
	gs.save()

@receiver(post_save, sender=group1)
def update_groups_per_master(sender, instance, created, **kwargs):
	if instance.Master != None:
		instance.Master.save()

@receiver(post_save, sender=group1)
def save_group_company(sender, instance, created, **kwargs):
	instance.Company.save()



# @receiver(post_save, sender=journal)
# def update_group_closing_by(sender, instance, created, **kwargs):
# 	instance.By.group1_Name.save()

# @receiver(post_save, sender=journal)
# def update_group_closing_by_master(sender, instance, created, **kwargs):
# 	if instance.By.group1_Name.Master != None:
# 		instance.By.group1_Name.Master.save()

# @receiver(post_save, sender=journal)
# def update_group_closing_to(sender, instance, created, **kwargs):
# 	instance.To.group1_Name.save()

# @receiver(post_save, sender=journal)
# def update_group_closing_to_master(sender, instance, created, **kwargs):
# 	if instance.To.group1_Name.Master != None:
# 		instance.To.group1_Name.Master.save()

# @receiver(post_save, sender=Pl_journal)
# def update_group_closingpl_by(sender, instance, created, **kwargs):
# 	instance.By.group1_Name.save()

# @receiver(post_save, sender=Pl_journal)
# def update_group_closingpl_by_master(sender, instance, created, **kwargs):
# 	if instance.By.group1_Name.Master != None:
# 		instance.By.group1_Name.Master.save()

# @receiver(post_save, sender=Pl_journal)
# def update_group_closingpl_to(sender, instance, created, **kwargs):
# 	instance.To.group1_Name.save()

# @receiver(post_save, sender=Pl_journal)
# def update_group_closingpl_to_master(sender, instance, created, **kwargs):
# 	if instance.To.group1_Name.Master != None:
# 		instance.To.group1_Name.Master.save()








class Bank_reconcilation(models.Model):
	User       			= models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=True,blank=True)
	Company    			= models.ForeignKey(company,on_delete=models.CASCADE,null=True,blank=True,related_name='Companynamebank')
	counter 			= models.IntegerField(blank=True,null=True)
	urlhash 			= models.CharField(max_length=100, null=True, blank=True)
	Date       			= models.DateField(default=datetime.date.today)
	voucher_id			= models.PositiveIntegerField(blank=True,null=True)
	voucher_type		= models.CharField(max_length=100,blank=True)
	By         			= models.ForeignKey(ledger1,on_delete=models.CASCADE,related_name='Debitledgersbank')
	To         			= models.ForeignKey(ledger1,on_delete=models.CASCADE,related_name='Creditledgersbank')
	Debit      			= models.DecimalField(max_digits=10,decimal_places=2,null=True)
	Credit     			= models.DecimalField(max_digits=10,decimal_places=2,null=True)
	category 			= (
				('ATM','ATM'),
				('Cash','Cash'),
				('Cheque/DD','Cheque/DD'),
				('Card','Card'),
				('ECS','ECS'),
				('Electronic Cheque','Electronic Cheque'),
				('Electronic DD/PO','Electronic DD/PO'),
				('e-Fund Transfer','e-Fund Transfer'),
				('Others','Others'),
				)
	transaction_type	= models.CharField(max_length=56,choices=category,default='ATM',blank=False)
	instrument_no 		= models.IntegerField(blank=True, default=0)
	bank_date			= models.DateField(blank=True, null=True)


	def __str__(self):
		return str(self.By)

	def clean(self):
		if self.Debit != self.Credit:
			raise ValidationError('Debit Amount Should Be Equal To Credit Amount')
		elif self.To == self.By:
			raise ValidationError('Particular Entry Cannot be same')

	def save(self, **kwargs):
		super(Bank_reconcilation, self).save()
		if not self.urlhash:
			if self.User.profile.user_type == 'Bussiness User':
				self.urlhash = 'BU'+ '-' + str(self.User.id) + '-'+ 'P' + '-' + '1' + '-'+ 'C' + str(self.Company.counter) + '-' + ('AJ') + str(self.counter)
				Bank_reconcilation.objects.filter(pk=self.pk).update(urlhash=self.urlhash)
			else:
				self.urlhash = 'PU'+ '-' + str(self.User.id) + '-'+ 'P' + '-' + '1' + '-'+ 'C' + str(self.Company.counter) + '-' + ('AJ') + str(self.counter)
				Bank_reconcilation.objects.filter(pk=self.pk).update(urlhash=self.urlhash)



@receiver(pre_save, sender=journal)
def create_bank_by(sender,instance,*args,**kwargs):
	c = Bank_reconcilation.objects.filter(User=instance.User, Company=instance.Company).count() + 1
	if instance.By.group1_Name.group_Name == 'Bank Accounts' and instance.voucher_type != 'Payment' and instance.voucher_type != 'Receipt' and instance.voucher_type != 'Contra':
		Bank_reconcilation.objects.update_or_create(counter=c,
								User=instance.User,
								Company=instance.Company,
								voucher_id=instance.id,
								defaults={
									'Date' 			: instance.Date,
									'voucher_type'	: "Journal",
									'By'			: instance.By,
									'To' 			: instance.To,
									'Debit' 		: instance.Debit,
									'Credit'		: instance.Credit
								}
							)

@receiver(pre_save, sender=journal)
def create_bank_to(sender,instance,*args,**kwargs):
	c = Bank_reconcilation.objects.filter(User=instance.User, Company=instance.Company).count() + 1
	if instance.To.group1_Name.group_Name == 'Bank Accounts' and instance.voucher_type != 'Payment' and instance.voucher_type != 'Receipt' and instance.voucher_type != 'Contra' :
		Bank_reconcilation.objects.update_or_create(counter=c,
								User=instance.User,
								Company=instance.Company,
								voucher_id=instance.id,
								defaults={
									'Date' 			: instance.Date,
									'voucher_type'	: "Journal",
									'By'			: instance.By,
									'To' 			: instance.To,
									'Debit' 		: instance.Debit,
									'Credit'		: instance.Credit
								}
							)
			



class Payment(models.Model):
	User       = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=True,blank=True)
	Company    = models.ForeignKey(company,on_delete=models.CASCADE,null=True,blank=True,related_name='Companynamepayment')
	counter    = models.IntegerField(blank=True,null=True)
	urlhash    = models.CharField(max_length=100, null=True, blank=True)
	date       = models.DateField(default=datetime.date.today)
	account    = models.ForeignKey(ledger1,on_delete=models.CASCADE,related_name='Payledgers')
	total_amt  = models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)

	def __str__(self):
		return str(self.account)

	def save(self, **kwargs):
		super(Payment, self).save()
		if not self.urlhash:
			if self.User.profile.user_type == 'Bussiness User':
				self.urlhash = 'BU'+ '-' + str(self.User.id) + '-'+ 'P' + '-' + '1' + '-'+ 'C' + str(self.Company.counter) + '-' + ('AJ') + str(self.counter)
				Payment.objects.filter(pk=self.pk).update(urlhash=self.urlhash)
			else:
				self.urlhash = 'PU'+ '-' + str(self.User.id) + '-'+ 'P' + '-' + '1' + '-'+ 'C' + str(self.Company.counter) + '-' + ('AJ') + str(self.counter)
				Payment.objects.filter(pk=self.pk).update(urlhash=self.urlhash)


class Particularspayment(models.Model):
	Company    = models.ForeignKey(company,on_delete=models.CASCADE,null=True,blank=True)
	payment    = models.ForeignKey(Payment,on_delete=models.CASCADE,related_name='payments')
	particular = models.ForeignKey(ledger1,on_delete=models.CASCADE,related_name='particularpayment')
	amount     = models.DecimalField(max_digits=10,decimal_places=2,null=True)

	def __str__(self):
		return str(self.payment)

class Receipt(models.Model):
	User       = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=True,blank=True)
	Company    = models.ForeignKey(company,on_delete=models.CASCADE,null=True,blank=True,related_name='Companynamereceipt')
	counter    = models.IntegerField(blank=True,null=True)
	urlhash    = models.CharField(max_length=100, null=True, blank=True)
	date       = models.DateField(default=datetime.date.today)
	account    = models.ForeignKey(ledger1,on_delete=models.CASCADE,related_name='receiptledgers')
	total_amt  = models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)

	def __str__(self):
		return str(self.account)

	def save(self, **kwargs):
		super(Receipt, self).save()
		if not self.urlhash:
			if self.User.profile.user_type == 'Bussiness User':
				self.urlhash = 'BU'+ '-' + str(self.User.id) + '-'+ 'P' + '-' + '1' + '-'+ 'C' + str(self.Company.counter) + '-' + ('AJ') + str(self.counter)
				Receipt.objects.filter(pk=self.pk).update(urlhash=self.urlhash)
			else:
				self.urlhash = 'PU'+ '-' + str(self.User.id) + '-'+ 'P' + '-' + '1' + '-'+ 'C' + str(self.Company.counter) + '-' + ('AJ') + str(self.counter)
				Receipt.objects.filter(pk=self.pk).update(urlhash=self.urlhash)


class Particularsreceipt(models.Model):
	Company    = models.ForeignKey(company,on_delete=models.CASCADE,null=True,blank=True)
	receipt    = models.ForeignKey(Receipt,on_delete=models.CASCADE,related_name='receipts')
	particular = models.ForeignKey(ledger1,on_delete=models.CASCADE,related_name='particularreceipt')
	amount     = models.DecimalField(max_digits=10,decimal_places=2,null=True)

	def __str__(self):
		return str(self.receipt)


class Contra(models.Model):
	User       = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=True,blank=True)
	Company    = models.ForeignKey(company,on_delete=models.CASCADE,null=True,blank=True,related_name='Companynamecontra')
	counter    = models.IntegerField(blank=True,null=True)
	urlhash	   = models.CharField(max_length=100, null=True, blank=True)
	date       = models.DateField(default=datetime.date.today)
	account    = models.ForeignKey(ledger1,on_delete=models.CASCADE,related_name='contraledgers')
	total_amt  = models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)

	def __str__(self):
		return str(self.account)

	def save(self, **kwargs):
		super(Contra, self).save()
		if not self.urlhash:
			if self.User.profile.user_type == 'Bussiness User':
				self.urlhash = 'BU'+ '-' + str(self.User.id) + '-'+ 'P' + '-' + '1' + '-'+ 'C' + str(self.Company.counter) + '-' + ('AJ') + str(self.counter)
				Contra.objects.filter(pk=self.pk).update(urlhash=self.urlhash)
			else:
				self.urlhash = 'PU'+ '-' + str(self.User.id) + '-'+ 'P' + '-' + '1' + '-'+ 'C' + str(self.Company.counter) + '-' + ('AJ') + str(self.counter)
				Contra.objects.filter(pk=self.pk).update(urlhash=self.urlhash)

class Particularscontra(models.Model):
	Company    = models.ForeignKey(company,on_delete=models.CASCADE,null=True,blank=True)
	contra     = models.ForeignKey(Contra,on_delete=models.CASCADE,related_name='contras')
	particular = models.ForeignKey(ledger1,on_delete=models.CASCADE,related_name='particularcontra')
	amount     = models.DecimalField(max_digits=10,decimal_places=2,null=True)

	def __str__(self):
		return str(self.contra)


@receiver(post_save, sender=Payment)
def update_ledger_closing_payment(sender, instance, created, **kwargs):
	for obj in instance.User.user_ledger.all():
		obj.save()

@receiver(post_save, sender=Receipt)
def update_ledger_closing_receipt(sender, instance, created, **kwargs):
	for obj in instance.User.user_ledger.all():
		obj.save()

@receiver(post_save, sender=Contra)
def update_ledger_closing_contra(sender, instance, created, **kwargs):
	for obj in instance.User.user_ledger.all():
		obj.save()

@receiver(pre_save, sender=Payment)
def update_total_payment(sender,instance,*args,**kwargs):
	total1 = instance.payments.aggregate(the_sum=Coalesce(Sum('amount'), Value(0)))['the_sum']
	instance.total_amt = total1


@receiver(pre_save, sender=Particularspayment)
def user_created_payment(sender,instance,*args,**kwargs):
	c = journal.objects.filter(User=instance.payment.User, Company=instance.payment.Company).count() + 1
	if instance.amount != None:
		journal.objects.update_or_create(counter=c,User=instance.payment.User,Company=instance.payment.Company,Date=instance.payment.date, voucher_id=instance.payment.id, voucher_type= "Payment",By=instance.particular,To=instance.payment.account,Debit=instance.amount,Credit=instance.amount)

@receiver(pre_save, sender=Particularspayment)
def create_payment_bank_(sender,instance,*args,**kwargs):
	c = Bank_reconcilation.objects.filter(User=instance.payment.User, Company=instance.payment.Company).count() + 1
	if instance.amount != None and instance.payment.account.group1_Name.group_Name == 'Bank Accounts':
		Bank_reconcilation.objects.update_or_create(counter=c,
								User=instance.payment.User,
								Company=instance.payment.Company,
								voucher_id=instance.payment.id,
								defaults={
									'Date' 			: instance.payment.date,
									'voucher_type'	: "Payment",
									'By'			: instance.particular,
									'To' 			: instance.payment.account,
									'Debit' 		: instance.amount,
									'Credit'		: instance.amount
								}
							)


@receiver(pre_save, sender=Receipt)
def update_total_receipt(sender,instance,*args,**kwargs):
	total1 = instance.receipts.aggregate(the_sum=Coalesce(Sum('amount'), Value(0)))['the_sum']
	instance.total_amt = total1


@receiver(pre_save, sender=Particularsreceipt)
def user_created_receipt(sender,instance,*args,**kwargs):
	c = journal.objects.filter(User=instance.receipt.User, Company=instance.receipt.Company).count() + 1
	if instance.amount != None:
		journal.objects.update_or_create(counter=c,User=instance.receipt.User,Company=instance.receipt.Company,Date=instance.receipt.date, voucher_id=instance.receipt.id, voucher_type= "Receipt",By=instance.receipt.account,To=instance.particular,Debit=instance.amount,Credit=instance.amount)


@receiver(pre_save, sender=Particularsreceipt)
def create_receipt_bank(sender,instance,*args,**kwargs):
	c = Bank_reconcilation.objects.filter(User=instance.receipt.User, Company=instance.receipt.Company).count() + 1
	if instance.amount != None and instance.receipt.account.group1_Name.group_Name == 'Bank Accounts':
		Bank_reconcilation.objects.update_or_create(counter=c,
								User=instance.receipt.User,
								Company=instance.receipt.Company,
								voucher_id=instance.receipt.id,
								defaults={
									'Date' 			: instance.receipt.date,
									'voucher_type'	: "Receipt",
									'By'			: instance.particular,
									'To' 			: instance.receipt.account,
									'Debit' 		: instance.amount,
									'Credit'		: instance.amount
								}
							)

@receiver(pre_save, sender=Contra)
def update_total_contra(sender,instance,*args,**kwargs):
	total1 = instance.contras.aggregate(the_sum=Coalesce(Sum('amount'), Value(0)))['the_sum']
	instance.total_amt = total1


@receiver(pre_save, sender=Particularscontra)
def user_created_contra(sender,instance,*args,**kwargs):
	c = journal.objects.filter(User=instance.contra.User, Company=instance.contra.Company).count() + 1
	if instance.amount != None:
		journal.objects.update_or_create(counter=c,User=instance.contra.User,Company=instance.contra.Company,Date=instance.contra.date, voucher_id=instance.contra.id, voucher_type= "Contra",By=instance.particular,To=instance.contra.account,Debit=instance.amount,Credit=instance.amount)

@receiver(pre_save, sender=Particularscontra)
def create_contra_to_bank_(sender,instance,*args,**kwargs):
	c = Bank_reconcilation.objects.filter(User=instance.contra.User, Company=instance.contra.Company).count() + 1
	if instance.amount != None and instance.contra.account.group1_Name.group_Name == 'Bank Accounts':
		Bank_reconcilation.objects.update_or_create(counter=c,
								User=instance.contra.User,
								Company=instance.contra.Company,
								voucher_id=instance.contra.id,
								defaults={
									'Date' 			: instance.contra.date,
									'voucher_type'	: "Contra",
									'By'			: instance.particular,
									'To' 			: instance.contra.account,
									'Debit' 		: instance.amount,
									'Credit'		: instance.amount
								}
							)

@receiver(pre_save, sender=Particularscontra)
def create_contra_by_bank_(sender,instance,*args,**kwargs):
	c = Bank_reconcilation.objects.filter(User=instance.contra.User, Company=instance.contra.Company).count() + 1
	if instance.amount != None and instance.particular.account.group1_Name.group_Name == 'Bank Accounts':
		Bank_reconcilation.objects.update_or_create(counter=c,
								User=instance.contra.User,
								Company=instance.contra.Company,
								voucher_id=instance.contra.id,
								defaults={
									'Date' 			: instance.contra.date,
									'voucher_type'	: "Contra",
									'By'			: instance.particular,
									'To' 			: instance.contra.account,
									'Debit' 		: instance.amount,
									'Credit'		: instance.amount
								}
							)

class Multijournaltotal(models.Model):
	User         = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=True,blank=True)
	Company      = models.ForeignKey(company,on_delete=models.CASCADE,null=True,blank=True,related_name='Companynamemultijournaltotal')
	Date         = models.DateField(default=datetime.date.today)
	Total_Debit  = models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)
	Total_Credit = models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)
	narration    = models.TextField(blank=True)

	def __str__(self):
		return str(self.Total_Debit)

	def clean(self):
		if self.Total_Debit != self.Total_Credit:
			raise ValidationError('Debit Amount Should Be Equal To Credit Amount')

	def get_absolute_url(self, **kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk1'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		return reverse("accounting_double_entry:multijournaldetail", kwargs={'pk2':self.pk, 'pk':company_details.pk, 'pk3':selectdatefield_details.pk })


class Multijournal(models.Model):
	Company      = models.ForeignKey(company,on_delete=models.CASCADE,null=True,blank=True)
	By           = models.ForeignKey(ledger1,on_delete=models.CASCADE,null=True,blank=True,related_name='Debitledgersmulti')
	To           = models.ForeignKey(ledger1,on_delete=models.CASCADE,null=True,blank=True,related_name='Creditledgersmulti')
	Debit        = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)	
	Credit       = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
	total 		 = models.ForeignKey(Multijournaltotal,on_delete=models.CASCADE,related_name='totals')	
	


	def __str__(self):
		return str(self.By)

	def get_absolute_url(self, **kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk1'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=pk3)
		return reverse("accounting_double_entry:multijournaldetail", kwargs={'pk2':self.pk, 'pk':company_details.pk, 'pk3':selectdatefield_details.pk })




@receiver(pre_save, sender=Multijournaltotal)
def update_total_journaldebit(sender,instance,*args,**kwargs):
	total_debit = instance.totals.aggregate(the_sum=Coalesce(Sum('Debit'), Value(0)))['the_sum']
	instance.Total_Debit = total_debit

@receiver(pre_save, sender=Multijournaltotal)
def update_total_journalcredit(sender,instance,*args,**kwargs):
	total_credit = instance.totals.aggregate(the_sum=Coalesce(Sum('Credit'), Value(0)))['the_sum']
	instance.Total_Credit = total_credit


@receiver(pre_save, sender=Multijournal)
def create_multijournal(sender,instance,*args,**kwargs):
	c = journal.objects.filter(User=instance.total.User, Company=instance.total.Company).count() + 1
	if instance.Debit != None and instance.Credit != None and instance.total.Total_Debit != None:
		debit_total = (instance.Debit * instance.Credit) / instance.total.Total_Debit
		credit_total = (instance.Debit * instance.Credit) / instance.total.Total_Debit
	else:
		debit_total = instance.Debit
		credit_total = instance.Credit
	if debit_total != None and credit_total != None:
		journal.objects.update_or_create(counter=c,
								User=instance.total.User,
								Company=instance.total.Company,
								voucher_id=instance.total.id,
								defaults={
									'Date' 			: instance.total.Date,
									'voucher_type'	: "Journal",
									'By'			: instance.By,
									'To' 			: instance.To,
									'Debit' 		: debit_total,
									'Credit'		: credit_total
								}
							)