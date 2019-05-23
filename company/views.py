from django.shortcuts import render
from django.views.generic import (View,ListView,DetailView,
								  CreateView,UpdateView,DeleteView)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.signals import pre_save,post_save,post_delete
from django.urls import reverse_lazy
from django.views.generic.edit import FormMixin
from company.models import company
from ecommerce_integration.models import coupon, Product, Product_review, Services, API, Role_based_product
from userprofile.models import Profile, Product_activation, Role_product_activation
from messaging.models import Message
from company.forms import companyform,companyupdateform
from django.shortcuts import redirect
from todogst.models import Todo
from django.contrib.auth.decorators import login_required
from accounting_double_entry.models import selectdatefield
from accounting_double_entry.forms import DateRangeForm
from django.shortcuts import get_object_or_404
from django.urls import reverse
from accounting_double_entry.models import Pl_journal,journal,group1,ledger1,selectdatefield,Payment,Particularspayment,Receipt,Particularsreceipt,Contra,Particularscontra,Multijournal,Multijournaltotal
from stockkeeping.models import Stockgroup,Simpleunits,Compoundunits,Stockdata,Purchase,Sales,Stock_Total,Stock_Total_sales,stock_journal
from django.db.models.functions import Coalesce
from django.db.models import Case, When, Value, Sum, Count, F, Q, ExpressionWrapper, Subquery, OuterRef, FloatField
from django.db.models.fields import DecimalField
from django.db.models.functions import Coalesce 
from django.core.exceptions import PermissionDenied
import calendar
import dateutil
import collections
from stockkeeping.models import Sales
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect, JsonResponse
from blog.models import Blog,categories,Blog_comments
from consultancy.models import consultancy,Answer
from ecommerce_integration.decorators import product_1_activation
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import get_user_model
from itertools import zip_longest
import json
from django.core import serializers
from django.http import HttpResponse
from datetime import datetime
from dateutil import relativedelta
from tablib import Dataset
from .resources import CompanyResource
from django.core.management import call_command
from datetime import datetime,timedelta

User = get_user_model()
# Create your views here.

class ProductExistsRequiredMixin:

    def dispatch(self, request, *args, **kwargs):
        if Product_activation.objects.filter(User=self.request.user,product__id = 1, is_active=True) or Role_product_activation.objects.filter(User=request.user,product__id = 1, is_active=True):
            return super().dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

class NormalProductExistsRequiredMixin:

    def dispatch(self, request, *args, **kwargs):
        if Product_activation.objects.filter(User=self.request.user,product__id = 1, is_active=True) :
            return super().dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied



@login_required
@product_1_activation
def getcompanyObject(request, pk):
	company_details = get_object_or_404(company, pk=pk)
	all_objects = list(company.objects.filter(pk=pk)) + list(group1.objects.filter(Company=company_details.pk)) + list(ledger1.objects.filter(Company=company_details.pk)) + list(journal.objects.filter(Company=company_details.pk)) + list(Pl_journal.objects.filter(Company=company_details.pk)) + list(Payment.objects.filter(Company=company_details.pk)) + list(Receipt.objects.filter(Company=company_details.pk)) + list(Contra.objects.filter(Company=company_details.pk)) + list(Stockgroup.objects.filter(Company=company_details.pk)) + list(Simpleunits.objects.filter(Company=company_details.pk)) + list(Compoundunits.objects.filter(Company=company_details.pk)) + list(Stockdata.objects.filter(Company=company_details.pk)) + list(Purchase.objects.filter(Company=company_details.pk)) + list(Sales.objects.filter(Company=company_details.pk))
	data = serializers.serialize('json', all_objects)
	data = json.dumps(json.loads(data), indent=4)
	response = HttpResponse(data , content_type='application/json')
	response['Content-Disposition'] = 'attachment; filename={}-{}.json'.format(company_details.Name,datetime.now()) 
	return response

@login_required
def company_upload(request):
	if request.method == 'POST':
		new_company = request.FILES['myfile']

		obj_generator = serializers.json.Deserializer(new_company)
		
		for obj in obj_generator:
			obj.save()

	return render(request, 'company/import.html')

class companyListView(ProductExistsRequiredMixin,LoginRequiredMixin,ListView):
	model = company
	paginate_by = 10

	def get_queryset(self):
		return company.objects.filter(User=self.request.user).order_by('id')

	def get_context_data(self, **kwargs):
		context = super(companyListView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated:
			context['company_list'] = company.objects.filter(User=self.request.user).order_by('id')
		else:
			context['company_list'] = company.objects.none()
			
		context['selectdates'] = selectdatefield.objects.filter(User=self.request.user)
		
		if self.request.user.is_authenticated:
			context['Products_aggrement'] = Product_activation.objects.filter(User=self.request.user,product__id = 9, is_active=True)
			context['Products'] = Product_activation.objects.filter(User=self.request.user,product__id = 1, is_active=True)
			context['Role_products'] = Role_product_activation.objects.filter(User=self.request.user,product__id = 1, is_active=True)
			context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
			context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
			context['inbox'] = Message.objects.filter(reciever=self.request.user)
			context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
			context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
			first_user = User.objects.first()
			context['auditor_company'] = company.objects.filter(auditor=self.request.user).order_by('id')
			context['accountant_company'] = company.objects.filter(accountant=self.request.user).order_by('id')
			context['purchase_company'] = company.objects.filter(purchase_personal=self.request.user).order_by('id')
			context['sales_company'] = company.objects.filter(sales_personal=self.request.user).order_by('id')
			context['cb_company'] = company.objects.filter(cb_personal=self.request.user).order_by('id')
			context['shared_companys'] 	= zip_longest(context['auditor_company'],context['accountant_company'],context['purchase_company'],context['sales_company'],context['cb_company'])

		return context

class companyDetailView(ProductExistsRequiredMixin,LoginRequiredMixin,DetailView):
	context_object_name = 'company_details'
	model = company
	template_name = 'company/Dashboard.html'

	def get_context_data(self, **kwargs):
		context = super(companyDetailView, self).get_context_data(**kwargs)
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		context['company_details'] = company_details
		context['todo_list'] = Todo.objects.filter(User=self.request.user)
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		context['Products'] = Product_activation.objects.filter(User=self.request.user,product__id = 1, is_active=True)
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		context['blogs']  = Blog.objects.all().order_by('-id') 
		context['consultancies'] = consultancy.objects.all().order_by('-id')
		context['selectdates'] = selectdatefield.objects.filter(User=self.request.user)

		month_diff_q = selectdatefield_details.End_Date - selectdatefield_details.Start_Date
		month_diff = (int(month_diff_q.days/30))

		capital_clo = company_details.Company_group.filter(group_Name__icontains='Capital A/c').aggregate(the_sum=Coalesce(Sum('ledgergroups__Closing_balance'), Value(0)))['the_sum']
		capital_clo_m = company_details.Company_group.filter(Master__group_Name__icontains='Capital A/c').aggregate(the_sum=Coalesce(Sum('ledgergroups__Closing_balance'), Value(0)))['the_sum']
		context['capital_ac_total'] = capital_clo + capital_clo_m

		sundeb_clo = company_details.Company_group.filter(group_Name__icontains='Sundry Debtors').aggregate(the_sum=Coalesce(Sum('ledgergroups__Closing_balance'), Value(0)))['the_sum']
		sundeb_clo_m = company_details.Company_group.filter(Master__group_Name__icontains='Sundry Debtors').aggregate(the_sum=Coalesce(Sum('ledgergroups__Closing_balance'), Value(0)))['the_sum']
		context['total_dues_to_collect'] = sundeb_clo + sundeb_clo_m

		suncre_clo = company_details.Company_group.filter(group_Name__icontains='Sundry Creditors').aggregate(the_sum=Coalesce(Sum('ledgergroups__Closing_balance'), Value(0)))['the_sum']
		suncre_clo_m = company_details.Company_group.filter(Master__group_Name__icontains='Sundry Creditors').aggregate(the_sum=Coalesce(Sum('ledgergroups__Closing_balance'), Value(0)))['the_sum']
		context['total_dues_to_pay'] = suncre_clo + suncre_clo_m

		curntast_clo = company_details.Company_group.filter(group_Name__icontains='Current Assets').aggregate(the_sum=Coalesce(Sum('ledgergroups__Closing_balance'), Value(0)))['the_sum']
		curntast_clo_m = company_details.Company_group.filter(Master__group_Name__icontains='Current Assets').aggregate(the_sum=Coalesce(Sum('ledgergroups__Closing_balance'), Value(0)))['the_sum']
			
		# closing stock
		ldstckcb = stock_journal.objects.filter(Company=company_details.pk)
		qs2 = ldstckcb.aggregate(the_sum=Coalesce(Sum('closing_stock'), Value(0)))['the_sum']
		context['total_current_asset'] = curntast_clo + curntast_clo_m + qs2

		curntlia_clo = company_details.Company_group.filter(group_Name__icontains='Current Liabilities').aggregate(the_sum=Coalesce(Sum('ledgergroups__Closing_balance'), Value(0)))['the_sum']
		curntlia_clo_m = company_details.Company_group.filter(Master__group_Name__icontains='Current Liabilities').aggregate(the_sum=Coalesce(Sum('ledgergroups__Closing_balance'), Value(0)))['the_sum']
		context['total_current_liabilities'] = curntlia_clo + curntlia_clo_m

		context['working_capital'] = context['total_current_asset'] - context['total_current_liabilities']

		closing_stock = company_details.Company_stock_journal.aggregate(the_sum=Coalesce(Sum('closing_stock'), Value(0)))['the_sum']
		opening_stock = company_details.Company_stock_journal.aggregate(the_sum=Coalesce(Sum('opening_stock'), Value(0)))['the_sum']

		total_purchase 	= company_details.Company_group.filter(group_Name__icontains='Purchase Accounts').aggregate(the_sum=Coalesce(Sum('ledgergroups__To_pl_debit'), Value(0)))['the_sum']
		total_sales 	= company_details.Company_group.filter(group_Name__icontains='Sales Account').aggregate(the_sum=Coalesce(Sum('ledgergroups__To_pl_credit'), Value(0)))['the_sum']
		total_directexp = company_details.Company_group.filter(group_Name__icontains='Direct Expenses').aggregate(the_sum=Coalesce(Sum('ledgergroups__To_pl_debit'), Value(0)))['the_sum']
		total_directinc = company_details.Company_group.filter(group_Name__icontains='Direct Incomes').aggregate(the_sum=Coalesce(Sum('ledgergroups__To_pl_credit'), Value(0)))['the_sum']

		if month_diff != 0:
			context['sales_per_month'] = total_sales / month_diff
		else:
			context['sales_per_month'] = 0

		if int(month_diff_q.days) != 0:
			context['sales_per_day'] = total_sales / int(month_diff_q.days) 
		else:
			context['sales_per_day'] = 0

		context['sales_next_day'] = (context['sales_per_day'] * 25) / 100

		if closing_stock != 0:
			context['inventory_turnover'] = float(total_sales) / float(closing_stock)
		else:
			context['inventory_turnover'] = 0

		if  total_directinc < 0 and total_directexp < 0:
			gp = abs(total_sales) + abs(closing_stock) + abs(total_directexp) - abs(opening_stock) - abs(total_purchase) - abs(total_directinc)
		elif total_directexp < 0:
			gp = abs(total_sales) + abs(closing_stock) + abs(total_directinc) + abs(total_directexp) - abs(opening_stock) - abs(total_purchase)
		elif total_directinc < 0:
			gp = abs(total_sales) + abs(closing_stock) - abs(total_directinc) - abs(opening_stock) - abs(total_purchase) - abs(total_directexp)
		else:	
			gp = abs(total_sales) + abs(closing_stock) + abs(total_directinc) - abs(opening_stock) - abs(total_purchase) - abs(total_directexp)


		if total_sales or total_sales != 0:
			context['gross_profit'] = (gp / total_sales) * 100
			context['nett_profit']	= (company_details.pl / int(total_sales)) * 100
		else:
			context['gross_profit'] = 0	
			context['nett_profit']	= 0	

		context['cost_goods_sold'] = opening_stock + total_purchase + total_directexp - closing_stock - total_directinc  	

		context['operating_cost'] = context['cost_goods_sold'] + total_directexp

		investment = context['capital_ac_total'] + company_details.pl

		if investment or investment != 0:
			context['roi']	= (company_details.pl / investment) * 100
		else:
			context['roi']	= 0

		if context['working_capital'] or context['working_capital'] != 0:
			context['return_working_capital'] = (company_details.pl / int(context['working_capital'])) * 100
		else:
			context['return_working_capital'] = 0



		pl_ledger = company_details.Companys.get(name__icontains='Profit & Loss A/c')

		qsob  = Pl_journal.objects.filter(Company=company_details.pk, By=pl_ledger.pk,  Date__lt=selectdatefield_details.Start_Date).order_by('Date')
		qsob2 = Pl_journal.objects.filter(Company=company_details.pk, To=pl_ledger.pk,  Date__lt=selectdatefield_details.Start_Date).order_by('Date')

		total_debitob = qsob.aggregate(the_sum=Coalesce(Sum('Debit'), Value(0)))['the_sum']
		total_creditob = qsob2.aggregate(the_sum=Coalesce(Sum('Credit'), Value(0)))['the_sum']

		if(pl_ledger.group1_Name.balance_nature == 'Debit'):
			opening_balance = abs(pl_ledger.Opening_Balance) + abs(total_debitob) - abs(total_creditob)
		else:
			opening_balance = abs(pl_ledger.Opening_Balance) + abs(total_creditob) - abs(total_debitob) 

		top_ledgers_deb = company_details.Companys.filter(group1_Name__group_Name__icontains='Sundry Debtors')
		context['top_ledger_sales'] = top_ledgers_deb.annotate(total = Coalesce(Sum('partyledgersales__sub_total'), 0)).order_by('-total')[:10] ## all ledger sales total
		context['total_ledger'] = context['top_ledger_sales'].aggregate(partial_total=Sum('total'))['partial_total']

		top_ledgers_cre = company_details.Companys.filter(group1_Name__group_Name__icontains='Sundry Creditors')
		context['top_ledger_purchase'] = top_ledgers_cre.annotate(total = Coalesce(Sum('partyledger__sub_total'), 0)).order_by('-total')[:10] ## all ledger purchase total
		context['total_ledger_purchase'] = context['top_ledger_purchase'].aggregate(partial_total=Sum('total'))['partial_total']


		context['top_stock'] = company_details.Company_stock.annotate(
							total = Coalesce(Sum('salestock__Total'), 0),
							quantity = Coalesce(Sum('salestock__Quantity'), 0),
							total_puchase = Coalesce(Sum('purchasestock__Total_p'), 0),
							quantity_purchase = Coalesce(Sum('purchasestock__Quantity_p'), 0)).order_by('-total')[:10]
							 # all stock sales and purchase total and Quantity
		context['top_stock_total'] = context['top_stock'].aggregate(partial_total=Sum('total'))['partial_total']

		context['stock_margin'] = context['top_stock'].annotate(
							Avg_purchase = ExpressionWrapper(F('total_puchase') / F('quantity_purchase'), output_field=FloatField()),
							Avg_sales = ExpressionWrapper(F('total') / F('quantity'), output_field=FloatField())) 


		results = collections.OrderedDict()
		result = Sales.objects.filter(Company=company_details.pk,date__gte=selectdatefield_details.Start_Date, date__lt=selectdatefield_details.End_Date).annotate(real_total = Case(When(sub_total__isnull=True, then=0),default=F('sub_total')))
		result_purchase = Purchase.objects.filter(Company=company_details.pk,date__gte=selectdatefield_details.Start_Date, date__lt=selectdatefield_details.End_Date).annotate(real_total_purchase = Case(When(sub_total__isnull=True, then=0),default=F('sub_total')))
		qscb  = Pl_journal.objects.filter(Company=company_details.pk, By=pl_ledger.pk, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).annotate(real_total_debit = Case(When(Debit__isnull=True, then=0),default=F('Debit')))
		qscb2 = Pl_journal.objects.filter(Company=company_details.pk, To=pl_ledger.pk, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).annotate(real_total_credit = Case(When(Credit__isnull=True, then=0),default=F('Credit')))

		date_cursor = selectdatefield_details.Start_Date

		j = 0
		k = 0

		while date_cursor <= selectdatefield_details.End_Date:
			month_partial_total = result.filter(date__month=date_cursor.month).aggregate(partial_total=Sum('real_total'))['partial_total']
			month_partial_total_purchase = result_purchase.filter(date__month=date_cursor.month).aggregate(partial_total_purchase=Sum('real_total_purchase'))['partial_total_purchase']
			month_partial_total_debit = qscb.filter(Date__month=date_cursor.month).aggregate(partial_total_debit=Sum('real_total_debit'))['partial_total_debit']
			month_partial_total_credit = qscb2.filter(Date__month=date_cursor.month).aggregate(partial_total_credit=Sum('real_total_credit'))['partial_total_credit']

			if month_partial_total == None:

				month_partial_total = int(0)
				e = month_partial_total
				
			else:

				e = month_partial_total


			if month_partial_total_purchase == None:

				month_partial_total_purchase = int(0)
				z = month_partial_total_purchase
				
			else:

				z = month_partial_total_purchase

			if month_partial_total_debit == None:

				month_partial_total_debit = int(0)

				g = month_partial_total_debit 

			else:

				g = month_partial_total_debit


			if month_partial_total_credit == None:

				month_partial_total_credit = int(0)

				f = month_partial_total_credit

			else:

				f = month_partial_total_credit
			
			j = j + g - f

			k = j + opening_balance

			results[calendar.month_name[date_cursor.month]] =  [e,z,k]			

			date_cursor += relativedelta.relativedelta(months=1)

		context['data'] = results.items()
		return context

def validate_gst_billing(request):

	data = {
		'is_enable' : company.objects.filter(gst_enabled = False,composite_enable = True).exists()
	}
	if data['is_enable']:
		data['error_message'] = 'To enable composite billing GST should be enabled'
	return JsonResponse(data)

class companyCreateView(NormalProductExistsRequiredMixin,LoginRequiredMixin,CreateView):
	form_class  = companyform
	template_name = "company/company_form.html"

	def get_success_url(self,**kwargs):
		return reverse('company:list')

	def form_valid(self, form):
		form.instance.User = self.request.user
		counter = company.objects.filter(User=self.request.user).count() + 1
		form.instance.counter = counter
		return super(companyCreateView, self).form_valid(form)

	def get_context_data(self, **kwargs):
		context = super(companyCreateView, self).get_context_data(**kwargs)
		context['Products_aggrement'] = Product_activation.objects.filter(User=self.request.user,product__id = 9, is_active=True)
		context['Products'] = Product_activation.objects.filter(User=self.request.user,product__id = 1, is_active=True)
		context['Role_products'] = Role_product_activation.objects.filter(User=self.request.user,product__id = 1, is_active=True)
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		return context


class companyUpdateView(NormalProductExistsRequiredMixin,LoginRequiredMixin,UpdateView):
	model = company
	form_class  = companyupdateform
	template_name = "company/company_form.html"

	def get_success_url(self,**kwargs):
		return reverse('company:list')

	def get_context_data(self, **kwargs):
		context = super(companyUpdateView, self).get_context_data(**kwargs)
		context['Products_aggrement'] = Product_activation.objects.filter(User=self.request.user,product__id = 9, is_active=True)
		context['Products'] = Product_activation.objects.filter(User=self.request.user,product__id = 1, is_active=True)
		context['Role_products'] = Role_product_activation.objects.filter(User=self.request.user,product__id = 1, is_active=True)
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']  
		return context


def save_all(request,form,template_name):
	data = dict()
	if request.method == 'POST':
		if form.is_valid():
			form.save()
			data['form_is_valid'] = True
			company_list = company.objects.all().order_by('-id')
			data['companies'] = render_to_string('company/companies.html',{'company_list':company_list})
		else:
			data['form_is_valid'] = False
	context = {
	'form':form
	}
	data['html_form'] = render_to_string(template_name,context,request=request)
	return JsonResponse(data)

@login_required
@product_1_activation
def company_delete(request,id):
	data = dict()
	Company = get_object_or_404(company,id=id)
	if request.method == "POST":
		Company.delete()
		data['form_is_valid'] = True
		company_list = company.objects.all().order_by('-id')
		data['companies'] = render_to_string('company/companies.html',{'company_list':company_list})
	else:
		context = {'Company':Company}
		data['html_form'] = render_to_string('company/company_confirm_delete.html',context,request=request)

	return JsonResponse(data)

@login_required
@product_1_activation
def specific_company_details(request, pk):
	company_details = get_object_or_404(company, pk=pk)

	if not request.user.is_authenticated:
		Products_aggrement = Product_activation.objects.filter(User=request.user,product__id = 9, is_active=True)
		Products = Product_activation.objects.filter(product__id = 1, is_active=True)
		Role_products = Role_product_activation.objects.filter(product__id = 1, is_active=True)
		Todos = Todo.objects.filter(complete=False)
		Todos_total = Todo.objects.filter(complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		inbox = Message.objects.all()
		inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		send_count = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']	
	else:
		Products_aggrement = Product_activation.objects.filter(product__id = 9, is_active=True)
		Products = Product_activation.objects.filter(User=request.user,product__id = 1, is_active=True)
		Todos = Todo.objects.filter(User=request.user,complete=False)
		Role_products = Role_product_activation.objects.filter(User=request.user,product__id = 1, is_active=True)
		Todos_total = Todo.objects.filter(User=request.user,complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		inbox = Message.objects.filter(reciever=request.user)
		inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

	context = {
		'company_details' 			: company_details,
		'inbox'			  			: inbox,
		'inbox_count'	  			: inbox_count,
		'send_count'	  			: send_count,
		'Products'		  			: Products,
		'Todos'			 			: Todos,
		'Todos_total' 	  			: Todos_total, 
		'Role_products' 			: Role_products,
		'Products_aggrement'		: Products_aggrement 

	}
	return render(request, 'company/company_details.html', context)


######################################## Auditor Views #############################################

@login_required
@product_1_activation
def auditor_list(request, pk):
	company_details = get_object_or_404(company, pk=pk)

	if not request.user.is_authenticated:
		Products_aggrement = Product_activation.objects.filter(User=request.user,product__id = 9, is_active=True)
		Products = Product_activation.objects.filter(product__id = 1, is_active=True)
		Role_products = Role_product_activation.objects.filter(product__id = 1, is_active=True)
		Todos = Todo.objects.filter(complete=False)
		Todos_total = Todo.objects.filter(complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		inbox = Message.objects.all()
		inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		send_count = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		
	else:
		Products_aggrement = Product_activation.objects.filter(product__id = 9, is_active=True)
		Products = Product_activation.objects.filter(User=request.user,product__id = 1, is_active=True)
		Todos = Todo.objects.filter(User=request.user,complete=False)
		Role_products = Role_product_activation.objects.filter(User=request.user,product__id = 1, is_active=True)
		Todos_total = Todo.objects.filter(User=request.user,complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		inbox = Message.objects.filter(reciever=request.user)
		inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

	context = {
		'company_details' 			: company_details,
		'inbox'			  			: inbox,
		'inbox_count'	  			: inbox_count,
		'send_count'	  			: send_count,
		'Products'		  			: Products,
		'Todos'			 			: Todos,
		'Todos_total' 	  			: Todos_total,
		'Role_products' 			: Role_products,
		'Products_aggrement' 		: Products_aggrement  

	}
	return render(request, 'auditor/auditor_list.html', context)


@login_required
@product_1_activation
def search_auditors(request,pk):
	template = 'auditor/search_auditor.html'

	user_profile = Profile.objects.filter(user_type__icontains='Professional')

	query = request.GET.get('q')

	if query:
		result = user_profile.filter(Q(Name__username__icontains=query) | Q(E_mail__icontains=query) | Q(Full_Name__icontains=query)).exclude(Name=request.user)
	else:
		result = Profile.objects.none()

	professional_count = result.count()

	page = request.GET.get('page', 1)
	paginator = Paginator(result, 9)
	try:
		users = paginator.page(page)
	except PageNotAnInteger:
		users = paginator.page(1)
	except EmptyPage:
		users = paginator.page(paginator.num_pages)

	Products_aggrement = Product_activation.objects.filter(product__id = 9, is_active=True)
	Products = Product_activation.objects.filter(product__id = 1, is_active=True)
	Role_products = Role_product_activation.objects.filter(product__id = 1, is_active=True)
	Todos = Todo.objects.filter(complete=False)
	Todos_total = Todo.objects.filter(complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
	inbox = Message.objects.all()
	inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
	send_count = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
	company_details = get_object_or_404(company, pk=pk)

	

	context = {
		'professionals'			: result,
		'users'					: users,
		'professional_count'	: professional_count,
		'Products'				: Products,
		'inbox'					: inbox,
		'inbox_count'			: inbox_count,
		'send_count'			: send_count,
		'Todos'					: Todos,
		'Todos_total' 			: Todos_total ,
		'company_details' 		: company_details,
		'Role_products' 		: Role_products,
		'Products_aggrement' 	: Products_aggrement,

	}

	return render(request, template, context)

@login_required
@product_1_activation
def add_auditor(request, pk, pk2):
	role_products = get_object_or_404(Role_based_product, pk=1)
	company_details = get_object_or_404(company, pk=pk)
	user_profile = get_object_or_404(Profile, pk=pk2)

	company_details.auditor.add(user_profile.Name)
	company_details.save()
	user_profile.subscribed_role_products.add(role_products)
	user_profile.save()

	return redirect(reverse('company:search_auditors', kwargs={"pk": company_details.pk}))


@login_required
@product_1_activation
def delete_auditors(request, pk, pk2):
	company_details = get_object_or_404(company, pk=pk)
	user_profile = get_object_or_404(Profile, pk=pk2)

	company_details.auditor.remove(user_profile.Name)

	return redirect(reverse('company:auditor_list', kwargs={"pk": company_details.pk}))

######################################## Accountant Views #############################################

@login_required
@product_1_activation
def accountant_list(request, pk):
	company_details = get_object_or_404(company, pk=pk)

	if not request.user.is_authenticated:
		Products_aggrement = Product_activation.objects.filter(product__id = 9, is_active=True)
		Products = Product_activation.objects.filter(product__id = 1, is_active=True)
		Role_products = Role_product_activation.objects.filter(product__id = 1, is_active=True)
		Todos = Todo.objects.filter(complete=False)
		Todos_total = Todo.objects.filter(complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		inbox = Message.objects.all()
		inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		send_count = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		
	else:
		Products_aggrement = Product_activation.objects.filter(User=request.user,product__id = 9, is_active=True)
		Products = Product_activation.objects.filter(User=request.user,product__id = 1, is_active=True)
		Todos = Todo.objects.filter(User=request.user,complete=False)
		Role_products = Role_product_activation.objects.filter(User=request.user,product__id = 1, is_active=True)
		Todos_total = Todo.objects.filter(User=request.user,complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		inbox = Message.objects.filter(reciever=request.user)
		inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

	context = {
		'company_details' 			: company_details,
		'inbox'			  			: inbox,
		'inbox_count'	  			: inbox_count,
		'send_count'	  			: send_count,
		'Products'		  			: Products,
		'Todos'			 			: Todos,
		'Todos_total' 	  			: Todos_total,
		'Role_products' 			: Role_products,
		'Products_aggrement' 		: Products_aggrement 

	}
	return render(request, 'accountant/accountant_list.html', context)


@login_required
@product_1_activation
def search_accountant(request,pk):
	template = 'accountant/search_accountant.html'

	query = request.GET.get('q')

	if query:
		result = Profile.objects.filter(Q(Name__username__icontains=query) | Q(E_mail__icontains=query) | Q(Full_Name__icontains=query)).exclude(Name=request.user)
	else:
		result = Profile.objects.none()

	professional_count = result.count()

	page = request.GET.get('page', 1)
	paginator = Paginator(result, 9)
	try:
		users = paginator.page(page)
	except PageNotAnInteger:
		users = paginator.page(1)
	except EmptyPage:
		users = paginator.page(paginator.num_pages)

	Products_aggrement = Product_activation.objects.filter(product__id = 9, is_active=True)
	Products = Product_activation.objects.filter(product__id = 1, is_active=True)
	Role_products = Role_product_activation.objects.filter(product__id = 1, is_active=True)
	Todos = Todo.objects.filter(complete=False)
	Todos_total = Todo.objects.filter(complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
	inbox = Message.objects.all()
	inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
	send_count = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
	company_details = get_object_or_404(company, pk=pk)

	

	context = {
		'professionals'			: result,
		'users'					: users,
		'professional_count'	: professional_count,
		'Products'				: Products,
		'inbox'					: inbox,
		'inbox_count'			: inbox_count,
		'send_count'			: send_count,
		'Todos'					: Todos,
		'Todos_total' 			: Todos_total ,
		'company_details' 		: company_details,
		'Role_products' 		: Role_products,
		'Products_aggrement' 	: Products_aggrement

	}

	return render(request, template, context)

@login_required
@product_1_activation
def add_accountant(request, pk, pk2):
	role_products = get_object_or_404(Role_based_product, pk=1)
	company_details = get_object_or_404(company, pk=pk)
	user_profile = get_object_or_404(Profile, pk=pk2)

	company_details.accountant.add(user_profile.Name)
	company_details.save()
	user_profile.subscribed_role_products.add(role_products)
	user_profile.save()

	return redirect(reverse('company:search_accountant', kwargs={"pk": company_details.pk}))


@login_required
@product_1_activation
def delete_accountant(request, pk, pk2):
	company_details = get_object_or_404(company, pk=pk)
	user_profile = get_object_or_404(Profile, pk=pk2)

	company_details.accountant.remove(user_profile.Name)

	return redirect(reverse('company:accountant_list', kwargs={"pk": company_details.pk}))

######################################## Purchase Personnel Views #############################################

@login_required
@product_1_activation
def purchase_personal_list(request, pk):
	company_details = get_object_or_404(company, pk=pk)

	if not request.user.is_authenticated:
		Products_aggrement = Product_activation.objects.filter(product__id = 9, is_active=True)
		Products = Product_activation.objects.filter(product__id = 1, is_active=True)
		Role_products = Role_product_activation.objects.filter(product__id = 1, is_active=True)
		Todos = Todo.objects.filter(complete=False)
		Todos_total = Todo.objects.filter(complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		inbox = Message.objects.all()
		inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		send_count = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		
	else:
		Products_aggrement = Product_activation.objects.filter(User=request.user,product__id = 9, is_active=True)
		Products = Product_activation.objects.filter(User=request.user,product__id = 1, is_active=True)
		Todos = Todo.objects.filter(User=request.user,complete=False)
		Role_products = Role_product_activation.objects.filter(User=request.user,product__id = 1, is_active=True)
		Todos_total = Todo.objects.filter(User=request.user,complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		inbox = Message.objects.filter(reciever=request.user)
		inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

	context = {
		'company_details' 			: company_details,
		'inbox'			  			: inbox,
		'inbox_count'	  			: inbox_count,
		'send_count'	  			: send_count,
		'Products'		  			: Products,
		'Todos'			 			: Todos,
		'Todos_total' 	  			: Todos_total, 
		'Role_products' 			: Role_products,
		'Products_aggrement' 		: Products_aggrement 

	}
	return render(request, 'purchase_personal/purchase_personnel_list.html', context)


@login_required
@product_1_activation
def search_purchase_personal(request,pk):
	template = 'purchase_personal/search_purchase_personnel.html'

	query = request.GET.get('q')

	if query:
		result = Profile.objects.filter(Q(Name__username__icontains=query) | Q(E_mail__icontains=query) | Q(Full_Name__icontains=query)).exclude(Name=request.user)
	else:
		result = Profile.objects.none()

	professional_count = result.count()

	page = request.GET.get('page', 1)
	paginator = Paginator(result, 9)
	try:
		users = paginator.page(page)
	except PageNotAnInteger:
		users = paginator.page(1)
	except EmptyPage:
		users = paginator.page(paginator.num_pages)

	Products_aggrement = Product_activation.objects.filter(product__id = 9, is_active=True)
	Products = Product_activation.objects.filter(product__id = 1, is_active=True)
	Role_products = Role_product_activation.objects.filter(product__id = 1, is_active=True)
	Todos = Todo.objects.filter(complete=False)
	Todos_total = Todo.objects.filter(complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
	inbox = Message.objects.all()
	inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
	send_count = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
	company_details = get_object_or_404(company, pk=pk)

	

	context = {
		'professionals'			: result,
		'users'					: users,
		'professional_count'	: professional_count,
		'Products'				: Products,
		'inbox'					: inbox,
		'inbox_count'			: inbox_count,
		'send_count'			: send_count,
		'Todos'					: Todos,
		'Todos_total' 			: Todos_total ,
		'company_details' 		: company_details,
		'Role_products' 		: Role_products,
		'Products_aggrement' 	: Products_aggrement

	}

	return render(request, template, context)

@login_required
@product_1_activation
def add_purchase_personal(request, pk, pk2):
	role_products = get_object_or_404(Role_based_product, pk=1)
	company_details = get_object_or_404(company, pk=pk)
	user_profile = get_object_or_404(Profile, pk=pk2)

	company_details.purchase_personal.add(user_profile.Name)
	company_details.save()
	user_profile.subscribed_role_products.add(role_products)
	user_profile.save()

	return redirect(reverse('company:search_purchase_personal', kwargs={"pk": company_details.pk}))


@login_required
@product_1_activation
def delete_purchase_personal(request, pk, pk2):
	company_details = get_object_or_404(company, pk=pk)
	user_profile = get_object_or_404(Profile, pk=pk2)

	company_details.purchase_personal.remove(user_profile.Name)

	return redirect(reverse('company:purchase_personal_list', kwargs={"pk": company_details.pk}))


######################################## Sales Personnel Views #############################################

@login_required
@product_1_activation
def sales_personal_list(request, pk):
	company_details = get_object_or_404(company, pk=pk)

	if not request.user.is_authenticated:
		Products_aggrement = Product_activation.objects.filter(product__id = 9, is_active=True)
		Products = Product_activation.objects.filter(product__id = 1, is_active=True)
		Role_products = Role_product_activation.objects.filter(product__id = 1, is_active=True)
		Todos = Todo.objects.filter(complete=False)
		Todos_total = Todo.objects.filter(complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		inbox = Message.objects.all()
		inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		send_count = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		
	else:
		Products_aggrement = Product_activation.objects.filter(User=request.user,product__id = 9, is_active=True)
		Products = Product_activation.objects.filter(User=request.user,product__id = 1, is_active=True)
		Todos = Todo.objects.filter(User=request.user,complete=False)
		Role_products = Role_product_activation.objects.filter(User=request.user,product__id = 1, is_active=True)
		Todos_total = Todo.objects.filter(User=request.user,complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		inbox = Message.objects.filter(reciever=request.user)
		inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

	context = {
		'company_details' 			: company_details,
		'inbox'			  			: inbox,
		'inbox_count'	  			: inbox_count,
		'send_count'	  			: send_count,
		'Products'		  			: Products,
		'Todos'			 			: Todos,
		'Todos_total' 	  			: Todos_total,
		'Role_products' 			: Role_products,
		'Products_aggrement' 		: Products_aggrement 

	}
	return render(request, 'sales_personnel/sales_personnel_list.html', context)


@login_required
@product_1_activation
def search_sales_personal(request,pk):
	template = 'sales_personnel/search_sales_personnel.html'

	query = request.GET.get('q')

	if query:
		result = Profile.objects.filter(Q(Name__username__icontains=query) | Q(E_mail__icontains=query) | Q(Full_Name__icontains=query)).exclude(Name=request.user)
	else:
		result = Profile.objects.none()

	professional_count = result.count()

	page = request.GET.get('page', 1)
	paginator = Paginator(result, 9)
	try:
		users = paginator.page(page)
	except PageNotAnInteger:
		users = paginator.page(1)
	except EmptyPage:
		users = paginator.page(paginator.num_pages)

	Products_aggrement = Product_activation.objects.filter(product__id = 9, is_active=True)
	Products = Product_activation.objects.filter(product__id = 1, is_active=True)
	Role_products = Role_product_activation.objects.filter(product__id = 1, is_active=True)
	Todos = Todo.objects.filter(complete=False)
	Todos_total = Todo.objects.filter(complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
	inbox = Message.objects.all()
	inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
	send_count = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
	company_details = get_object_or_404(company, pk=pk)


	context = {
		'professionals'			: result,
		'users'					: users,
		'professional_count'	: professional_count,
		'Products'				: Products,
		'inbox'					: inbox,
		'inbox_count'			: inbox_count,
		'send_count'			: send_count,
		'Todos'					: Todos,
		'Todos_total' 			: Todos_total ,
		'company_details' 		: company_details,
		'Role_products' 		: Role_products,
		'Products_aggrement' 	: Products_aggrement

	}

	return render(request, template, context)

@login_required
@product_1_activation
def add_sales_personal(request, pk, pk2):
	role_products = get_object_or_404(Role_based_product, pk=1)
	company_details = get_object_or_404(company, pk=pk)
	user_profile = get_object_or_404(Profile, pk=pk2)

	company_details.sales_personal.add(user_profile.Name)
	company_details.save()
	user_profile.subscribed_role_products.add(role_products)
	user_profile.save()

	return redirect(reverse('company:search_sales_personal', kwargs={"pk": company_details.pk}))


@login_required
@product_1_activation
def delete_sales_personal(request, pk, pk2):
	company_details = get_object_or_404(company, pk=pk)
	user_profile = get_object_or_404(Profile, pk=pk2)

	company_details.sales_personal.remove(user_profile.Name)

	return redirect(reverse('company:sales_personal_list', kwargs={"pk": company_details.pk}))


######################################## Cash/Bank Personnel Views #############################################

@login_required
@product_1_activation
def cb_personal_list(request, pk):
	company_details = get_object_or_404(company, pk=pk)

	if not request.user.is_authenticated:
		Products_aggrement = Product_activation.objects.filter(product__id = 9, is_active=True)
		Products = Product_activation.objects.filter(product__id = 1, is_active=True)
		Role_products = Role_product_activation.objects.filter(product__id = 1, is_active=True)
		Todos = Todo.objects.filter(complete=False)
		Todos_total = Todo.objects.filter(complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		inbox = Message.objects.all()
		inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		send_count = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		
	else:
		Products_aggrement = Product_activation.objects.filter(User=request.user,product__id = 9, is_active=True)
		Products = Product_activation.objects.filter(User=request.user,product__id = 1, is_active=True)
		Todos = Todo.objects.filter(User=request.user,complete=False)
		Role_products = Role_product_activation.objects.filter(User=request.user,product__id = 1, is_active=True)
		Todos_total = Todo.objects.filter(User=request.user,complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		inbox = Message.objects.filter(reciever=request.user)
		inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

	context = {
		'company_details' 			: company_details,
		'inbox'			  			: inbox,
		'inbox_count'	  			: inbox_count,
		'send_count'	  			: send_count,
		'Products'		  			: Products,
		'Todos'			 			: Todos,
		'Todos_total' 	  			: Todos_total, 
		'Role_products' 			: Role_products,
		'Products_aggrement' 		: Products_aggrement

	}
	return render(request, 'cb_personnal/cb_personnal_list.html', context)


@login_required
@product_1_activation
def search_cb_personal(request,pk):
	template = 'cb_personnal/search_cb_personnal.html'

	query = request.GET.get('q')

	if query:
		result = Profile.objects.filter(Q(Name__username__icontains=query) | Q(E_mail__icontains=query) | Q(Full_Name__icontains=query)).exclude(Name=request.user)
	else:
		result = Profile.objects.none()

	professional_count = result.count()

	page = request.GET.get('page', 1)
	paginator = Paginator(result, 9)
	try:
		users = paginator.page(page)
	except PageNotAnInteger:
		users = paginator.page(1)
	except EmptyPage:
		users = paginator.page(paginator.num_pages)

	Products_aggrement = Product_activation.objects.filter(User=request.user,product__id = 9, is_active=True)
	Products = Product_activation.objects.filter(product__id = 1, is_active=True)
	Role_products = Role_product_activation.objects.filter(product__id = 1, is_active=True)
	Todos = Todo.objects.filter(complete=False)
	Todos_total = Todo.objects.filter(complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
	inbox = Message.objects.all()
	inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
	send_count = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
	company_details = get_object_or_404(company, pk=pk)
	

	context = {
		'professionals'			: result,
		'users'					: users,
		'professional_count'	: professional_count,
		'Products'				: Products,
		'inbox'					: inbox,
		'inbox_count'			: inbox_count,
		'send_count'			: send_count,
		'Todos'					: Todos,
		'Todos_total' 			: Todos_total ,
		'company_details' 		: company_details,
		'Role_products' 		: Role_products,
		'Products_aggrement' 	: Products_aggrement

	}

	return render(request, template, context)

@login_required
@product_1_activation
def add_cb_personal(request, pk, pk2):
	role_products = get_object_or_404(Role_based_product, pk=1)
	company_details = get_object_or_404(company, pk=pk)
	user_profile = get_object_or_404(Profile, pk=pk2)

	company_details.cb_personal.add(user_profile.Name)
	company_details.save()
	user_profile.subscribed_role_products.add(role_products)
	user_profile.save()

	return redirect(reverse('company:search_cb_personal', kwargs={"pk": company_details.pk}))


@login_required
@product_1_activation
def delete_cb_personal(request, pk, pk2):
	company_details = get_object_or_404(company, pk=pk)
	user_profile = get_object_or_404(Profile, pk=pk2)

	company_details.cb_personal.remove(user_profile.Name)

	return redirect(reverse('company:cb_personal_list', kwargs={"pk": company_details.pk}))