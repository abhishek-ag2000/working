from django.shortcuts import render
from django.views.generic import (ListView,DetailView,
								  CreateView,UpdateView,DeleteView)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from accounting_double_entry.models import Pl_journal,journal,group1,ledger1,selectdatefield,Payment,Particularspayment,Receipt,Particularsreceipt,Contra,Particularscontra,Multijournal,Multijournaltotal,Bank_reconcilation
from stockkeeping.models import stock_journal,Stockgroup,Simpleunits,Compoundunits,Stockdata,Purchase,Sales,Stock_Total,Stock_Total_sales
from accounting_double_entry.forms import bank_journalForm,pl_journalForm,journalForm,group1Form,Ledgerform,DateRangeForm,PaymentForm,Payment_formSet,ParticularspaymentForm,ReceiptForm,ParticularsreceiptForm,Receipt_formSet,ContraForm,ParticularscontraForm,Contra_formSet,MultijournalForm,MultijournaltotalForm,Multijournal_formSet
from userprofile.models import Profile, Product_activation, Role_product_activation
from todogst.models import Todo
from company.models import company
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from messaging.models import Message 
import datetime
from django.db.models.functions import Coalesce 
from itertools import zip_longest
from django.db.models import Case, When, CharField, Value, Sum, F, Q, ExpressionWrapper, Subquery, OuterRef, Count
from django.db.models.fields import DecimalField
from ecommerce_integration.models import coupon, Product, Product_review, Services, API
import calendar
import dateutil
import collections   
from django.db import transaction  
from django.forms import inlineformset_factory
from django.http import JsonResponse
from django.template.loader import render_to_string
from ecommerce_integration.decorators import product_1_activation
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt
from .resources import journalResource,Pl_journalResource
from django.http import HttpResponse
from tablib import Dataset
import pandas as pd
import xlrd
from django.core.exceptions import ValidationError
from decimal import Decimal
import numpy as np

class ProductExistsRequiredMixin:

    def dispatch(self, request, *args, **kwargs):
        if Product_activation.objects.filter(User=self.request.user,product__id = 1, is_active=True) or Role_product_activation.objects.filter(User=request.user,product__id = 1, is_active=True):
            return super().dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

# Create your views here.

###################### Views For Exporting and Importing Data ############################################

def export_journal(request,pk,pk3):
	company_details = get_object_or_404(company, pk=pk)
	selectdatefield_details = get_object_or_404(selectdatefield, pk=pk3)
	journal_resource = journalResource()
	queryset = journal.objects.filter(Company= company_details.pk)
	dataset = journal_resource.export(queryset)
	# modification to find name of ledger and its group name in dataset final
	response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
	response['Content-Disposition'] = 'attachment; filename="journal.xls"'
	return response


def journal_upload(request,pk,pk3):
	company_details = get_object_or_404(company, pk=pk)
	selectdatefield_details = get_object_or_404(selectdatefield, pk=pk3)
	error_message = "Some of the ledgers and Groups doesnot match with the ledgers of your Company"
	form_error = False
	if request.method == 'POST':
		journal_resource = journalResource()
		dataset = Dataset()
		new_journal = request.FILES['myfile']

		
		
		data = pd.ExcelFile(new_journal)
		dfex = pd.read_excel(data,'Tablib Dataset')
		dfnew = dfex[['Date','By','By__group1_Name__group_Name','To','To__group1_Name__group_Name','Debit','Credit']]

		# dfdup = dfnew.drop_duplicates(subset=['To__group1_Name__group_Name'], keep='last')
		# dfdup = dfnew.drop_duplicates(subset=['To__name'], keep='last')
		# dfdup = dfnew.drop_duplicates(subset=['By__group1_Name__group_Name'], keep='last')
		# dfdup = dfnew.drop_duplicates(subset=['By__name'], keep='last')
		# print(dfnew)

		# x=[]
		# for i in range(0, len(dfnew)):
		# 	if ledger1.objects.filter(Company=company_details.pk,name__icontains=dfnew.iloc[i]['By'],group1_Name__group_Name__icontains=dfnew.iloc[i]['By__group1_Name__group_Name']).exists() and ledger1.objects.filter(Company=company_details.pk,name__icontains=dfnew.iloc[i]['To'],group1_Name__group_Name__icontains=dfnew.iloc[i]['To__group1_Name__group_Name']).exists():
		# 		x.append(str(dfnew.iloc[i]['By']))
		# 		x.append(str(dfnew.iloc[i]['To']))
		# 		x.append(str(dfnew.iloc[i]['By__group1_Name__group_Name']))
		# 		x.append(str(dfnew.iloc[i]['To__group1_Name__group_Name']))				
		# 	else:
		# 		pass
			

		# print(x[:4])
		
		for i in range(0, len(dfnew)):
			debit = Decimal(np.sum(dfnew.iloc[i]['Debit']).item())
			credit = Decimal(np.sum(dfnew.iloc[i]['Credit']).item())
			if ledger1.objects.filter(Company=company_details.pk,name__icontains=dfnew.iloc[i]['By'],group1_Name__group_Name__icontains=dfnew.iloc[i]['By__group1_Name__group_Name']).exists() and ledger1.objects.filter(Company=company_details.pk,name__icontains=dfnew.iloc[i]['To'],group1_Name__group_Name__icontains=dfnew.iloc[i]['To__group1_Name__group_Name']).exists():
				journal.objects.create(User=request.user,Company=company_details,Date=dfnew.iloc[i]['Date'],By=ledger1.objects.filter(name__icontains=dfnew.iloc[i]['By']).first(),To=ledger1.objects.filter(name__icontains=dfnew.iloc[i]['To']).first(),Debit=debit,Credit=credit)
			else:
				form_error = True


	inbox = Message.objects.filter(reciever=request.user)
	inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
	send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

	context = {
		'company_details' 			: company_details,
		'selectdatefield_details' 	: selectdatefield_details,
		'error_message'				: error_message,
		'inbox' 					: inbox,
		'form_error' 				: form_error,
		'inbox_count' 				: inbox_count,
		'send_count' 				: send_count,
		'Todos'						: Todo.objects.filter(User=request.user, complete=False),
		'Todos_total' 			  	: Todo.objects.filter(User=request.user, complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
	}

	return render(request, 'accounting_double_entry/import_journal.html',context)


###################### Views For Group Display ############################################

class groupsummaryListView(ProductExistsRequiredMixin,LoginRequiredMixin,ListView):
	model = group1
	paginate_by = 15

	def get_template_names(self):
		if True:  
			return ['Group_Summary/group_summary.html']
		else:
			return ['accounting_double_entry/group1_list.html']

	def get_queryset(self):
		return self.model.objects.filter(Company=self.kwargs['pk'])

	def get_context_data(self, **kwargs):
		context = super(groupsummaryListView, self).get_context_data(**kwargs) 
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		if company_details.gst_enabled == True:
			context['group1_list'] = group1.objects.filter(Company= company_details.pk).exclude(group_Name__icontains='Primary')
		else:
			context['group1_list'] = group1.objects.filter(Company= company_details.pk).exclude(Q(group_Name__icontains='GST') | Q(group_Name__icontains='Primary'))
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		return context



class group1ListView(ProductExistsRequiredMixin,LoginRequiredMixin,ListView):
	model = group1
	paginate_by = 15

	def get_queryset(self):
		return self.model.objects.filter(Company=self.kwargs['pk']).exclude(group_Name__icontains='Primary').order_by('id')

	def get_context_data(self, **kwargs):
		context = super(group1ListView, self).get_context_data(**kwargs) 
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		if company_details.gst_enabled == True:
			context['group1_list'] = group1.objects.filter(Company= company_details.pk).exclude(group_Name__icontains='Primary')
		else:
			context['group1_list'] = group1.objects.filter(Company= company_details.pk).exclude(Q(group_Name='GST') | Q(group_Name__icontains='Primary'))
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		return context


@login_required
@product_1_activation
def groupsummary_detail_view(request, pk, pk2, pk3):
	company_details = get_object_or_404(company, pk=pk)
	group1_details = get_object_or_404(group1, pk=pk2)
	selectdatefield_details = get_object_or_404(selectdatefield, pk=pk3)

	# purchases
	gs_purchase = group1.objects.filter(Company=company_details.pk,group_Name__icontains="Purchase Accounts")
	gs_purchase_total = gs_purchase.aggregate(the_sum=Coalesce(Sum('ledgergroups__To_pl_debit'), Value(0)))['the_sum']

	# sales
	gs_sales = group1.objects.filter(Company=company_details.pk,group_Name__icontains="Sales Account")
	gs_sales_total = gs_sales.aggregate(the_sum=Coalesce(Sum('ledgergroups__To_pl_credit'), Value(0)))['the_sum']

	# Direct Expense
	gs_directexp = group1.objects.filter(Company=company_details.pk,group_Name__icontains="Direct Expenses")
	gs_directexp_total = gs_directexp.aggregate(the_sum=Coalesce(Sum('ledgergroups__To_pl_debit'), Value(0)))['the_sum']

	# Direct Income
	gs_directinc = group1.objects.filter(Company=company_details.pk,group_Name__icontains="Direct Incomes")
	gs_directinc_total = gs_directinc.aggregate(the_sum=Coalesce(Sum('ledgergroups__To_pl_credit'), Value(0)))['the_sum']

	# Indirect Expense
	gs_indirectexp = group1.objects.filter(Company=company_details.pk,group_Name__icontains="Indirect Expense")
	gs_indirectexp_total = gs_indirectexp.aggregate(the_sum=Coalesce(Sum('ledgergroups__To_pl_debit'), Value(0)))['the_sum']

	# Indirect Income
	gs_indirectinc = group1.objects.filter(Company=company_details.pk,group_Name__icontains="Indirect Income")
	gs_indirectinc_total = gs_indirectinc.aggregate(the_sum=Coalesce(Sum('ledgergroups__To_pl_credit'), Value(0)))['the_sum']


	inbox = Message.objects.filter(reciever=request.user)
	inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
	send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']


	context = {

		'company_details' 		  	: company_details,
		'group1_details'  		  	: group1_details,
		'selectdatefield_details' 	: selectdatefield_details,
		'gs_purchase' 				: gs_purchase,
		'gs_purchase_total'			: gs_purchase_total,
		'gs_sales' 					: gs_sales,
		'gs_sales_total'			: gs_sales_total,
		'gs_directexp'				: gs_directexp,
		'gs_directexp_total'		: gs_directexp_total,
		'gs_directinc'				: gs_directinc,
		'gs_directinc_total'		: gs_directinc_total,
		'gs_indirectinc'			: gs_indirectinc,
		'gs_indirectinc_total'		: gs_indirectinc_total,
		'gs_indirectexp' 			: gs_indirectexp,
		'gs_indirectexp_total'		: gs_indirectexp_total,
		'inbox'					  	: inbox,
		'inbox_count'			  	: inbox_count,
		'send_count'			  	: send_count,
		'Todos'					  	: Todo.objects.filter(User=request.user, complete=False),
		'Todos_total' 			  	: Todo.objects.filter(User=request.user, complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 

				
	}

	return render(request, 'Group_Summary/group_summary_details.html', context)



class group1DetailView(ProductExistsRequiredMixin,LoginRequiredMixin,DetailView):
	context_object_name = 'group1_details'
	model = group1
	template_name = 'accounting_double_entry/group1_details.html'

	def get_object(self):
		pk1 = self.kwargs['pk1']
		pk2 = self.kwargs['pk2']
		pk3 = self.kwargs['pk3']
		get_object_or_404(selectdatefield, pk=pk3)
		get_object_or_404(company, pk=pk1)
		group = get_object_or_404(group1, pk=pk2)
		return group


	def get_context_data(self, **kwargs):
		context = super(group1DetailView, self).get_context_data(**kwargs) 
		company_details = get_object_or_404(company, pk=self.kwargs['pk1'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		return context


class group1CreateView(ProductExistsRequiredMixin,LoginRequiredMixin,CreateView):
	form_class  = group1Form
	template_name = "accounting_double_entry/group1_form.html"

	def get_success_url(self,**kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		return reverse('accounting_double_entry:grouplist', kwargs={'pk':company_details.pk, 'pk3':selectdatefield_details.pk})


	def form_valid(self, form):
		form.instance.User = self.request.user
		c = company.objects.get(pk=self.kwargs['pk'])
		form.instance.Company = c
		counter = group1.objects.filter(User=self.request.user, Company=c).count() + 1
		form.instance.counter = counter
		return super(group1CreateView, self).form_valid(form)

	def get_form_kwargs(self):
		data = super(group1CreateView, self).get_form_kwargs()
		data.update(
			User=self.request.user,
			Company=company.objects.get(pk=self.kwargs['pk'])
			)
		return data

	def get_context_data(self, **kwargs):
		context = super(group1CreateView, self).get_context_data(**kwargs) 
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		return context

class group1UpdateView(ProductExistsRequiredMixin,LoginRequiredMixin,UpdateView):
	model = group1
	form_class  = group1Form
	template_name = "accounting_double_entry/group1_form.html"


	def get_success_url(self,**kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk1'])
		group1_details  = get_object_or_404(group1, pk=self.kwargs['pk2'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		return reverse('accounting_double_entry:groupdetail', kwargs={'pk1':company_details.pk, 'pk2':group1_details.pk,'pk3':selectdatefield_details.pk})

	def get_object(self):
		pk1 = self.kwargs['pk1']
		pk2 = self.kwargs['pk2']
		get_object_or_404(company, pk=pk1)
		group = get_object_or_404(group1, pk=pk2)
		return group

	def get_form_kwargs(self):
		data = super(group1UpdateView, self).get_form_kwargs()
		data.update(
			User=self.request.user,
			Company=company.objects.get(pk=self.kwargs['pk1'])
			)
		return data


	def get_context_data(self, **kwargs):
		context = super(group1UpdateView, self).get_context_data(**kwargs) 
		company_details = get_object_or_404(company, pk=self.kwargs['pk1'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		return context

def save_all(request,form,template_name,pk, pk3):
	company_details = get_object_or_404(company, pk=pk)
	selectdatefield_details = get_object_or_404(selectdatefield, pk=pk3)
	data = dict()
	if request.method == 'POST':
		if form.is_valid():
			form.save()
			data['form_is_valid'] = True
			group1_list = group1.objects.filter(User= request.user, Company=company_details.pk).order_by('-id')
			data['group_list'] = render_to_string('accounting_double_entry/group1_list2.html',{'group1_list':group1_list})
		else:
			data['form_is_valid'] = False
	context = {

		'form':form,
		'company_details' : company_details,
		'selectdatefield_details' : selectdatefield_details
	}
	data['html_form'] = render_to_string(template_name,context,request=request)

	return JsonResponse(data)

@login_required
@product_1_activation
def group_delete_view(request, pk, pk2, pk3):
	data = dict()
	company_details = get_object_or_404(company, pk=pk)
	group = get_object_or_404(group1, pk=pk2)
	selectdatefield_details = get_object_or_404(selectdatefield, pk=pk3)

	if request.method == "POST":
		group.delete()
		data['form_is_valid'] = True
		group1_list = group1.objects.filter(User= request.user, Company=company_details.pk).order_by('-id')
		context = {
			'group1_list':group1_list,
			'company_details' : company_details,
			'selectdatefield_details' : selectdatefield_details,
		}
		data['group_list'] = render_to_string('accounting_double_entry/group1_list2.html',context)
	else:
		context = {
			'group':group,
			'company_details' : company_details,
			'selectdatefield_details' : selectdatefield_details,
		}
		data['html_form'] = render_to_string('accounting_double_entry/group1_confirm_delete.html',context,request=request)

	return JsonResponse(data)




################## Views For Ledger Monthly Display ###################################


@login_required
@product_1_activation
def ledger_monthly_detail_view(request, pk, pk2, pk3):
	company_details = get_object_or_404(company, pk=pk)
	ledger1_details = get_object_or_404(ledger1, pk=pk2)
	selectdatefield_details = get_object_or_404(selectdatefield, pk=pk3)


	
	# opening balance
	if company_details.gst_enabled == True:
		if (ledger1_details.name == 'Profit & Loss A/c'):
			qsob  = Pl_journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk,  Date__lt=selectdatefield_details.Start_Date).order_by('Date')
			qsob2 = Pl_journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk,  Date__lt=selectdatefield_details.Start_Date).order_by('Date')
		else:
			qsob  = journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk,  Date__lt=selectdatefield_details.Start_Date).order_by('Date')
			qsob2 = journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk,  Date__lt=selectdatefield_details.Start_Date).order_by('Date')
	else:
		if (ledger1_details.name == 'Profit & Loss A/c'):
			qsob  = Pl_journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk,  Date__lt=selectdatefield_details.Start_Date).exclude(To__group1_Name__group_Name__icontains='GST').order_by('Date')
			qsob2 = Pl_journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk,  Date__lt=selectdatefield_details.Start_Date).exclude(By__group1_Name__group_Name__icontains='GST').order_by('Date')
		else:
			qsob  = journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk,  Date__lt=selectdatefield_details.Start_Date).exclude(To__group1_Name__group_Name__icontains='GST').order_by('Date')
			qsob2 = journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk,  Date__lt=selectdatefield_details.Start_Date).exclude(By__group1_Name__group_Name__icontains='GST').order_by('Date')

	total_debitob = qsob.aggregate(the_sum=Coalesce(Sum('Debit'), Value(0)))['the_sum']
	total_creditob = qsob2.aggregate(the_sum=Coalesce(Sum('Credit'), Value(0)))['the_sum']



	if(ledger1_details.group1_Name.balance_nature == 'Debit'):
		opening_balance = abs(ledger1_details.Opening_Balance) + abs(total_debitob) - abs(total_creditob)
	else:
		opening_balance = abs(ledger1_details.Opening_Balance) + abs(total_creditob) - abs(total_debitob) 


	results = collections.OrderedDict()


	if company_details.gst_enabled == True:
		if (ledger1_details.name == 'Profit & Loss A/c'):
			qscb  = Pl_journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).annotate(real_total_debit = Case(When(Debit__isnull=True, then=0),default=F('Debit')))
			qscb2 = Pl_journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).annotate(real_total_credit = Case(When(Credit__isnull=True, then=0),default=F('Credit')))
			qscb3 = Pl_journal.objects.filter(id=0).annotate(real_total_debit = Case(When(Debit__isnull=True, then=0),default=F('Debit')))
			qscb4 = Pl_journal.objects.filter(id=0).annotate(real_total_credit = Case(When(Credit__isnull=True, then=0),default=F('Credit')))	
		
		else:
			qscb  = journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).annotate(real_total_debit = Case(When(Debit__isnull=True, then=0),default=F('Debit')))
			qscb2 = journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).annotate(real_total_credit = Case(When(Credit__isnull=True, then=0),default=F('Credit')))	
			qscb3 = Pl_journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).annotate(real_total_debit = Case(When(Debit__isnull=True, then=0),default=F('Debit')))
			qscb4 = Pl_journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).annotate(real_total_credit = Case(When(Credit__isnull=True, then=0),default=F('Credit')))	
	else:
		if (ledger1_details.name == 'Profit & Loss A/c'):
			qscb  = Pl_journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).exclude(To__group1_Name__group_Name__icontains='GST').annotate(real_total_debit = Case(When(Debit__isnull=True, then=0),default=F('Debit')))
			qscb2 = Pl_journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).exclude(By__group1_Name__group_Name__icontains='GST').annotate(real_total_credit = Case(When(Credit__isnull=True, then=0),default=F('Credit')))
			qscb3 = Pl_journal.objects.filter(id=0).annotate(real_total_debit = Case(When(Debit__isnull=True, then=0),default=F('Debit')))
			qscb4 = Pl_journal.objects.filter(id=0).annotate(real_total_credit = Case(When(Credit__isnull=True, then=0),default=F('Credit')))	
		
		else:
			qscb  = journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).exclude(To__group1_Name__group_Name__icontains='GST').annotate(real_total_debit = Case(When(Debit__isnull=True, then=0),default=F('Debit')))
			qscb2 = journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).exclude(By__group1_Name__group_Name__icontains='GST').annotate(real_total_credit = Case(When(Credit__isnull=True, then=0),default=F('Credit')))	
			qscb3 = Pl_journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).exclude(To__group1_Name__group_Name__icontains='GST').annotate(real_total_debit = Case(When(Debit__isnull=True, then=0),default=F('Debit')))
			qscb4 = Pl_journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).exclude(By__group1_Name__group_Name__icontains='GST').annotate(real_total_credit = Case(When(Credit__isnull=True, then=0),default=F('Credit')))


	date_cursor = selectdatefield_details.Start_Date

	z = 0
	k = 0

	while date_cursor <= selectdatefield_details.End_Date:
		month_partial_total_debit = qscb.filter(Date__month=date_cursor.month).aggregate(partial_total_debit=Sum('real_total_debit'))['partial_total_debit']
		month_partial_total_credit = qscb2.filter(Date__month=date_cursor.month).aggregate(partial_total_credit=Sum('real_total_credit'))['partial_total_credit']
		month_partial_total_debit_pl = qscb3.filter(Date__month=date_cursor.month).aggregate(partial_total_debit=Sum('real_total_debit'))['partial_total_debit']
		month_partial_total_credit_pl = qscb4.filter(Date__month=date_cursor.month).aggregate(partial_total_credit=Sum('real_total_credit'))['partial_total_credit']

		if month_partial_total_debit == None:

			month_partial_total_debit = int(0)

			e = month_partial_total_debit 

		else:

			e = month_partial_total_debit


		if month_partial_total_credit == None:

			month_partial_total_credit = int(0)

			f = month_partial_total_credit

		else:

			f = month_partial_total_credit

		if month_partial_total_debit_pl == None:

			month_partial_total_debit_pl = int(0)

			g = month_partial_total_debit_pl 

		else:

			g = month_partial_total_debit_pl

		if month_partial_total_credit_pl == None:

			month_partial_total_credit_pl = int(0)

			h = month_partial_total_credit_pl 

		else:

			h = month_partial_total_credit_pl


		if (ledger1_details.name != 'Profit & Loss A/c'):
			if(ledger1_details.group1_Name.balance_nature == 'Debit'):

				z = z + e + g - f - h 

			else:
				z = z + f + h - e - g 
		else:
			if(ledger1_details.group1_Name.balance_nature == 'Debit'):

				z = z + e  - f  

			else:
				z = z + f  - e  

		k = z + opening_balance

		results[date_cursor.month] =  [e,f,k,g,h]

		date_cursor += dateutil.relativedelta.relativedelta(months=1)

	total_debit = qscb.aggregate(the_sum=Coalesce(Sum('Debit'), Value(0)))['the_sum']
	total_credit = qscb2.aggregate(the_sum=Coalesce(Sum('Credit'), Value(0)))['the_sum']
	total_debit_pl = qscb3.aggregate(the_sum=Coalesce(Sum('Debit'), Value(0)))['the_sum']
	total_credit_pl = qscb4.aggregate(the_sum=Coalesce(Sum('Credit'), Value(0)))['the_sum']


	if (ledger1_details.name != 'Profit & Loss A/c'):
		if(ledger1_details.group1_Name.balance_nature == 'Debit'):

			total1 = total_debit + total_debit_pl - total_credit - total_credit_pl
		else:
			 total1 = total_credit + total_credit_pl - total_debit - total_debit_pl
	else:
		if(ledger1_details.group1_Name.balance_nature == 'Debit'):

			total1 = total_debit - total_credit 
		else:
			 total1 = total_credit - total_debit 


	total = total1 + opening_balance

	inbox = Message.objects.filter(reciever=request.user)
	inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
	send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']


	context = {

		'company_details' 			: company_details,
		'ledger1_details' 			: ledger1_details,
		'selectdatefield_details' 	: selectdatefield_details,
		'total_debit'     			: total_debit,
		'total_credit'   			: total_credit,
		'total_debit_pl'			: total_debit_pl,
		'total_credit_pl'			: total_credit_pl,
		'total'			  			: total,
		'data'			  			: results.items(),
		'opening_balance' 			: opening_balance,
		'inbox'					  	: inbox,
		'inbox_count'			  	: inbox_count,
		'send_count'				: send_count,
		'Todos'			  			: Todo.objects.filter(User=request.user, complete=False),
		'Todos_total' 	  			: Todo.objects.filter(User=request.user, complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 


				
	}

	return render(request, 'accounting_double_entry/ledger_monthly.html', context)



def ledger_register_datewise(request,month,pk,pk2,pk3):
	company_details = get_object_or_404(company, pk=pk)
	selectdatefield_details = get_object_or_404(selectdatefield, pk=pk3)
	ledger1_details = get_object_or_404(ledger1, pk=pk2)

	# opening balance
	if company_details.gst_enabled == True:
		if (ledger1_details.name == 'Profit & Loss A/c'):
			qsob  = Pl_journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk, Date__month=month, Date__lt=selectdatefield_details.Start_Date)
			qsob2 = Pl_journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk, Date__month=month, Date__lt=selectdatefield_details.Start_Date)
		else:
			qsob  = journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk, Date__lt=selectdatefield_details.Start_Date)
			qsob2 = journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk, Date__lt=selectdatefield_details.Start_Date)
	else:
		if (ledger1_details.name == 'Profit & Loss A/c'):
			qsob  = Pl_journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk, Date__month=month, Date__lt=selectdatefield_details.Start_Date).exclude(To__group1_Name__group_Name__icontains='GST')
			qsob2 = Pl_journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk, Date__month=month, Date__lt=selectdatefield_details.Start_Date).exclude(By__group1_Name__group_Name__icontains='GST')
		else:
			qsob  = journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk, Date__lt=selectdatefield_details.Start_Date).exclude(To__group1_Name__group_Name__icontains='GST')
			qsob2 = journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk, Date__lt=selectdatefield_details.Start_Date).exclude(By__group1_Name__group_Name__icontains='GST')


	total_debitob = qsob.aggregate(the_sum=Coalesce(Sum('Debit'), Value(0)))['the_sum']
	total_creditob = qsob2.aggregate(the_sum=Coalesce(Sum('Credit'), Value(0)))['the_sum']

	if(ledger1_details.group1_Name.balance_nature == 'Debit'):
		opening_balance = abs(ledger1_details.Opening_Balance) + abs(total_debitob) - abs(total_creditob)
	else:
		opening_balance = abs(ledger1_details.Opening_Balance) + abs(total_creditob) - abs(total_debitob) 


	if company_details.gst_enabled == False:
		if (ledger1_details.name == 'Profit & Loss A/c'):
			qscb  = Pl_journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk, Date__month=month, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).exclude(To__group1_Name__group_Name__icontains='GST')
			qscb2 = Pl_journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk, Date__month=month, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).exclude(By__group1_Name__group_Name__icontains='GST')
			qscb3 = Pl_journal.objects.filter(id=0)
			qscb4 = Pl_journal.objects.filter(id=0)	
		
		else:
			qscb  = journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk, Date__month=month, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).exclude(To__group1_Name__group_Name__icontains='GST')
			qscb2 = journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk, Date__month=month, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).exclude(By__group1_Name__group_Name__icontains='GST')	
			qscb3 = Pl_journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk, Date__month=month, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).exclude(To__group1_Name__group_Name__icontains='GST')
			qscb4 = Pl_journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk, Date__month=month, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).exclude(By__group1_Name__group_Name__icontains='GST')	
	else:
		if (ledger1_details.name == 'Profit & Loss A/c'):
			qscb  = Pl_journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk, Date__month=month, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date)
			qscb2 = Pl_journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk, Date__month=month, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date)
			qscb3 = Pl_journal.objects.filter(id=0)
			qscb4 = Pl_journal.objects.filter(id=0)	
		
		else:
			qscb  = journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk, Date__month=month, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date)
			qscb2 = journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk, Date__month=month, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date)	
			qscb3 = Pl_journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk, Date__month=month, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date)
			qscb4 = Pl_journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk, Date__month=month, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date)	

	new   = zip_longest(qscb,qscb2,qscb3,qscb4)

	total_debitcb = qscb.aggregate(the_sum=Coalesce(Sum('Debit'), Value(0)))['the_sum']
	total_creditcb = qscb2.aggregate(the_sum=Coalesce(Sum('Credit'), Value(0)))['the_sum']
	total_debitcbpl = qscb3.aggregate(the_sum=Coalesce(Sum('Debit'), Value(0)))['the_sum']
	total_creditcbpl = qscb4.aggregate(the_sum=Coalesce(Sum('Credit'), Value(0)))['the_sum']


	if company_details.gst_enabled == True:
		if (ledger1_details.name == 'Profit & Loss A/c'):
			qs  = Pl_journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk, Date__month__gte=selectdatefield_details.Start_Date.month, Date__month__lte=month)
			qs2 = Pl_journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk, Date__month__gte=selectdatefield_details.Start_Date.month, Date__month__lte=month)
			qs3 = Pl_journal.objects.filter(id=0)
			qs4 = Pl_journal.objects.filter(id=0)	
		
		else:
			qs  = journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk, Date__month__gte=selectdatefield_details.Start_Date.month, Date__month__lte=month)
			qs2 = journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk, Date__month__gte=selectdatefield_details.Start_Date.month, Date__month__lte=month)	
			qs3 = Pl_journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk, Date__month__gte=selectdatefield_details.Start_Date.month, Date__month__lte=month)
			qs4 = Pl_journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk, Date__month__gte=selectdatefield_details.Start_Date.month, Date__month__lte=month)	
	else:
		if (ledger1_details.name == 'Profit & Loss A/c'):
			qs  = Pl_journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk, Date__month__gte=selectdatefield_details.Start_Date.month, Date__month__lte=month).exclude(To__group1_Name__group_Name__icontains='GST')
			qs2 = Pl_journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk, Date__month__gte=selectdatefield_details.Start_Date.month, Date__month__lte=month).exclude(By__group1_Name__group_Name__icontains='GST')
			qs3 = Pl_journal.objects.filter(id=0)
			qs4 = Pl_journal.objects.filter(id=0)	
		
		else:
			qs  = journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk, Date__month__gte=selectdatefield_details.Start_Date.month, Date__month__lte=month).exclude(To__group1_Name__group_Name__icontains='GST').exclude(To__group1_Name__group_Name__icontains='GST')
			qs2 = journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk, Date__month__gte=selectdatefield_details.Start_Date.month, Date__month__lte=month).exclude(By__group1_Name__group_Name__icontains='GST')	
			qs3 = Pl_journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk, Date__month__gte=selectdatefield_details.Start_Date.month, Date__month__lte=month).exclude(To__group1_Name__group_Name__icontains='GST')
			qs4 = Pl_journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk, Date__month__gte=selectdatefield_details.Start_Date.month, Date__month__lte=month).exclude(By__group1_Name__group_Name__icontains='GST')	



	total_debit = qs.aggregate(the_sum=Coalesce(Sum('Debit'), Value(0)))['the_sum']
	total_credit = qs2.aggregate(the_sum=Coalesce(Sum('Credit'), Value(0)))['the_sum']
	total_debitpl = qs3.aggregate(the_sum=Coalesce(Sum('Debit'), Value(0)))['the_sum']
	total_creditpl = qs4.aggregate(the_sum=Coalesce(Sum('Credit'), Value(0)))['the_sum']

	if (ledger1_details.name != 'Profit & Loss A/c'):
		if(ledger1_details.group1_Name.balance_nature == 'Debit'):
			closing_balance = opening_balance + abs(total_debit) + abs(total_debitpl) - abs(total_credit) - abs(total_creditpl) 
		else:
			closing_balance = opening_balance + abs(total_credit) + abs(total_creditpl) - abs(total_debit) - abs(total_debitpl)
	else:
		if(ledger1_details.group1_Name.balance_nature == 'Debit'):
			closing_balance = opening_balance + abs(total_debit) - abs(total_credit) 
		else:
			closing_balance = opening_balance + abs(total_credit) - abs(total_debit) 

	if (ledger1_details.name != 'Profit & Loss A/c'):
		if(ledger1_details.group1_Name.balance_nature == 'Debit'):
			#closing_balance = opening_balance + abs(total_debit) + abs(total_debitpl) - abs(total_credit) - abs(total_creditpl) 
			opening_balancerev =  closing_balance - abs(total_debitcb) - abs(total_debitcbpl) + abs(total_creditcb) + abs(total_creditcbpl)
		else:
			opening_balancerev =  closing_balance - abs(total_creditcb) - abs(total_creditcbpl) + abs(total_debitcb) + abs(total_debitcbpl)
	else:
		if(ledger1_details.group1_Name.balance_nature == 'Debit'):
			opening_balancerev =  closing_balance - abs(total_debitcb) + abs(total_creditcb) 
		else:
			opening_balancerev =  closing_balance - abs(total_creditcb) + abs(total_debitcb) 


	inbox = Message.objects.filter(reciever=request.user)
	inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
	send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']


	context = {

		'company_details'             : company_details,
		'selectdatefield_details' 	  : selectdatefield_details,
		'ledger1_details' 			  : ledger1_details,
		'new'						  : new,
		'total_debitcb' 			  : total_debitcb,
		'total_creditcb'			  : total_creditcb,
		'total_debitcbpl' 			  : total_debitcbpl,
		'total_creditcbpl' 			  : total_creditcbpl,
		'closing_balance' 			  : closing_balance,
		'opening_balance' 			  : opening_balancerev,
		'm' 					  	  : calendar.month_name[int(month)],
		'inbox'						  : inbox,
		'inbox_count'				  : inbox_count,
		'send_count'				  : send_count,
		'Todos'					      : Todo.objects.filter(User=request.user, complete=False),
		'Todos_total' 			      : Todo.objects.filter(User=request.user, complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 

				
	}

	return render(request, 'accounting_double_entry/ledger_daily.html', context)



@login_required
@product_1_activation
def ledger_monthly_detail_view_2(request, pk, pk2, pk3):
	company_details = get_object_or_404(company, pk=pk)
	ledger1_details = get_object_or_404(ledger1, pk=pk2)
	selectdatefield_details = get_object_or_404(selectdatefield, pk=pk3)
	
	# opening balance
	if company_details.gst_enabled == True:
		qsob  = journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk,  Date__lt=selectdatefield_details.Start_Date).order_by('Date')
		qsob2 = journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk,  Date__lt=selectdatefield_details.Start_Date).order_by('Date')
	else:
		qsob  = journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk,  Date__lt=selectdatefield_details.Start_Date).exclude(To__group1_Name__group_Name__icontains='GST').order_by('Date')
		qsob2 = journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk,  Date__lt=selectdatefield_details.Start_Date).exclude(By__group1_Name__group_Name__icontains='GST').order_by('Date')

	total_debitob = qsob.aggregate(the_sum=Coalesce(Sum('Debit'), Value(0)))['the_sum']
	total_creditob = qsob2.aggregate(the_sum=Coalesce(Sum('Credit'), Value(0)))['the_sum']


	if(ledger1_details.group1_Name.balance_nature == 'Debit'):
		opening_balance = abs(ledger1_details.Opening_Balance) + abs(total_debitob) - abs(total_creditob)
	else:
		opening_balance = abs(ledger1_details.Opening_Balance) + abs(total_creditob) - abs(total_debitob) 


	results = collections.OrderedDict()


	if company_details.gst_enabled == True:	
		qscb  = journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).annotate(real_total_debit = Case(When(Debit__isnull=True, then=0),default=F('Debit')))
		qscb2 = journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).annotate(real_total_credit = Case(When(Credit__isnull=True, then=0),default=F('Credit')))	
	else:		
		qscb  = journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).exclude(To__group1_Name__group_Name__icontains='GST').annotate(real_total_debit = Case(When(Debit__isnull=True, then=0),default=F('Debit')))
		qscb2 = journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).exclude(By__group1_Name__group_Name__icontains='GST').annotate(real_total_credit = Case(When(Credit__isnull=True, then=0),default=F('Credit')))	


	date_cursor = selectdatefield_details.Start_Date

	z = 0
	k = 0

	while date_cursor <= selectdatefield_details.End_Date:
		month_partial_total_debit = qscb.filter(Date__month=date_cursor.month).aggregate(partial_total_debit=Sum('real_total_debit'))['partial_total_debit']
		month_partial_total_credit = qscb2.filter(Date__month=date_cursor.month).aggregate(partial_total_credit=Sum('real_total_credit'))['partial_total_credit']

		if month_partial_total_debit == None:

			month_partial_total_debit = int(0)

			e = month_partial_total_debit 

		else:

			e = month_partial_total_debit


		if month_partial_total_credit == None:

			month_partial_total_credit = int(0)

			f = month_partial_total_credit

		else:

			f = month_partial_total_credit


		if (ledger1_details.name != 'Profit & Loss A/c'):
			if(ledger1_details.group1_Name.balance_nature == 'Debit'):

				z = z + e - f  

			else:
				z = z + f - e 
		else:
			if(ledger1_details.group1_Name.balance_nature == 'Debit'):

				z = z + e - f  

			else:
				z = z + f - e  

		k = z + opening_balance

		results[date_cursor.month] =  [e,f,k]

		date_cursor += dateutil.relativedelta.relativedelta(months=1)

	total_debit = qscb.aggregate(the_sum=Coalesce(Sum('Debit'), Value(0)))['the_sum']
	total_credit = qscb2.aggregate(the_sum=Coalesce(Sum('Credit'), Value(0)))['the_sum']


	if (ledger1_details.name != 'Profit & Loss A/c'):
		if(ledger1_details.group1_Name.balance_nature == 'Debit'):

			total1 = total_debit  - total_credit 
		else:
			 total1 = total_credit  - total_debit 
	else:
		if(ledger1_details.group1_Name.balance_nature == 'Debit'):

			total1 = total_debit - total_credit 
		else:
			 total1 = total_credit - total_debit 


	total = total1 + opening_balance

	inbox = Message.objects.filter(reciever=request.user)
	inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
	send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']


	context = {

		'company_details' 			: company_details,
		'ledger1_details' 			: ledger1_details,
		'selectdatefield_details' 	: selectdatefield_details,
		'total_debit'     			: total_debit,
		'total_credit'   			: total_credit,
		'total'			  			: total,
		'data'			  			: results.items(),
		'opening_balance' 			: opening_balance,
		'inbox'					  	: inbox,
		'inbox_count'			  	: inbox_count,
		'send_count'				: send_count,
		'Todos'			  			: Todo.objects.filter(User=request.user, complete=False),
		'Todos_total' 	  			: Todo.objects.filter(User=request.user, complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
				
	}

	return render(request, 'accounting_double_entry/ledger_monthly_2.html', context)



def ledger_register_datewise_2(request,month,pk,pk2,pk3):
	company_details = get_object_or_404(company, pk=pk)
	selectdatefield_details = get_object_or_404(selectdatefield, pk=pk3)
	ledger1_details = get_object_or_404(ledger1, pk=pk2)

	# opening balance
	if company_details.gst_enabled == True:
		qsob  = journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk, Date__lt=selectdatefield_details.Start_Date)
		qsob2 = journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk, Date__lt=selectdatefield_details.Start_Date)
	else:
		qsob  = journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk, Date__lt=selectdatefield_details.Start_Date).exclude(To__group1_Name__group_Name__icontains='GST')
		qsob2 = journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk, Date__lt=selectdatefield_details.Start_Date).exclude(By__group1_Name__group_Name__icontains='GST')


	total_debitob = qsob.aggregate(the_sum=Coalesce(Sum('Debit'), Value(0)))['the_sum']
	total_creditob = qsob2.aggregate(the_sum=Coalesce(Sum('Credit'), Value(0)))['the_sum']

	if(ledger1_details.group1_Name.balance_nature == 'Debit'):
		opening_balance = abs(ledger1_details.Opening_Balance) + abs(total_debitob) - abs(total_creditob)
	else:
		opening_balance = abs(ledger1_details.Opening_Balance) + abs(total_creditob) - abs(total_debitob) 


	if company_details.gst_enabled == False:
		qscb  = journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk, Date__month=month, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).exclude(To__group1_Name__group_Name__icontains='GST')
		qscb2 = journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk, Date__month=month, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).exclude(By__group1_Name__group_Name__icontains='GST')	
	else:
		qscb  = journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk, Date__month=month, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date)
		qscb2 = journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk, Date__month=month, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date)	

	new   = zip_longest(qscb,qscb2)

	total_debitcb = qscb.aggregate(the_sum=Coalesce(Sum('Debit'), Value(0)))['the_sum']
	total_creditcb = qscb2.aggregate(the_sum=Coalesce(Sum('Credit'), Value(0)))['the_sum']


	if company_details.gst_enabled == True:		
		qs  = journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk, Date__month__gte=selectdatefield_details.Start_Date.month, Date__month__lte=month)
		qs2 = journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk, Date__month__gte=selectdatefield_details.Start_Date.month, Date__month__lte=month)	
	else:		
		qs  = journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk, Date__month__gte=selectdatefield_details.Start_Date.month, Date__month__lte=month).exclude(To__group1_Name__group_Name__icontains='GST').exclude(To__group1_Name__group_Name__icontains='GST')
		qs2 = journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk, Date__month__gte=selectdatefield_details.Start_Date.month, Date__month__lte=month).exclude(By__group1_Name__group_Name__icontains='GST')	


	total_debit = qs.aggregate(the_sum=Coalesce(Sum('Debit'), Value(0)))['the_sum']
	total_credit = qs2.aggregate(the_sum=Coalesce(Sum('Credit'), Value(0)))['the_sum']


	if(ledger1_details.group1_Name.balance_nature == 'Debit'):
		closing_balance = opening_balance + abs(total_debit) - abs(total_credit)
	else:
		closing_balance = opening_balance + abs(total_credit) - abs(total_debit)


	if(ledger1_details.group1_Name.balance_nature == 'Debit'):
		opening_balancerev =  closing_balance - abs(total_debitcb) + abs(total_creditcb)
	else:
		opening_balancerev =  closing_balance - abs(total_creditcb) + abs(total_debitcb)


	inbox = Message.objects.filter(reciever=request.user)
	inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
	send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']


	context = {

		'company_details'             : company_details,
		'selectdatefield_details' 	  : selectdatefield_details,
		'ledger1_details' 			  : ledger1_details,
		'new'						  : new,
		'total_debitcb' 			  : total_debitcb,
		'total_creditcb'			  : total_creditcb,
		'closing_balance' 			  : closing_balance,
		'opening_balance' 			  : opening_balancerev,
		'm' 					  	  : calendar.month_name[int(month)],
		'inbox'						  : inbox,
		'inbox_count'				  : inbox_count,
		'send_count'				  : send_count,
		'Todos'					      : Todo.objects.filter(User=request.user, complete=False),
		'Todos_total' 			      : Todo.objects.filter(User=request.user, complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 

				
	}

	return render(request, 'accounting_double_entry/ledger_daily_2.html', context)




################## Views For Ledger Display ###################################


class ledger1ListView(ProductExistsRequiredMixin,LoginRequiredMixin,ListView):
	model = ledger1

	def get_queryset(self):
		return ledger1.objects.filter(Company=self.kwargs['pk'])

	def get_context_data(self, **kwargs):
		context = super(ledger1ListView, self).get_context_data(**kwargs) 
		context['profile_details'] = Profile.objects.all()
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		context['company_details'] = company_details
		if company_details.gst_enabled == True and company_details.composite_enable == True:
			context['ledger1s'] = ledger1.objects.filter(Company=company_details.pk)
		elif company_details.gst_enabled == True:
			context['ledger1s'] = ledger1.objects.filter(Company=company_details.pk).exclude(Q(name__icontains='Tax'), Q(Closing_balance=0))
		else:
			context['ledger1s'] = ledger1.objects.filter(Company=company_details.pk).exclude(Q(group1_Name__group_Name__icontains='GST') | Q(name__icontains='Tax'))
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		return context

@login_required
@product_1_activation
def ledger1_detail_view(request, pk, pk2, pk3):
	company_details = get_object_or_404(company, pk=pk)
	ledger1_details = get_object_or_404(ledger1, pk=pk2)
	selectdatefield_details = get_object_or_404(selectdatefield, pk=pk3)

	
	# opening balance
	if company_details.gst_enabled == True:
		if (ledger1_details.name == 'Profit & Loss A/c'):
			qsob  = Pl_journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk,  Date__lt=selectdatefield_details.Start_Date).order_by('Date')
			qsob2 = Pl_journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk,  Date__lt=selectdatefield_details.Start_Date).order_by('Date')
		else:
			qsob  = journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk,  Date__lt=selectdatefield_details.Start_Date).order_by('Date')
			qsob2 = journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk,  Date__lt=selectdatefield_details.Start_Date).order_by('Date')
	else:
		if (ledger1_details.name == 'Profit & Loss A/c'):
			qsob  = Pl_journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk,  Date__lt=selectdatefield_details.Start_Date).exclude(To__group1_Name__group_Name__icontains='GST').order_by('Date')
			qsob2 = Pl_journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk,  Date__lt=selectdatefield_details.Start_Date).exclude(By__group1_Name__group_Name__icontains='GST').order_by('Date')
		else:
			qsob  = journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk,  Date__lt=selectdatefield_details.Start_Date).exclude(To__group1_Name__group_Name__icontains='GST').order_by('Date')
			qsob2 = journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk,  Date__lt=selectdatefield_details.Start_Date).exclude(By__group1_Name__group_Name__icontains='GST').order_by('Date')


	total_debitob = qsob.aggregate(the_sum=Coalesce(Sum('Debit'), Value(0)))['the_sum']
	total_creditob = qsob2.aggregate(the_sum=Coalesce(Sum('Credit'), Value(0)))['the_sum']

	# if(ledger1_details.Creation_Date!=selectdatefield_details.Start_Date):
	if(ledger1_details.group1_Name.balance_nature == 'Debit'):
		opening_balance = abs(ledger1_details.Opening_Balance) + abs(total_debitob) - abs(total_creditob)
	else:
		opening_balance = abs(ledger1_details.Opening_Balance) + abs(total_creditob) - abs(total_debitob) 
	# else:
	# 	opening_balance = abs(ledger1_details.Opening_Balance)

	if company_details.gst_enabled == True:
		# closing balance
		if (ledger1_details.name == 'Profit & Loss A/c'):
			qscb  = Pl_journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).order_by('Date')
			qscb2 = Pl_journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).order_by('Date')
		else:
			qscb  = journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).order_by('Date')
			qscb2 = journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).order_by('Date')	
		new   = zip_longest(qscb,qscb2)

		qscb3 = Pl_journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).order_by('Date')
		qscb4 = Pl_journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).order_by('Date')
		new2   = zip_longest(qscb3,qscb4)
	else:
		# closing balance
		if (ledger1_details.name == 'Profit & Loss A/c'):
			qscb  = Pl_journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).exclude(To__group1_Name__group_Name__icontains='GST').order_by('Date')
			qscb2 = Pl_journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).exclude(By__group1_Name__group_Name__icontains='GST').order_by('Date')
		else:
			qscb  = journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).exclude(To__group1_Name__group_Name__icontains='GST').order_by('Date')
			qscb2 = journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).exclude(By__group1_Name__group_Name__icontains='GST').order_by('Date')	
		new   = zip_longest(qscb,qscb2)

		qscb3 = Pl_journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).exclude(To__group1_Name__group_Name__icontains='GST').order_by('Date')
		qscb4 = Pl_journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).exclude(By__group1_Name__group_Name__icontains='GST').order_by('Date')
		new2   = zip_longest(qscb3,qscb4)


	total_debitcb = qscb.aggregate(the_sum=Coalesce(Sum('Debit'), Value(0)))['the_sum']
	total_creditcb = qscb2.aggregate(the_sum=Coalesce(Sum('Credit'), Value(0)))['the_sum']
	total_debitcbpl = qscb3.aggregate(the_sum=Coalesce(Sum('Debit'), Value(0)))['the_sum']
	total_creditcbpl = qscb4.aggregate(the_sum=Coalesce(Sum('Credit'), Value(0)))['the_sum']

	if (ledger1_details.name != 'Profit & Loss A/c'):
		if(ledger1_details.group1_Name.balance_nature == 'Debit'):
			closing_balance = abs(opening_balance) + abs(total_debitcb) + abs(total_debitcbpl) - abs(total_creditcb) - abs(total_creditcbpl) 
		else:
			closing_balance = abs(opening_balance) + abs(total_creditcb) + abs(total_creditcbpl) - abs(total_debitcb) - abs(total_debitcbpl)
	else:
		if(ledger1_details.group1_Name.balance_nature == 'Debit'):
			closing_balance = abs(opening_balance) + abs(total_debitcb) - abs(total_creditcb) 
		else:
			closing_balance = abs(opening_balance) + abs(total_creditcb) - abs(total_debitcb) 


	ledger1_detail = ledger1.objects.get(pk=ledger1_details.pk)
	ledger1_detail.Closing_balance = closing_balance
	ledger1_detail.Balance_opening = opening_balance
	ledger1_detail.save(update_fields=['Closing_balance', 'Balance_opening'])

	inbox = Message.objects.filter(reciever=request.user)
	inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
	send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

	context = {

		'company_details' 			: company_details,
		'ledger1_details' 			: ledger1_details,
		'selectdatefield_details' 	: selectdatefield_details,
		'total_debit'     			: abs(total_debitcb),
		'total_credit'    			: abs(total_creditcb),
		'total_debit_pl'			: abs(total_debitcbpl),
		'total_credit_pl'			: abs(total_creditcbpl),
		'journal_debit'   			: qscb,
		'journal_credit'  			: qscb2,
		'n'				  			: new,
		'n2'						: new2,
		'closing_balance' 			: closing_balance,
		'opening_balance' 			: opening_balance,		
		'company_list'    			: company.objects.all(),
		'inbox'					 	: inbox,
		'inbox_count'			  	: inbox_count,
		'send_count'				: send_count,
		'selectdate' 	  			: selectdatefield.objects.filter(User=request.user),
		'Todos'			  			: Todo.objects.filter(User=request.user, complete=False),
		'Todos_total' 	 			: Todo.objects.filter(User=request.user, complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 

				
	}	

	return render(request, 'accounting_double_entry/ledger1_details.html', context)




class ledger1CreateView(ProductExistsRequiredMixin,LoginRequiredMixin,CreateView):
	form_class = Ledgerform
	template_name = "accounting_double_entry/ledger1_form.html"

	def get_success_url(self,**kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		return reverse('accounting_double_entry:ledgerlist', kwargs={'pk':company_details.pk, 'pk3':selectdatefield_details.pk})

	def form_valid(self, form):
		form.instance.User = self.request.user
		c = company.objects.get(pk=self.kwargs['pk'])
		form.instance.Company = c
		counter = ledger1.objects.filter(User=self.request.user, Company=c).count() + 1
		form.instance.counter = counter
		return super(ledger1CreateView, self).form_valid(form)

	def get_form_kwargs(self):
		data = super(ledger1CreateView, self).get_form_kwargs()
		data.update(
			User=self.request.user,
			Company=company.objects.get(pk=self.kwargs['pk'])
			)
		return data

	def get_context_data(self, **kwargs):
		context = super(ledger1CreateView, self).get_context_data(**kwargs) 
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		return context


class ledger1UpdateView(ProductExistsRequiredMixin,LoginRequiredMixin,UpdateView):
	model = ledger1
	form_class = Ledgerform
	template_name = "accounting_double_entry/ledger1_form.html"

	def get_success_url(self,**kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		ledger1_details = get_object_or_404(ledger1, pk=self.kwargs['pk2'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		return reverse('accounting_double_entry:ledgerdetail', kwargs={'pk':company_details.pk, 'pk2':ledger1_details.pk, 'pk3' : selectdatefield_details.pk})

	def get_object(self):
		pk = self.kwargs['pk']
		pk2 = self.kwargs['pk2']
		get_object_or_404(company, pk=pk)
		ledger = get_object_or_404(ledger1, pk=pk2)
		return ledger

	def get_form_kwargs(self):
		data = super(ledger1UpdateView, self).get_form_kwargs()
		data.update(
			User=self.request.user,
			Company=company.objects.get(pk=self.kwargs['pk'])
			)
		return data


	def get_context_data(self, **kwargs):
		context = super(ledger1UpdateView, self).get_context_data(**kwargs) 
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		return context


@login_required
@product_1_activation
def ledger_delete_view(request, pk, pk2, pk3):
	data = dict()
	company_details = get_object_or_404(company, pk=pk)
	ledger = get_object_or_404(ledger1, pk=pk2)
	selectdatefield_details = get_object_or_404(selectdatefield, pk=pk3)

	if request.method == "POST":
		ledger.delete()
		data['form_is_valid'] = True
		ledger1_list = ledger1.objects.filter(User= request.user, Company=company_details.pk).order_by('-id')
		context = {
			'ledger1_list':ledger1_list,
			'company_details' : company_details,
			'selectdatefield_details' : selectdatefield_details,
		}
		data['ledger_list'] = render_to_string('accounting_double_entry/ledger_list_2.html',context)
	else:
		context = {
			'ledger':ledger,
			'company_details' : company_details,
			'selectdatefield_details' : selectdatefield_details,
		}
		data['html_form'] = render_to_string('accounting_double_entry/ledger1_confirm_delete.html',context,request=request)

	return JsonResponse(data)


################## Views For journal register Display ###################################
	
class Journal_Register_view(ProductExistsRequiredMixin,LoginRequiredMixin,ListView):
	model = journal
	template_name = 'accounting_double_entry/Journal_register.html'

	def get_context_data(self, **kwargs):
		context = super(Journal_Register_view, self).get_context_data(**kwargs)
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['company_details'] = company_details
		context['selectdatefield_details'] = selectdatefield_details

		results = collections.OrderedDict()
		result = journal.objects.filter(Company=company_details.pk, voucher_type = 'Journal',Date__gte=selectdatefield_details.Start_Date, Date__lt=selectdatefield_details.End_Date).annotate(real_total = Case(When(Debit__isnull=True, then=0),default=F('Debit')))

		date_cursor = selectdatefield_details.Start_Date


		while date_cursor <= selectdatefield_details.End_Date:
			month_partial_total = result.filter(Date__month=date_cursor.month).aggregate(partial_total=Count('real_total'))['partial_total']

			if month_partial_total == None:

				month_partial_total = int(0)

				e = month_partial_total

			else:

				e = month_partial_total


			results[date_cursor.month] = e 			

			date_cursor += dateutil.relativedelta.relativedelta(months=1)

		total_voucher = result.aggregate(the_sum=Coalesce(Count('real_total'), Value(0)))['the_sum']

		total = total_voucher

		context['data'] = results.items()
		context['total'] = total
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		return context

@login_required
@product_1_activation
def journal_register_datewise(request,month,pk,pk3):
	company_details = get_object_or_404(company, pk=pk)
	selectdatefield_details = get_object_or_404(selectdatefield, pk=pk3)

	result 	= journal.objects.filter(Company=company_details.pk, voucher_type = 'Journal', Date__month=month,Date__gte=selectdatefield_details.Start_Date, Date__lt=selectdatefield_details.End_Date)

	total_debit = result.aggregate(partial_total=Sum('Debit'))['partial_total']
	total_credit = result.aggregate(partial_total=Sum('Credit'))['partial_total']

	inbox = Message.objects.filter(reciever=request.user)
	inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
	send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']


	context = {

		'company_details'             : company_details,
		'selectdatefield_details' 	  : selectdatefield_details,
		'result' 		  			  : result,
		'm' 					  	  : calendar.month_name[int(month)],
		'total_debit' 				  : total_debit,
		'total_credit' 				  : total_credit,
		'inbox'						  : inbox,
		'inbox_count'				  : inbox_count,
		'send_count'				  : send_count,
		'Todos'					      : Todo.objects.filter(User=request.user, complete=False),
		'Todos_total' 			      : Todo.objects.filter(User=request.user, complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 

				
	}

	return render(request, 'accounting_double_entry/journal_datewise.html', context)


################## Views For journal Display ###################################


class journalListView(ProductExistsRequiredMixin,LoginRequiredMixin,ListView):
	model = journal
	paginate_by = 15

	def get_queryset(self):
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		return journal.objects.filter(Company=self.kwargs['pk'], Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).order_by('-id')


	def get_context_data(self, **kwargs):
		context = super(journalListView, self).get_context_data(**kwargs) 
		context['profile_details'] = Profile.objects.all()
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['pl_journals'] = Pl_journal.objects.filter(Company=company_details.pk, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).order_by('Date')
		context['journal_list'] = journal.objects.filter(Company=company_details.pk, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).order_by('Date')
		context['new']   = zip_longest(context['pl_journals'],context['journal_list'])
		return context

class DaybookListView(ProductExistsRequiredMixin,LoginRequiredMixin,ListView):
	model = journal
	paginate_by = 15

	def get_template_names(self):
		if True:  
			return ['Daybook/daybook.html']
		else:
			return ['accounting_double_entry/journal_list.html']

	def get_queryset(self):
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		return journal.objects.filter(Company=self.kwargs['pk'], Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).order_by('-id')


	def get_context_data(self, **kwargs):
		context = super(DaybookListView, self).get_context_data(**kwargs) 
		context['profile_details'] = Profile.objects.all()
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['pl_journals'] = Pl_journal.objects.filter(Company=company_details.pk, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).order_by('-id')
		context['journal_list'] = journal.objects.filter(Company=company_details.pk, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).order_by('-id')
		context['new']   = zip_longest(context['pl_journals'],context['journal_list'])
		return context

@login_required
@product_1_activation
def journal_detail(request, pk1, pk2, pk3):
	company_details = get_object_or_404(company, pk=pk1)
	journal_details = get_object_or_404(journal, pk=pk2)
	selectdatefield_details = get_object_or_404(selectdatefield, pk=pk3)

	inbox = Message.objects.filter(reciever=request.user)
	inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
	send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

	context = {
		'journal_details'          : journal_details,
		'company_details'          : company_details,
		'inbox'					   : inbox,
		'inbox_count'			   : inbox_count,
		'send_count'			   : send_count,
		'selectdatefield_details'  : selectdatefield_details,
		'Todos'					   : Todo.objects.filter(User=request.user, complete=False),
		'Todos_total'			   : Todo.objects.filter(User=request.user, complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
	}
	return render(request, 'accounting_double_entry/journal_details.html', context)



class journalCreateView(ProductExistsRequiredMixin,LoginRequiredMixin,CreateView):
	model = journal
	form_class  = journalForm

	def get_success_url(self,**kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		return reverse('accounting_double_entry:list', kwargs={'pk':company_details.pk, 'pk3':selectdatefield_details.pk})

	def form_valid(self, form):
		form.instance.User = self.request.user
		c = company.objects.get(pk=self.kwargs['pk'])
		form.instance.Company = c
		counter = journal.objects.filter(User=self.request.user, Company=c).count() + 1
		form.instance.counter = counter
		return super(journalCreateView, self).form_valid(form)

	def get_form_kwargs(self):
		data = super(journalCreateView, self).get_form_kwargs()
		data.update(
			User=self.request.user,
			Company=company.objects.get(pk=self.kwargs['pk'])
			)
		return data


	def get_context_data(self, **kwargs):
		context = super(journalCreateView, self).get_context_data(**kwargs) 
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		return context

class journalUpdateView(ProductExistsRequiredMixin,LoginRequiredMixin,UpdateView):
	model = journal
	form_class  = journalForm

	def get_success_url(self,**kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk1'])
		journal_details = get_object_or_404(journal, pk=self.kwargs['pk2'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		return reverse('accounting_double_entry:detail', kwargs={'pk1':company_details.pk, 'pk2':journal_details.pk, 'pk3':selectdatefield_details.pk})

	def get_object(self):
		pk1 = self.kwargs['pk1']
		pk2 = self.kwargs['pk2']
		get_object_or_404(company, pk=pk1)
		Journal = get_object_or_404(journal, pk=pk2)
		return Journal

	def get_form_kwargs(self):
		data = super(journalUpdateView, self).get_form_kwargs()
		data.update(
			User=self.request.user,
			Company=company.objects.get(pk=self.kwargs['pk1'])
			)
		return data


	def get_context_data(self, **kwargs):
		context = super(journalUpdateView, self).get_context_data(**kwargs) 
		company_details = get_object_or_404(company, pk=self.kwargs['pk1'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		return context

@login_required
@product_1_activation
def journal_delete_view(request, pk, pk2, pk3):
	data = dict()
	company_details = get_object_or_404(company, pk=pk)
	journals = get_object_or_404(journal, pk=pk2)
	selectdatefield_details = get_object_or_404(selectdatefield, pk=pk3)

	if request.method == "POST":
		journals.delete()
		data['form_is_valid'] = True
		journal_list = journal.objects.filter(User= request.user, Company=company_details.pk, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).order_by('-id')
		context = {
			'journal_list':journal_list,
			'company_details' : company_details,
			'selectdatefield_details' : selectdatefield_details,
		}
		data['journals_list'] = render_to_string('accounting_double_entry/journal_list_2.html',context)
	else:
		context = {
			'journals':journals,
			'company_details' : company_details,
			'selectdatefield_details' : selectdatefield_details,
		}
		data['html_form'] = render_to_string('accounting_double_entry/journal_confirm_delete.html',context,request=request)

	return JsonResponse(data)



################## Views For P&L Journal ###################################

@login_required
@product_1_activation
def pl_journal_detail(request, pk1, pk2, pk3):
	company_details = get_object_or_404(company, pk=pk1)
	pl_details = get_object_or_404(Pl_journal, pk=pk2)
	selectdatefield_details = get_object_or_404(selectdatefield, pk=pk3)

	inbox = Message.objects.filter(reciever=request.user)
	inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
	send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

	context = {
		'pl_details'          	   : pl_details,
		'company_details'          : company_details,
		'inbox'					   : inbox,
		'inbox_count'			   : inbox_count,
		'send_count'			   : send_count,
		'selectdatefield_details'  : selectdatefield_details,
		'Todos'					   : Todo.objects.filter(User=request.user, complete=False),
		'Todos_total'			   : Todo.objects.filter(User=request.user, complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
	}
	return render(request, 'P&L/pl_details.html', context)



class pl_journalUpdateView(ProductExistsRequiredMixin,LoginRequiredMixin,UpdateView):
	model = Pl_journal
	form_class  = pl_journalForm
	template_name = 'P&L/pl_journal_form.html'

	def get_success_url(self,**kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk1'])
		pl_journals = get_object_or_404(Pl_journal, pk=self.kwargs['pk2'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		return reverse('accounting_double_entry:pl_detail', kwargs={'pk1':company_details.pk, 'pk2':pl_journals.pk, 'pk3':selectdatefield_details.pk})

	def get_object(self):
		pk1 = self.kwargs['pk1']
		pk2 = self.kwargs['pk2']
		get_object_or_404(company, pk=pk1)
		pl_journal = get_object_or_404(Pl_journal, pk=pk2)
		return pl_journal

	def get_form_kwargs(self):
		data = super(pl_journalUpdateView, self).get_form_kwargs()
		data.update(
			User=self.request.user,
			Company=company.objects.get(pk=self.kwargs['pk1'])
			)
		return data


	def get_context_data(self, **kwargs):
		context = super(pl_journalUpdateView, self).get_context_data(**kwargs) 
		company_details = get_object_or_404(company, pk=self.kwargs['pk1'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		return context

@login_required
@product_1_activation
def pl_journal_delete_view(request, pk, pk2, pk3):
	data = dict()
	company_details = get_object_or_404(company, pk=pk)
	pl_journal_details = get_object_or_404(Pl_journal, pk=pk2)
	selectdatefield_details = get_object_or_404(selectdatefield, pk=pk3)

	if request.method == "POST":
		pl_journal_details.delete()
		data['form_is_valid'] = True
		pl_journals = Pl_journal.objects.filter(User= request.user, Company=company_details.pk, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).order_by('-id')
		context = {
			'pl_journals':pl_journals,
			'company_details' : company_details,
			'selectdatefield_details' : selectdatefield_details,
		}
		data['pl_journals_list'] = render_to_string('accounting_double_entry/journal_list_2.html',context)
	else:
		context = {
			'pl_journal_details': pl_journal_details,
			'company_details' : company_details,
			'selectdatefield_details' : selectdatefield_details,
		}
		data['html_form'] = render_to_string('P&L/pl_journal_confirm_delete.html',context,request=request)

	return JsonResponse(data)


################## Views For Multijournal ###################################


class Multijournal_listview(ProductExistsRequiredMixin,LoginRequiredMixin,ListView):
	model = Multijournaltotal
	template_name = 'Multijournal/multi_journal_list.html'
	paginate_by = 15


	def get_queryset(self):
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		return self.model.objects.filter(Company=self.kwargs['pk'], Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).order_by('-id')

	def get_context_data(self, **kwargs):
		context = super(Multijournal_listview, self).get_context_data(**kwargs) 
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		return context

@product_1_activation
def multijournal_detail(request, pk, pk2, pk3):
	company_details = get_object_or_404(company, pk=pk)
	multijournal_details = get_object_or_404(Multijournaltotal, pk=pk2)
	selectdatefield_details = get_object_or_404(selectdatefield, pk=pk3)
	Multijournals = Multijournal.objects.filter(total=multijournal_details.pk)

	inbox = Message.objects.filter(reciever=request.user)
	inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
	send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']



	context = {

		'multijournal_details'     	: multijournal_details,
		'company_details'          	: company_details,
		'selectdatefield_details'  	: selectdatefield_details,
		'inbox'					  	: inbox,
		'inbox_count'			 	: inbox_count,
		'send_count'				: send_count,
		'Multijournals'            	: Multijournals,
		'Todos'					  	: Todo.objects.filter(User=request.user, complete=False),
		'Todos_total' 			  	: Todo.objects.filter(User=request.user, complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
	}
	return render(request, 'Multijournal/multi_journal_details.html', context)


class Multijournal_createview(ProductExistsRequiredMixin,LoginRequiredMixin,CreateView):
	form_class  = MultijournaltotalForm
	template_name = 'Multijournal/multi_journal_form.html'


	def get_success_url(self,**kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		return reverse('accounting_double_entry:multijournallist', kwargs={'pk':company_details.pk, 'pk3':selectdatefield_details.pk})

	def get_context_data(self, **kwargs):
		context = super(Multijournal_createview, self).get_context_data(**kwargs) 
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		if self.request.POST:
			context['multijournalformset'] = Multijournal_formSet(self.request.POST, form_kwargs = {'Company': company_details.pk})
		else:
			context['multijournalformset'] = Multijournal_formSet(form_kwargs = {'Company': company_details.pk})
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		return context

	def form_valid(self, form):
		form.instance.User = self.request.user
		c = company.objects.get(pk=self.kwargs['pk'])
		form.instance.Company = c
		context = self.get_context_data()
		multijournalformset = context['multijournalformset']
		with transaction.atomic():
			self.object = form.save()
			if multijournalformset.is_valid():
				multijournalformset.instance = self.object
				multijournalformset.save()
		return super(Multijournal_createview, self).form_valid(form)

	def get_form_kwargs(self):
		data = super(Multijournal_createview, self).get_form_kwargs()
		data.update(
			Company=company.objects.get(pk=self.kwargs['pk'])
			)
		return data



class Multijournal_updateview(ProductExistsRequiredMixin,LoginRequiredMixin,UpdateView):
	model = Multijournaltotal
	form_class  = MultijournaltotalForm
	template_name = 'Multijournal/multi_journal_form.html'


	def get_success_url(self,**kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		multijournal_details = get_object_or_404(Multijournaltotal, pk=self.kwargs['pk2'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		return reverse('accounting_double_entry:multijournaldetail', kwargs={'pk':company_details.pk, 'pk2':multijournal_details.pk,'pk3':selectdatefield_details.pk})

	def get_object(self):
		pk1 = self.kwargs['pk']
		pk2 = self.kwargs['pk2']
		get_object_or_404(company, pk=pk1)
		multijournaltotal = get_object_or_404(Multijournaltotal, pk=pk2)
		return multijournaltotal

	def get_context_data(self, **kwargs):
		context = super(Multijournal_updateview, self).get_context_data(**kwargs) 
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		multijournal_details = get_object_or_404(Multijournaltotal, pk=self.kwargs['pk2'])
		total = Multijournaltotal.objects.get(pk=multijournal_details.pk)
		if self.request.POST:
			context['multijournalformset'] = Multijournal_formSet(self.request.POST, instance=total, form_kwargs = {'Company': company_details.pk})
		else:
			context['multijournalformset'] = Multijournal_formSet(instance=total,form_kwargs = {'Company': company_details.pk})
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		return context

	def form_valid(self, form):
		form.instance.User = self.request.user
		c = company.objects.get(pk=self.kwargs['pk']) 
		form.instance.Company = c
		context = self.get_context_data()
		multijournalformset = context['multijournalformset']
		with transaction.atomic():
			self.object = form.save()
			if multijournalformset.is_valid():
				multijournalformset.instance = self.object
				multijournalformset.save()
		return super(Multijournal_updateview, self).form_valid(form)


# @login_required
# def Multijournal_updateview(request,pk,pk2,pk3):
# 	company_details = get_object_or_404(company, pk=pk)
# 	selectdatefield_details = get_object_or_404(selectdatefield, pk=pk3)
# 	multijournal_details = get_object_or_404(Multijournaltotal, pk=pk2)

# 	total = Multijournal.objects.filter(total=multijournal_details.pk)
# 	Multijournal_formSet = inlineformset_factory(Multijournaltotal, Multijournal,form=MultijournalForm, extra=6)

# 	if request.method == "POST":
# 		multijournalformset = Multijournal_formSet(request.POST or None, instance=total)

# 		if multijournalformset.is_valid():
# 			instances = multijournalformset.save(commit=False)
# 			for instance in instances:
# 				m = Multijournaltotal.objects.get(total=multijournal_details.pk)
# 				instance.total = m
# 				instance.save()
# 				return HttpResponseRedirect(total.get_absolute_url())

# 	else:
# 		multijournalformset = Multijournal_formSet()

# 	context = {

# 		'company_details' 		  : company_details,
# 		'selectdatefield_details' : selectdatefield_details,
# 		'multijournal_details'	  : multijournal_details,
# 		'multijournalformset'	  : multijournalformset
# 	}

# 	return render(request, 'Multijournal/multi_journal_form.html', context)

class multijournal_deleteview(ProductExistsRequiredMixin,LoginRequiredMixin,DeleteView):
	model = Multijournaltotal
	template_name = 'Multijournal/multijournal_delete.html'

	def get_success_url(self,**kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		return reverse('accounting_double_entry:multijournallist', kwargs={'pk':company_details.pk, 'pk3':selectdatefield_details.pk})

	def get_object(self):
		pk1 = self.kwargs['pk']
		pk2 = self.kwargs['pk2']
		get_object_or_404(company, pk=pk1)
		multijournal = get_object_or_404(Multijournaltotal, pk=pk2)
		return multijournal

	def get_context_data(self, **kwargs):
		context = super(multijournal_deleteview, self).get_context_data(**kwargs) 
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		multijournal_details = get_object_or_404(Multijournaltotal, pk=self.kwargs['pk2'])
		context['multijournal_details'] = multijournal_details	
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		return context	


################## Views For Multiplae Journal objects ###################################	

class Multiplae_Journal_objectsCreateView(ProductExistsRequiredMixin,LoginRequiredMixin,CreateView):
	form_class  = Multijournal
	template_name = 'Multijournal/multi_journal_form.html'

	def get_success_url(self,**kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		return reverse('accounting_double_entry:multijournallist', kwargs={'pk':company_details.pk, 'pk3':selectdatefield_details.pk})


	def get_form_kwargs(self):
		data = super(Multiplae_Journal_objectsCreateView, self).get_form_kwargs()
		data.update(
			User=self.request.user,
			Company=company.objects.get(pk=self.kwargs['pk'])
			)
		return data


	def get_context_data(self, **kwargs):
		context = super(Multiplae_Journal_objectsCreateView, self).get_context_data(**kwargs) 
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		return context



################## Views For Daterange Display ###################################

def save_all(request,form,template_name):
	data = dict()
	if request.method == 'POST':
		if form.is_valid():
			form.save()
			data['form_is_valid'] = True
			selectdatefield_details = selectdatefield.objects.filter(User=request.user)
			data['selectdatefields_list'] = render_to_string('company/company_list_2.html',{'selectdatefield_details':selectdatefield_details})
		else:
			data['form_is_valid'] = False
	context = {
	'form':form
	}
	data['html_form'] = render_to_string(template_name,context,request=request)
	return JsonResponse(data)

@csrf_exempt
def selectdate_create(request):
	if request.method == 'POST':
		form = DateRangeForm(request.POST)
		if form.is_valid():
			form.instance.User = request.user
			form.save()
	else:
		form = DateRangeForm()
	return save_all(request,form,"company/selectdate_create.html")

@csrf_exempt
def selectdate_update(request,pk):
	selectdatefield_details = get_object_or_404(selectdatefield, pk=pk)
	if request.method == 'POST':
		form = DateRangeForm(request.POST,instance=selectdatefield_details)
	else:
		form = DateRangeForm(instance=selectdatefield_details)

	return save_all(request,form,'company/selectdate_update.html')



################## Views For Payment ###################################

class Payment_createview(ProductExistsRequiredMixin,LoginRequiredMixin,CreateView):
	form_class  = PaymentForm
	success_message = "%(account)s is submitted successfully"
	template_name = 'Payments/payment_form.html'


	def get_success_url(self,**kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		return reverse('accounting_double_entry:paymentcreate', kwargs={'pk':company_details.pk, 'pk3':selectdatefield_details.pk})

	def get_context_data(self, **kwargs):
		context = super(Payment_createview, self).get_context_data(**kwargs) 
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		if self.request.POST:
			context['payments'] = Payment_formSet(self.request.POST, form_kwargs = {'Company': company_details.pk})
		else:
			context['payments'] = Payment_formSet(form_kwargs = {'Company': company_details.pk})
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['successful_submit'] = True
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		return context

	def form_valid(self, form):
		form.instance.User = self.request.user
		c = company.objects.get(pk=self.kwargs['pk'])
		form.instance.Company = c
		counter = Payment.objects.filter(User=self.request.user, Company=c).count() + 1
		form.instance.counter = counter
		context = self.get_context_data()
		payments = context['payments']
		with transaction.atomic():
			self.object = form.save()
			if payments.is_valid():
				payments.instance = self.object
				payments.save()
		return super(Payment_createview, self).form_valid(form)

	def get_form_kwargs(self):
		data = super(Payment_createview, self).get_form_kwargs()
		data.update(
			User=self.request.user,
			Company=company.objects.get(pk=self.kwargs['pk'])
			)
		return data

class ParticularspaymentCreateView(ProductExistsRequiredMixin,LoginRequiredMixin,CreateView):
	form_class  = ParticularspaymentForm
	template_name = 'Payments/payment_form.html'

	def get_success_url(self,**kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		return reverse('accounting_double_entry:paymentcreate', kwargs={'pk':company_details.pk, 'pk3':selectdatefield_details.pk})


	def get_form_kwargs(self):
		data = super(ParticularspaymentCreateView, self).get_form_kwargs()
		data.update(
			User=self.request.user,
			Company=company.objects.get(pk=self.kwargs['pk'])
			)
		return data


	def get_context_data(self, **kwargs):
		context = super(ParticularspaymentCreateView, self).get_context_data(**kwargs) 
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		return context


################## Views For Receipt ###################################

class Receipt_createview(ProductExistsRequiredMixin,LoginRequiredMixin,CreateView):
	form_class  = ReceiptForm
	success_message = "%(account)s is submitted successfully"
	template_name = 'Receipt/receipt_form.html'


	def get_success_url(self,**kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		return reverse('accounting_double_entry:receiptcreate', kwargs={'pk':company_details.pk, 'pk3':selectdatefield_details.pk})

	def get_context_data(self, **kwargs):
		context = super(Receipt_createview, self).get_context_data(**kwargs) 
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		if self.request.POST:
			context['receipts'] = Receipt_formSet(self.request.POST, form_kwargs = {'Company': company_details.pk})
		else:
			context['receipts'] = Receipt_formSet(form_kwargs = {'Company': company_details.pk})
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		return context

	def form_valid(self, form):
		form.instance.User = self.request.user
		c = company.objects.get(pk=self.kwargs['pk'])
		form.instance.Company = c
		counter = Receipt.objects.filter(User=self.request.user, Company=c).count() + 1
		form.instance.counter = counter
		context = self.get_context_data()
		receipts = context['receipts']
		with transaction.atomic():
			self.object = form.save()
			if receipts.is_valid():
				receipts.instance = self.object
				receipts.save()
		return super(Receipt_createview, self).form_valid(form)

	def get_form_kwargs(self):
		data = super(Receipt_createview, self).get_form_kwargs()
		data.update(
			User=self.request.user,
			Company=company.objects.get(pk=self.kwargs['pk'])
			)
		return data

class ParticularspayreceiptCreateView(ProductExistsRequiredMixin,LoginRequiredMixin,CreateView):
	form_class  = ParticularsreceiptForm
	template_name = 'Receipt/receipt_form.html'

	def get_success_url(self,**kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		return reverse('accounting_double_entry:receiptcreate', kwargs={'pk':company_details.pk, 'pk3':selectdatefield_details.pk})


	def get_form_kwargs(self):
		data = super(ParticularspayreceiptCreateView, self).get_form_kwargs()
		data.update(
			User=self.request.user,
			Company=company.objects.get(pk=self.kwargs['pk'])
			)
		return data


	def get_context_data(self, **kwargs):
		context = super(ParticularspayreceiptCreateView, self).get_context_data(**kwargs) 
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		return context

################## Views For Contra ###################################

class Contra_createview(ProductExistsRequiredMixin,LoginRequiredMixin,CreateView):
	form_class  = ContraForm
	success_message = "%(account)s is submitted successfully"
	template_name = 'Contra/contra_form.html'


	def get_success_url(self,**kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		return reverse('accounting_double_entry:contracreate', kwargs={'pk':company_details.pk, 'pk3':selectdatefield_details.pk})

	def get_context_data(self, **kwargs):
		context = super(Contra_createview, self).get_context_data(**kwargs) 
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		if self.request.POST:
			context['contras'] = Contra_formSet(self.request.POST, form_kwargs = {'Company': company_details.pk})
		else:
			context['contras'] = Contra_formSet(form_kwargs = {'Company': company_details.pk})
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		return context

	def form_valid(self, form):
		form.instance.User = self.request.user
		c = company.objects.get(pk=self.kwargs['pk'])
		form.instance.Company = c
		counter = Contra.objects.filter(User=self.request.user, Company=c).count() + 1
		form.instance.counter = counter
		context = self.get_context_data()
		contras = context['contras']
		with transaction.atomic():
			self.object = form.save()
			if contras.is_valid():
				contras.instance = self.object
				contras.save()
		return super(Contra_createview, self).form_valid(form)

	def get_form_kwargs(self):
		data = super(Contra_createview, self).get_form_kwargs()
		data.update(
			User=self.request.user,
			Company=company.objects.get(pk=self.kwargs['pk'])
			)
		return data

class ParticularspaycontraCreateView(ProductExistsRequiredMixin,LoginRequiredMixin,CreateView):
	form_class  = ParticularscontraForm
	template_name = 'Contra/contra_form.html'

	def get_success_url(self,**kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		return reverse('accounting_double_entry:contracreate', kwargs={'pk':company_details.pk, 'pk3':selectdatefield_details.pk})


	def get_form_kwargs(self):
		data = super(ParticularspaycontraCreateView, self).get_form_kwargs()
		data.update(
			User=self.request.user,
			Company=company.objects.get(pk=self.kwargs['pk'])
			)
		return data


	def get_context_data(self, **kwargs):
		context = super(ParticularspaycontraCreateView, self).get_context_data(**kwargs) 
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		return context

################## Views For Profit & Loss Display ###################################

@login_required
@product_1_activation
def profit_and_loss_condensed_view(request,pk,pk3):
	company_details = get_object_or_404(company, pk=pk)
	selectdatefield_details = get_object_or_404(selectdatefield, pk=pk3)

	# closing stock
	ldstckcb = stock_journal.objects.filter(Company=company_details.pk)
	qs2 = ldstckcb.aggregate(the_sum=Coalesce(Sum('closing_stock'), Value(0)))['the_sum']

	# opening stock
	ldstck = stock_journal.objects.filter(Company=company_details.pk)
	qo2 = ldstck.aggregate(the_sum=Coalesce(Sum('opening_stock'), Value(0)))['the_sum']

	# purchases #debit
	ld = group1.objects.filter(Company=company_details.pk, group_Name__icontains='Purchase Accounts')
	ldc = ld.aggregate(the_sum=Coalesce(Sum('ledgergroups__To_pl_debit'), Value(0)))['the_sum']

	# Direct Expense #debit
	ldd = group1.objects.filter(Company=company_details.pk, group_Name__icontains='Direct Expenses')
	lddt = ldd.aggregate(the_sum=Coalesce(Sum('ledgergroups__To_pl_debit'), Value(0)))['the_sum']

	# Direct Income #credit
	ldii = group1.objects.filter(Company=company_details.pk, group_Name__icontains='Direct Incomes')
	lddi = ldii.aggregate(the_sum=Coalesce(Sum('ledgergroups__To_pl_credit'), Value(0)))['the_sum']
	
	# sales #credit
	lds = group1.objects.filter(Company=company_details.pk, group_Name__icontains='Sales Account')
	ldsc = lds.aggregate(the_sum=Coalesce(Sum('ledgergroups__To_pl_credit'), Value(0)))['the_sum']

	#Indirect Expense  #debit
	lde = group1.objects.filter(Company=company_details.pk,group_Name__icontains='Indirect Expense')
	ldse = lde.aggregate(the_sum=Coalesce(Sum('ledgergroups__To_pl_debit'), Value(0)))['the_sum']
	ldsecr = lde.aggregate(the_sum=Coalesce(Sum('ledgergroups__To_pl_credit'), Value(0)))['the_sum']
	if ldse == 0 or ldse == None:
		total = - ldsecr 
	elif ldsecr == 0 or ldsecr == None:
		total = ldse
	else:
		total = ldse - ldsecr

	#Indirect Income #credit
	ldi = group1.objects.filter(Company=company_details.pk, group_Name__icontains='Indirect Income')
	ldsi = ldi.aggregate(the_sum=Coalesce(Sum('ledgergroups__To_pl_credit'), Value(0)))['the_sum']
	# qo1 means opening stock exists

	# lddt = Direct Expenses
	# lddi = Direct Incomes
	# ldc = Purchase Accounts
	# ldsc = Sales Account
	# qs2 = closing stock
	# qo2 = opening stock


	# gross profit/loss calculation
	if  lddi < 0 and lddt < 0:
		gp = abs(ldsc) + abs(qs2) + abs(lddt) - abs(qo2) - abs(ldc) - abs(lddi)
	elif lddt < 0:
		gp = abs(ldsc) + abs(qs2) + abs(lddi) + abs(lddt) - abs(qo2) - abs(ldc)
	elif lddi < 0:
		gp = abs(ldsc) + abs(qs2) - abs(lddi) - abs(qo2) - abs(ldc) - abs(lddt)
	else:	
		gp = abs(ldsc) + abs(qs2) + abs(lddi) - abs(qo2) - abs(ldc) - abs(lddt)


	# Trading profil/loss calculation
	if gp >=0:
		if  lddi < 0 and lddt < 0:
			tradingp  =  abs(qo2) + abs(ldc) + (gp) + abs(lddi)
			tgp = abs(qs2) + abs(ldsc) + abs(lddt) 
		elif lddt < 0:
			tradingp  =  abs(qo2) + abs(ldc) + (gp)
			tgp = abs(qs2) + abs(lddi) + abs(ldsc) + abs(lddt)
		elif lddi < 0:
			tradingp  =  abs(qo2) + abs(ldc) + abs(lddt) + (gp) + abs(lddi)
			tgp = abs(qs2) + abs(ldsc)
 						
		else:
			tradingp  =  abs(qo2) + abs(ldc) + abs(lddt) + (gp)
			tgp = abs(qs2) + abs(lddi) + abs(ldsc) 

	else: # gp <0
		if  lddi < 0 and lddt < 0:
			tradingp =  abs(qo2) + abs(ldc) + abs(lddi) 
			tgp = abs(qs2) + abs(ldsc) + abs(gp) + abs(lddt)
		elif lddt < 0:
			tradingp =  abs(qo2) + abs(ldc) 
			tgp = abs(qs2) + abs(lddi) + abs(ldsc) + abs(gp) + abs(lddt)
		elif lddi < 0:
			tradingp =  abs(qo2) + abs(ldc) + abs(lddt) + abs(lddi) 
			tgp = abs(qs2) + abs(ldsc) + abs(gp) 	
  					
		else:
			tradingp =  abs(qo2) + abs(ldc) + abs(lddt) 
			tgp = abs(qs2) + abs(lddi) + abs(ldsc) + abs(gp) 

	
	# total = Indirect Expense
	# ldsi = Indirect Income

	# nett profit/loss calculation
	if gp >=0:
		if ldsi < 0 and total < 0:
			np = (gp) + abs(total) - abs(ldsi)
		elif total < 0:
			np = (gp) + abs(ldsi) + abs(total)
		elif ldsi < 0:
			np = (gp) - abs(ldsi) - abs(total)
		else:
			np = (gp) + abs(ldsi) - abs(total)
	else:
		if ldsi < 0 and total < 0:
			np = abs(total) - abs(ldsi) - abs(gp) 
		elif ldsi < 0:
			np = abs(ldsi) + abs(total) + abs(gp)
		elif total < 0:
			np = abs(ldsi) + abs(total) - abs(gp)
		else:
			np = abs(ldsi) - abs(total) - abs(gp) 


	# total = Indirect Expense
	# ldsi = Indirect Income
 

	# Total value calculation
	if gp >= 0:
		if np >= 0:
			if ldsi < 0 and total < 0:
				tp = abs(ldsi) + np
				tc = abs(total) + (gp)
			elif ldsi < 0:
				tp = abs(ldsi) + np + abs(total)  
				tc = (gp) 
			elif total < 0:
				tp = np
				tc = abs(ldsi) + (gp) + abs(total)			
			else:
				tp = abs(total) + np 
				tc = abs(ldsi) + (gp) 
		else:
			if ldsi < 0 and total < 0:
				tp = abs(ldsi)  
				tc = gp + np + abs(total) 
			elif ldsi < 0:
				tp = abs(total)  + abs(ldsi)   
				tc = gp + np 
			elif total < 0:
				tp =  0
				tc = gp + np + abs(ldsi) + abs(total) 																								
			else:
				tp = abs(total)  
				tc = gp + np + abs(ldsi) 
	else: # gp<0
		if np >= 0:
			if ldsi < 0 and total < 0:
				tp = abs(ldsi) + np + abs(gp) 
				tc = abs(total) 
			elif ldsi < 0:
				tp = abs(total) + np + abs(gp) + abs(ldsi)  
				tc = 0	
			elif total < 0:
				tp = np + abs(gp) 
				tc = abs(ldsi) + abs(total) 							
			else:
				tp = abs(total) + np + abs(gp)  
				tc = abs(ldsi)  
		else:
			if ldsi < 0 and total < 0:
				tp = abs(ldsi) + abs(gp)  
				tc = abs(np) + abs(total) 
			elif ldsi < 0:
				tp = abs(total) + abs(gp) + abs(ldsi)  
				tc = abs(np) 
			elif total < 0:
				tp = abs(gp)  
				tc = abs(np) + abs(ldsi) + abs(total) 				
			else:
				tp = abs(total) + abs(gp)  
				tc = abs(np) + abs(ldsi) 

	# company_detail = company.objects.get(pk=company_details.pk)
	# company_detail.pl = abs(np)
	# company_detail.save(update_fields=['pl'])

	inbox = Message.objects.filter(reciever=request.user)
	inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
	send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

	context = {

		'company_details' : company_details,
		'selectdatefield_details' : selectdatefield_details,
		'closing_stock_items' : ldstckcb,
		'closing_stock' : qs2,
		# 'each_closing_stock' : qs1.values(),
		'opening_stock': qo2,
		'opening_stock_items' : ldstck,
		# 'each_opening_stock' : qo1.values(),
		'purchase_ledger' : ld,
		'total_purchase_ledger' : ldc,
		# 'specific_purchase_total' : ldsp,
		'sales_ledger' : lds,
		'total_sales_ledger' : ldsc,
		'indirectexp_group' : lde,
		'total_indirectexp_ledger' : total,
		'indirectinc_group' : ldi,
		'total_indirectinc_ledger' : ldsi,
		'total_direct_expenses': lddt,
		'direct_expenses_group': ldd,
		'total_direct_incomes': lddi,
		'direct_incomes': ldii,
		'gross_profit' : gp,
		'nett_profit' : np,
		'tradingprofit': tradingp,
		'tradingprofit2': tgp,
		'totalpl' : tp,
		'totalplright' : tc,
		'inbox'			: inbox,
		'inbox_count'	: inbox_count,
		'send_count'	: send_count,
		'Todos'					  : Todo.objects.filter(User=request.user, complete=False),
		'Todos_total' 			  : Todo.objects.filter(User=request.user, complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
	}

	return render(request, 'accounting_double_entry/P&Lcondnsd.html', context)








################## Views For Trial Balance Display ###################################

@login_required
@product_1_activation
def trial_balance_condensed_view(request,pk,pk3):
	company_details = get_object_or_404(company, pk=pk)
	selectdatefield_details = get_object_or_404(selectdatefield, pk=pk3)

	# opening stock
	ldstck = stock_journal.objects.filter(Company=company_details.pk)
	qo2 = ldstck.aggregate(the_sum=Coalesce(Sum('opening_stock'), Value(0)))['the_sum']

	grp_debit = group1.objects.filter(Company=company_details.pk,Master__group_Name__icontains='Primary',balance_nature__icontains='Debit')
	grp_credit = group1.objects.filter(Company=company_details.pk,Master__group_Name__icontains='Primary',balance_nature__icontains='Credit')

	grp_debit_co = group1.objects.filter(Company=company_details.pk,Master__group_Name__icontains='Primary',balance_nature__icontains='Debit')
	grp_credit_co = group1.objects.filter(Company=company_details.pk,Master__group_Name__icontains='Primary',balance_nature__icontains='Credit')

	
	gs_debit_open = grp_debit.aggregate(the_sum=Coalesce(Sum('positive_opening'), Value(0)))['the_sum']
	gs_credit_op = grp_credit.aggregate(the_sum=Coalesce(Sum('negative_opening'), Value(0)))['the_sum']

	#Net profit/loss opening balance
	ledger_pl = ledger1.objects.get(Company=company_details.pk,name__icontains="Profit & Loss A/c")
	ledger_pl_closing = ledger_pl.Balance_opening

	gs_credit_open = gs_credit_op + ledger_pl_closing


	print(gs_credit_open)

	if qo2 > 0:
		gs_debit_opening = gs_debit_open + qo2
		gs_credit_opening = gs_credit_open 
	else:
		gs_debit_opening = gs_debit_open
		gs_credit_opening = gs_credit_open + qo2


	gs_debit_opening_co = grp_debit_co.aggregate(the_sum=Coalesce(Sum('positive_opening'), Value(0)))['the_sum']
	gs_credit_opening_co = grp_credit_co.aggregate(the_sum=Coalesce(Sum('negative_opening'), Value(0)))['the_sum']
	print(gs_credit_opening_co)

	gs_opening = group1.objects.filter(Company=company_details.pk,Master__group_Name__icontains='Primary')

	gs_deb_opening = gs_opening.aggregate(the_sum=Coalesce(Sum('positive_opening'), Value(0)))['the_sum']
	gs_cre_opening = gs_opening.aggregate(the_sum=Coalesce(Sum('negative_opening'), Value(0)))['the_sum']





	if gs_debit_opening > gs_credit_opening:
		dif_ob = gs_debit_opening - gs_credit_opening
		total_deb = gs_debit_opening
		total_ceb = gs_credit_opening + abs(dif_ob)
	else:
		dif_ob = gs_credit_opening - gs_debit_opening
		total_deb = gs_debit_opening + abs(dif_ob)
		total_ceb = gs_credit_opening 

	print(gs_debit_opening)
	print(gs_credit_opening)
	print(dif_ob)




	gs = group1.objects.filter(Company=company_details.pk,Master__group_Name__icontains='Primary').exclude(Q(group_Name__icontains="Stock-in-hand") | Q(group_Name__icontains="Sales Account") | Q(group_Name__icontains="Purchase Accounts") | Q(group_Name__icontains="Indirect Expense") | Q(group_Name__icontains="Indirect Income") | Q(group_Name__icontains="Direct Incomes") | Q(group_Name__icontains="Direct Expenses"))



	gs_deb_notstock = gs.aggregate(the_sum=Coalesce(Sum('positive_closing'), Value(0)))['the_sum']
	gs_cre_notstock = gs.aggregate(the_sum=Coalesce(Sum('negative_closing'), Value(0)))['the_sum']

	if qo2 > 0:
		gs_deb = gs_deb_notstock + qo2
		gs_cre = gs_cre_notstock
	else:
		gs_deb = gs_deb_notstock 
		gs_cre = gs_cre_notstock + qo2

	# purchases
	gs_purchase = group1.objects.filter(Company=company_details.pk,group_Name__icontains="Purchase Accounts")
	gs_purchase_total = gs_purchase.aggregate(the_sum=Coalesce(Sum('ledgergroups__To_pl_debit'), Value(0)))['the_sum']

	# sales
	gs_sales = group1.objects.filter(Company=company_details.pk,group_Name__icontains="Sales Account")
	gs_sales_total = gs_sales.aggregate(the_sum=Coalesce(Sum('ledgergroups__To_pl_credit'), Value(0)))['the_sum']

	# Direct Expense
	gs_directexp = group1.objects.filter(Company=company_details.pk,group_Name__icontains="Direct Expenses")
	gs_directexp_total = gs_directexp.aggregate(the_sum=Coalesce(Sum('ledgergroups__To_pl_debit'), Value(0)))['the_sum']

	# Direct Income
	gs_directinc = group1.objects.filter(Company=company_details.pk,group_Name__icontains="Direct Incomes")
	gs_directinc_total = gs_directinc.aggregate(the_sum=Coalesce(Sum('ledgergroups__To_pl_credit'), Value(0)))['the_sum']

	# Indirect Expense
	gs_indirectexp = group1.objects.filter(Company=company_details.pk,group_Name__icontains="Indirect Expense")
	gs_indirectexp_total = gs_indirectexp.aggregate(the_sum=Coalesce(Sum('ledgergroups__To_pl_debit'), Value(0)))['the_sum']

	# Indirect Income
	gs_indirectinc = group1.objects.filter(Company=company_details.pk,group_Name__icontains="Indirect Income")
	gs_indirectinc_total = gs_indirectinc.aggregate(the_sum=Coalesce(Sum('ledgergroups__To_pl_credit'), Value(0)))['the_sum']

	#Net profit/loss
	ledger_pl = ledger1.objects.get(Company=company_details.pk,name__icontains="Profit & Loss A/c")
	ledger_pl_closing = ledger_pl.Balance_opening



	if ledger_pl_closing <= 0:
		gs_debit = gs_deb + abs(ledger_pl_closing) + gs_purchase_total + gs_directexp_total + gs_indirectexp_total
		gs_credit = gs_cre + gs_sales_total + gs_directinc_total + gs_indirectinc_total
	else:
		gs_debit = gs_deb + gs_purchase_total + gs_directexp_total + gs_indirectexp_total
		gs_credit = gs_cre + ledger_pl_closing + gs_sales_total + gs_directinc_total + gs_indirectinc_total


	if gs_debit > gs_credit:
		difference_ob = gs_debit_opening - gs_credit_opening
		total_credit = gs_credit + abs(difference_ob)
		total_debit = gs_debit
	else:
		difference_ob = gs_credit_opening - gs_debit_opening
		total_credit = gs_credit 
		total_debit = gs_debit + abs(difference_ob)


	inbox = Message.objects.filter(reciever=request.user)
	inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
	send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']


	context = {
		'company_details' 			: company_details,
		'selectdatefield_details' 	: selectdatefield_details,
		'qo2' 						: qo2,
		'gs_deb_opening' 			: gs_debit_opening,
		'gs_cre_opening'			: gs_credit_opening,
		'dif_ob' 					: dif_ob,
		'total_deb' 				: total_deb,
		'total_ceb'					: total_ceb,
		'groups_list' 				: gs,
		'ledger_pl'					: ledger_pl,
		'gs_purchase' 				: gs_purchase,
		'gs_purchase_total'			: gs_purchase_total,
		'gs_sales' 					: gs_sales,
		'gs_sales_total'			: gs_sales_total,
		'gs_directexp'				: gs_directexp,
		'gs_directexp_total'		: gs_directexp_total,
		'gs_directinc'				: gs_directinc,
		'gs_directinc_total'		: gs_directinc_total,
		'gs_indirectinc'			: gs_indirectinc,
		'gs_indirectinc_total'		: gs_indirectinc_total,
		'gs_indirectexp' 			: gs_indirectexp,
		'gs_indirectexp_total'		: gs_indirectexp_total,
		'ledger_pl_closing'			: ledger_pl_closing,
		'difference_ob' 			: difference_ob,
		'gs_debit' 					: gs_debit,
		'gs_credit'					: gs_credit,
		'total_debit' 				: total_debit,
		'total_credit' 				: total_credit,
		'inbox'						: inbox,
		'inbox_count'				: inbox_count,
		'send_count'				: send_count,
		'Todos'						: Todo.objects.filter(User=request.user, complete=False),
		'Todos_total' 				: Todo.objects.filter(User=request.user, complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
	}

	return render(request, 'accounting_double_entry/trial_bal_condendensed.html', context)



################## Views For Balance Sheet Display ###################################

@login_required
@product_1_activation
def balance_sheet_condensed_view(request,pk,pk3):
	company_details = get_object_or_404(company, pk=pk)
	selectdatefield_details = get_object_or_404(selectdatefield, pk=pk3)

	# All primary groups with nature of group is 'Liabilities'
	group_lia = group1.objects.filter(Company=company_details.pk,Master__group_Name__icontains='Primary',Nature_of_group1__icontains='Liabilities')
	
	# Getting the positive closing balances of all groups with nature of group is 'Liabilities'

	group_lia_clo = group_lia.annotate(
			closing_positive = Coalesce(Sum('positive_closing'), 0),
			closing_negative = Coalesce(Sum('negative_closing'), 0))

	# Closing balances of all groups with nature of group is 'Liabilities'
	lia_particular = group_lia_clo.annotate(
	    	difference = ExpressionWrapper(F('closing_negative') - F('closing_positive'), output_field=DecimalField()),
		)

	# Total of positive liabilities
	total_lia_positive = lia_particular.filter(difference__lt = 0).aggregate(the_sum=Coalesce(Sum('difference'), Value(0)))['the_sum']

	# Total of negative liabilities
	total_lia_negative = lia_particular.filter(difference__gte = 0).aggregate(the_sum=Coalesce(Sum('difference'), Value(0)))['the_sum']
	
	# closing stock
	ldstckcb = stock_journal.objects.filter(Company=company_details.pk)
	qs2 = ldstckcb.aggregate(the_sum=Coalesce(Sum('closing_stock'), Value(0)))['the_sum']


	
	# All primary groups with nature of group is 'Assets'
	group_ast = group1.objects.filter(Company=company_details.pk,Master__group_Name__icontains='Primary',Nature_of_group1__icontains='Assets')
	
	# Getting the positive closing balances of all groups with nature of group is 'Assets'

	group_ast_clo = group_ast.annotate(
			closing_positive = Coalesce(Sum('positive_closing'), 0),
			closing_negative = Coalesce(Sum('negative_closing'), 0))

	# Closing balances of all groups with nature of group is 'Assets'
	ast_particular = group_ast_clo.annotate(
	    	difference = ExpressionWrapper(F('closing_positive') - F('closing_negative'), output_field=DecimalField()),
		)

	# Total of positive Assets
	total_ast_positive = ast_particular.filter(difference__lt = 0).aggregate(the_sum=Coalesce(Sum('difference'), Value(0)))['the_sum']
	
	# Total of negative Assets
	total_ast_negative = ast_particular.filter(difference__gt = 0).aggregate(the_sum=Coalesce(Sum('difference'), Value(0)))['the_sum']

	
	# Current asset calculation
	ca_group = group1.objects.get(Company=company_details.pk,group_Name__icontains='Current Assets')
	total_ca = (ca_group.positive_closing - ca_group.negative_closing) + qs2

	#Net profit/loss
	ledger_pl = ledger1.objects.get(Company=company_details.pk,name__icontains="Profit & Loss A/c")

	# From Profit and Loss
	#################################################

	# opening stock
	ldstck = stock_journal.objects.filter(Company=company_details.pk)
	qo2 = ldstck.aggregate(the_sum=Coalesce(Sum('opening_stock'), Value(0)))['the_sum']

	# purchases #debit
	ld = group1.objects.filter(Company=company_details.pk, group_Name__icontains='Purchase Accounts')
	ldc = ld.aggregate(the_sum=Coalesce(Sum('ledgergroups__To_pl_debit'), Value(0)))['the_sum']

	# Direct Expense #debit
	ldd = group1.objects.filter(Company=company_details.pk, group_Name__icontains='Direct Expenses')
	lddt = ldd.aggregate(the_sum=Coalesce(Sum('ledgergroups__To_pl_debit'), Value(0)))['the_sum']

	# Direct Income #credit
	ldii = group1.objects.filter(Company=company_details.pk, group_Name__icontains='Direct Incomes')
	lddi = ldii.aggregate(the_sum=Coalesce(Sum('ledgergroups__To_pl_credit'), Value(0)))['the_sum']
	
	# sales #credit
	lds = group1.objects.filter(Company=company_details.pk, group_Name__icontains='Sales Account')
	ldsc = lds.aggregate(the_sum=Coalesce(Sum('ledgergroups__To_pl_credit'), Value(0)))['the_sum']

	#Indirect Expense  #debit
	lde = group1.objects.filter(Company=company_details.pk,group_Name__icontains='Indirect Expense')
	ldse = lde.aggregate(the_sum=Coalesce(Sum('ledgergroups__To_pl_debit'), Value(0)))['the_sum']
	ldsecr = lde.aggregate(the_sum=Coalesce(Sum('ledgergroups__To_pl_credit'), Value(0)))['the_sum']
	if ldse == 0 or ldse == None:
		total = - ldsecr 
	elif ldsecr == 0 or ldsecr == None:
		total = ldse
	else:
		total = ldse - ldsecr

	#Indirect Income #credit
	ldi = group1.objects.filter(Company=company_details.pk, group_Name__icontains='Indirect Income')
	ldsi = ldi.aggregate(the_sum=Coalesce(Sum('ledgergroups__To_pl_credit'), Value(0)))['the_sum']
	# qo1 means opening stock exists

	# lddt = Direct Expenses
	# lddi = Direct Incomes


	if  lddi < 0 and lddt < 0:
		gp = abs(ldsc) + abs(qs2) + abs(lddt) - abs(qo2) - abs(ldc) - abs(lddi)
	elif lddt < 0:
		gp = abs(ldsc) + abs(qs2) + abs(lddi) + abs(lddt) - abs(qo2) - abs(ldc)
	elif lddi < 0:
		gp = abs(ldsc) + abs(qs2) - abs(lddi) - abs(qo2) - abs(ldc) - abs(lddt)
	else:	
		gp = abs(ldsc) + abs(qs2) + abs(lddi) - abs(qo2) - abs(ldc) - abs(lddt)

	
	# total = Indirect Expense
	# ldsi = Indirect Income


	if gp >=0:
		if ldsi < 0 and total < 0:
			np = (gp) + abs(total) - abs(ldsi)
		elif total < 0:
			np = (gp) + abs(ldsi) + abs(total)
		elif ldsi < 0:
			np = (gp) - abs(ldsi) - abs(total)
		else:
			np = (gp) + abs(ldsi) - abs(total)
	else:
		if ldsi < 0 and total < 0:
			np = abs(total) - abs(ldsi) - abs(gp) 
		elif ldsi < 0:
			np = abs(ldsi) + abs(total) + abs(gp)
		elif total < 0:
			np = abs(ldsi) + abs(total) - abs(gp)
		else:
			np = abs(ldsi) - abs(total) - abs(gp) 

	#Net profit/loss opening balance
	ledger_pl = ledger1.objects.get(Company=company_details.pk,name__icontains="Profit & Loss A/c")
	ledger_pl_closing = ledger_pl.Balance_opening


	total_pl = np + ledger_pl_closing



	# From Trial Balance
	#################################################

	grp_debit = group1.objects.filter(Company=company_details.pk,Master__group_Name__icontains='Primary',balance_nature__icontains='Debit')
	grp_credit = group1.objects.filter(Company=company_details.pk,Master__group_Name__icontains='Primary',balance_nature__icontains='Credit')

	grp_debit_co = group1.objects.filter(Company=company_details.pk,Master__group_Name__icontains='Primary',balance_nature__icontains='Debit')
	grp_credit_co = group1.objects.filter(Company=company_details.pk,Master__group_Name__icontains='Primary',balance_nature__icontains='Credit')

	gs_debit_open = grp_debit.aggregate(the_sum=Coalesce(Sum('positive_opening'), Value(0)))['the_sum']
	gs_credit_op = grp_credit.aggregate(the_sum=Coalesce(Sum('negative_opening'), Value(0)))['the_sum']



	gs_credit_open = gs_credit_op + ledger_pl_closing


	if qo2 > 0:
		gs_debit_opening = gs_debit_open + qo2
	else:
		gs_debit_opening = gs_debit_open

	if qo2 > 0:
		gs_credit_opening = gs_credit_open 
	else:
		gs_credit_opening = gs_credit_open + qo2

	gs_debit_opening_co = grp_debit_co.aggregate(the_sum=Coalesce(Sum('positive_opening'), Value(0)))['the_sum']
	gs_credit_opening_co = grp_credit_co.aggregate(the_sum=Coalesce(Sum('negative_opening'), Value(0)))['the_sum']

	gs_opening = group1.objects.filter(Company=company_details.pk,Master__group_Name__icontains='Primary')

	gs_deb_opening = gs_opening.aggregate(the_sum=Coalesce(Sum('positive_opening'), Value(0)))['the_sum']
	gs_cre_opening = gs_opening.aggregate(the_sum=Coalesce(Sum('negative_opening'), Value(0)))['the_sum']




	if gs_debit_opening > gs_credit_opening:
		dif_ob = gs_debit_opening - gs_credit_opening
	else:
		dif_ob = gs_credit_opening - gs_debit_opening

	####################################### 


	# Balance sheet total of liabilities side
	if total_lia_positive or total_ast_negative:
		if total_ca < 0:
			if total_pl > 0:
				total_liabilities_1 = total_lia_positive + total_ast_negative + qs2 + total_pl
			else:
				total_liabilities_1 = total_lia_positive + total_ast_negative + qs2
		else:
			if total_pl > 0:
				total_liabilities_1 = total_lia_positive + total_ast_negative + total_pl
			else:
				total_liabilities_1 = total_lia_positive + total_ast_negative 

	# Balance sheet total of assets side
	if total_lia_negative or total_ast_positive:
		if total_ca > 0:
			if total_pl < 0:
				total_asset_1 = total_lia_negative + total_ast_positive + qs2 + total_pl
			else:
				total_asset_1 = total_lia_negative + total_ast_positive + qs2
		else:
			if total_pl < 0:
				total_asset_1 = total_lia_negative + total_ast_positive + total_pl
			else:
				total_asset_1 = total_lia_negative + total_ast_positive 

	if gs_debit_opening > gs_credit_opening:
		dif_ob = gs_debit_opening - gs_credit_opening
		total_liabilities = total_liabilities_1 + dif_ob
		total_asset = total_asset_1	
	else:
		dif_ob = gs_debit_opening - gs_credit_opening
		total_liabilities = total_liabilities_1 
		total_asset = total_asset_1	+ dif_ob


	inbox = Message.objects.filter(reciever=request.user)
	inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
	send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
	

	context = {

		'company_details' : company_details,
		'selectdatefield_details' : selectdatefield_details,

		'lia_particular' : lia_particular,
		'ast_particular' : ast_particular,
		'closing_stock' : qs2,
		'total_ca' 		: total_ca,

		'ledger_pl' 	: ledger_pl,

		'dif_ob' 			: dif_ob,
		'gs_debit_opening'	: gs_debit_opening,
		'gs_credit_opening' : gs_credit_opening,

		'np' 				: np,
		'total_pl' 			: total_pl,

		'total_asset' 		: total_asset,
		'total_liabilities' : total_liabilities,

		'inbox'			: inbox,
		'inbox_count'	: inbox_count,
		'send_count'	: send_count,

		'Todos'			: Todo.objects.filter(User=request.user, complete=False),
		'Todos_total' 	: Todo.objects.filter(User=request.user, complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 


	}

	return render(request, 'accounting_double_entry/balance_sheet.html', context)



@login_required
@product_1_activation
def cash_and_bank_view(request,pk,pk3):
	company_details = get_object_or_404(company, pk=pk)
	selectdatefield_details = get_object_or_404(selectdatefield, pk=pk3)

	# Cash Account
	cash_group = group1.objects.filter( Company=company_details.pk, group_Name__icontains='Cash-in-hand')
	cash_group_closing = cash_group.annotate(
				closing = Coalesce(Sum('ledgergroups__Closing_balance'), 0),
			)


	groups_ca_pos = cash_group.annotate(
				closing = Coalesce(Sum('ledgergroups__Closing_balance'), 0)
			).filter(closing__gt = 0)

	groups_ca_neg = cash_group.annotate(
				closing = Coalesce(Sum('ledgergroups__Closing_balance'), 0)
			).filter(closing__lte = 0)

	groups_ca_positive = groups_ca_pos.aggregate(the_sum=Coalesce(Sum('closing'), Value(0)))['the_sum']
	groups_ca_negative = groups_ca_neg.aggregate(the_sum=Coalesce(Sum('closing'), Value(0)))['the_sum']


	# Bank Account
	bank_group = group1.objects.filter(Company=company_details.pk, group_Name__icontains='Bank Accounts')
	bank_group_closing = bank_group.annotate(
				closing = Coalesce(Sum('ledgergroups__Closing_balance'), 0),
			)

	groups_ba_pos = bank_group.annotate(
				closing = Coalesce(Sum('ledgergroups__Closing_balance'), 0),
			).filter(closing__gt = 0)

	# groups_ba_neg = bank_group.annotate(
	# 			closing = Sum('ledgergroups__Closing_balance')
	# 		).filter(closing__lte = 0, closing = 0),

	groups_ba_positive = groups_ba_pos.aggregate(the_sum=Coalesce(Sum('closing'), Value(0)))['the_sum']
	# groups_ba_negative = groups_ba_neg.aggregate(the_sum1=Sum('closing'))['the_sum1']



	positive = groups_ca_positive + groups_ba_positive
	negative = groups_ca_negative 

	inbox = Message.objects.filter(reciever=request.user)
	inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
	send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']



	context = {
		'company_details' : company_details,
		'selectdatefield_details' : selectdatefield_details,

		'cash_group' : cash_group_closing,

		'bank_group' : bank_group_closing,

		'positive' : positive,
		'negative' : negative, 

		'inbox'			: inbox,
		'inbox_count'	: inbox_count,
		'send_count'	: send_count,

		'Todos'		   : Todo.objects.filter(User=request.user, complete=False),
		'Todos_total'  :Todo.objects.filter(User=request.user, complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] ,

	}

	return render(request, 'Cash_Bank/cash_and_bank.html', context)


################################################### Bank Reconcilation #################################################

class Bank_ledgerlistview(ProductExistsRequiredMixin,LoginRequiredMixin,ListView):
	model = ledger1
	template_name = 'Bank/bank_ledger_list.html'

	def get_queryset(self):
		return ledger1.objects.filter(Q(Company=self.kwargs['pk']) , Q(group1_Name__group_Name__icontains='Bank Accounts') | Q(group1_Name__Master__group_Name__icontains='Bank Accounts'))

	def get_context_data(self, **kwargs):
		context = super(Bank_ledgerlistview, self).get_context_data(**kwargs)
		context['ledger_list'] = ledger1.objects.filter(Q(Company=self.kwargs['pk']) , Q(group1_Name__group_Name__icontains='Bank Accounts') | Q(group1_Name__Master__group_Name__icontains='Bank Accounts'))
		context['profile_details'] = Profile.objects.all()
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		return context


@login_required
@product_1_activation
def Bank_ledger1_detail_view(request, pk, pk2, pk3):
	company_details = get_object_or_404(company, pk=pk)
	ledger1_details = get_object_or_404(ledger1, pk=pk2)
	selectdatefield_details = get_object_or_404(selectdatefield, pk=pk3)

	# opening balance

	qsob  = Bank_reconcilation.objects.filter(Company=company_details.pk, By=ledger1_details.pk, Date__lt=selectdatefield_details.Start_Date)
	qsob2 = Bank_reconcilation.objects.filter(Company=company_details.pk, To=ledger1_details.pk, Date__lt=selectdatefield_details.Start_Date)


	total_debitob = qsob.aggregate(the_sum=Coalesce(Sum('Debit'), Value(0)))['the_sum']
	total_creditob = qsob2.aggregate(the_sum=Coalesce(Sum('Credit'), Value(0)))['the_sum']

	if(ledger1_details.group1_Name.balance_nature == 'Debit'):
		opening_balance = abs(ledger1_details.Opening_Balance) + abs(total_debitob) - abs(total_creditob)
	else:
		opening_balance = abs(ledger1_details.Opening_Balance) + abs(total_creditob) - abs(total_debitob) 

	# closing balance
	qscb  = Bank_reconcilation.objects.filter(Company=company_details.pk, By=ledger1_details.pk, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).order_by('Date')
	qscb2 = Bank_reconcilation.objects.filter(Company=company_details.pk, To=ledger1_details.pk, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).order_by('Date')	
	new   = zip_longest(qscb,qscb2)


	total_debitcb = qscb.aggregate(the_sum=Coalesce(Sum('Debit'), Value(0)))['the_sum']
	total_creditcb = qscb2.aggregate(the_sum=Coalesce(Sum('Credit'), Value(0)))['the_sum']

	if (ledger1_details.name != 'Profit & Loss A/c'):
		if(ledger1_details.group1_Name.balance_nature == 'Debit'):
			closing_balance = opening_balance + abs(total_debitcb) - abs(total_creditcb) 
		else:
			closing_balance = opening_balance + abs(total_creditcb) - abs(total_debitcb)
	else:
		if(ledger1_details.group1_Name.balance_nature == 'Debit'):
			closing_balance = opening_balance + abs(total_debitcb) - abs(total_creditcb) 
		else:
			closing_balance = opening_balance + abs(total_creditcb) - abs(total_debitcb) 


	per_bank_balance = (abs(closing_balance) + abs(total_debitcb)) - total_creditcb

	qscb_bank  = Bank_reconcilation.objects.filter(Company=company_details.pk, By=ledger1_details.pk, bank_date=None, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).order_by('Date')
	qscb2_bank = Bank_reconcilation.objects.filter(Company=company_details.pk, To=ledger1_details.pk, bank_date=None, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).order_by('Date')	
	
	total_debit = qscb_bank.aggregate(the_sum=Coalesce(Sum('Debit'), Value(0)))['the_sum']
	total_credit = qscb2_bank.aggregate(the_sum=Coalesce(Sum('Credit'), Value(0)))['the_sum']

	per_bank_balance = (abs(closing_balance) + abs(total_debit)) - total_credit

	ledger1_detail = ledger1.objects.get(pk=ledger1_details.pk)
	ledger1_detail.Closing_balance = closing_balance
	ledger1_detail.Balance_opening = opening_balance
	ledger1_detail.save(update_fields=['Closing_balance', 'Balance_opening'])

	inbox = Message.objects.filter(reciever=request.user)
	inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
	send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

	context = {

		'company_details' 			: company_details,
		'ledger1_details' 			: ledger1_details,
		'selectdatefield_details' 	: selectdatefield_details,
		'total_debit'     			: abs(total_debit),
		'total_credit'    			: abs(total_credit),
		'per_bank_balance'			: per_bank_balance,
		'journal_debit'   			: qscb,
		'journal_credit'  			: qscb2,
		'n'				  			: new,
		'closing_balance' 			: closing_balance,
		'opening_balance' 			: opening_balance,		
		'company_list'    			: company.objects.all(),
		'inbox'					 	: inbox,
		'inbox_count'			  	: inbox_count,
		'send_count'				: send_count,
		'selectdate' 	  			: selectdatefield.objects.filter(User=request.user),
		'Todos'			  			: Todo.objects.filter(User=request.user, complete=False),
		'Todos_total' 	 			: Todo.objects.filter(User=request.user, complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 

				
	}	

	return render(request, 'Bank/bank_ledger_details.html', context)


@login_required
@product_1_activation
def bank_journal_detail(request, pk1, pk2, pk3):
	company_details = get_object_or_404(company, pk=pk1)
	journal_details = get_object_or_404(Bank_reconcilation, pk=pk2)
	selectdatefield_details = get_object_or_404(selectdatefield, pk=pk3)

	inbox = Message.objects.filter(reciever=request.user)
	inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
	send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

	context = {
		'journal_details'          : journal_details,
		'company_details'          : company_details,
		'inbox'					   : inbox,
		'inbox_count'			   : inbox_count,
		'send_count'			   : send_count,
		'selectdatefield_details'  : selectdatefield_details,
		'Todos'					   : Todo.objects.filter(User=request.user, complete=False),
		'Todos_total'			   : Todo.objects.filter(User=request.user, complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
	}
	return render(request, 'Bank/bank_details.html', context)



def save_all_bank(request,form,template_name):
	data = dict()
	if request.method == 'POST':
		if form.is_valid():
			form.save()
			data['form_is_valid'] = True
			bank_journal_list = Bank_reconcilation.objects.all().order_by('-id')
			data['bank_journal_list'] = render_to_string('Bank/bank_list_2.html',{'bank_journal_list':bank_journal_list})
		else:
			data['form_is_valid'] = False
	context = {

		'form':form,

	}
	data['html_form'] = render_to_string(template_name,context,request=request)

	return JsonResponse(data)

@login_required
@product_1_activation
def bank_journal_update(request,id):
	journal_details = get_object_or_404(Bank_reconcilation, id=id)

	if request.method == 'POST':
		form = bank_journalForm(request.POST,instance=journal_details)
	else:
		form = bank_journalForm(instance=journal_details)

	return save_all_bank(request,form,'Bank/bank_update.html')









