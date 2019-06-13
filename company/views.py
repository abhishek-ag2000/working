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
import xlwt


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
	all_objects = list(company.objects.filter(pk=pk)) + list(group1.objects.filter(Company=company_details.pk)) + list(ledger1.objects.filter(Company=company_details.pk)) + list(journal.objects.filter(Company=company_details.pk)) + list(Payment.objects.filter(Company=company_details.pk)) + list(Particularspayment.objects.filter(payment__Company=company_details.pk)) + list(Receipt.objects.filter(Company=company_details.pk)) + list(Particularsreceipt.objects.filter(receipt__Company=company_details.pk)) + list(Contra.objects.filter(Company=company_details.pk)) + list(Particularscontra.objects.filter(contra__Company=company_details.pk)) + list(Stockgroup.objects.filter(Company=company_details.pk)) + list(Simpleunits.objects.filter(Company=company_details.pk)) + list(Compoundunits.objects.filter(Company=company_details.pk)) + list(Stockdata.objects.filter(Company=company_details.pk)) + list(Purchase.objects.filter(Company=company_details.pk)) + list(Stock_Total.objects.filter(purchases__Company=company_details.pk)) + list(Sales.objects.filter(Company=company_details.pk)) + list(Stock_Total_sales.objects.filter(sales__Company=company_details.pk))
	data = serializers.serialize('json', all_objects)
	data = json.dumps(json.loads(data), indent=4)
	response = HttpResponse(data , content_type='application/json')
	response['Content-Disposition'] = 'attachment; filename={}-{}.json'.format(company_details.Name,datetime.now()) 
	return response


@login_required
@product_1_activation
def getcompanyObject_in_excel(request, pk):
	company_details = get_object_or_404(company, pk=pk)

	response = HttpResponse(content_type='application/ms-excel')
	response['Content-Disposition'] = 'attachment; filename={}.xls'.format(company_details.Name) 

	wb = xlwt.Workbook(encoding='utf-8')
	ws = wb.add_sheet('Company')
	wg = wb.add_sheet('Ledger_Groups')
	wl = wb.add_sheet('Ledgers')
	wj = wb.add_sheet('Journals')
	wp = wb.add_sheet('Payments')
	wr = wb.add_sheet('Receipts')
	wc = wb.add_sheet('Contra')
	wsg = wb.add_sheet('Stock_Groups')
	wsm = wb.add_sheet('SimpleUnits')
	wcu = wb.add_sheet('CompoundUnits')
	wst = wb.add_sheet('StockItems')
	wpu = wb.add_sheet('Purchases')
	wps = wb.add_sheet('Purchase_Stock')
	wsa = wb.add_sheet('Sales')
	wss = wb.add_sheet('Sales Stock')
	wsc = wb.add_sheet('Stock Closing')

	# Sheet header, first row
	row_num = 0
	row_num1 = 0
	row_num2 = 0
	row_num3 = 0
	row_num4 = 0
	row_num5 = 0
	row_num6 = 0
	row_num7 = 0
	row_num8 = 0
	row_num9 = 0
	row_num10 = 0
	row_num11 = 0
	row_num12 = 0
	row_num13 = 0
	row_num14 = 0
	row_num15 = 0

	font_style = xlwt.XFStyle()
	font_style.font.bold = True

	columns = ['User', 'created_date', 'modified_date', 'Name', 'bussiness_nature', 'maintain', 'Type_of_company', 'Address', 'Country', 'State','Financial_Year_From','Books_Begining_From','GST_enabled','composite_enable',]
	columns_g = ['Group_Name', 'Voucher_Id','Parent','Nature','Balance_Nature']
	columns_l = ['Group_Name','Voucher_Id','Ledger_Name','Opening','Balance_Nature','Contact_Name','Address','State','PIN','PAN','GST_No']
	columns_j = ['Date','Voucher_Id','Voucher_Type','By','To','Debit','Credit']
	columns_p = ['Date','Voucher_Id','Payment_Account','Payment_Particular','Payment_Amount']
	columns_r = ['Date','Voucher_Id','Receipt_Account','Receipt_Particular','Receipt_Amount']
	columns_c = ['Date','Voucher_Id','Contra_Account','Contra_Particular','Contra_Amount']
	columns_sg = ['Group_Name','Voucher_Id','Parent',]
	columns_sm = ['Symbol','Voucher_Id','Formal_Name',]
	columns_cu = ['First_Unit','Voucher_Id','Conversion','Seconds_Unit']
	columns_st = ['Stock_Name','Voucher_Id','Simple_Unit','Quantity','Rate','Opening','Group_Name','Unit']
	columns_pu = ['Date','Voucher_Id','Invoice_No','Party_Account','Purchase_Account','Party_Name','Address','State','PAN','GST_No','Sub_Total','CGST_Total','SGST_IGST_Total','Composite_Tax','Total']
	columns_ps = ['Voucher_Id','Stock_Name','Simple_Unit','Quantity','Rate','Discount','GST_Rate','Master_GST_Rate','Sub_Total','CGST_Total','SGST_IGST_Total','Composite_Tax','Total']
	columns_sa = ['Date','Voucher_Id','Invoice_No','Party_Account','Sales_Account','Party_Name','Address','State','PAN','GST_No','Sub_Total','CGST_Total','SGST_IGST_Total','Composite_Tax','Total']
	columns_ss = ['Voucher_Id','Stock_Name','Simple_Unit','Quantity','Rate','Discount','GST_Rate','Master_GST_Rate','Sub_Total','CGST_Total','SGST_IGST_Total','Composite_Tax','Total']
	columns_sc = ['Stock_Name','Voucher_Id','Opening_Stock','Closing_Quantity','Closing_Stock',]


	for col_num in range(len(columns)):
		ws.write(row_num, col_num, columns[col_num], font_style)

	for col_num_g in range(len(columns_g)):
		wg.write(row_num, col_num_g, columns_g[col_num_g], font_style)

	for col_num_l in range(len(columns_l)):
		wl.write(row_num, col_num_l, columns_l[col_num_l], font_style)

	for col_num_j in range(len(columns_j)):
		wj.write(row_num, col_num_j, columns_j[col_num_j], font_style)

	for col_num_p in range(len(columns_p)):
		wp.write(row_num, col_num_p, columns_p[col_num_p], font_style)

	for col_num_r in range(len(columns_r)):
		wr.write(row_num, col_num_r, columns_r[col_num_r], font_style)

	for col_num_c in range(len(columns_c)):
		wc.write(row_num, col_num_c, columns_c[col_num_c], font_style)

	for col_num_sg in range(len(columns_sg)):
		wsg.write(row_num, col_num_sg, columns_sg[col_num_sg], font_style)

	for col_num_sm in range(len(columns_sm)):
		wsm.write(row_num, col_num_sm, columns_sm[col_num_sm], font_style)

	for col_num_cu in range(len(columns_cu)):
		wcu.write(row_num, col_num_cu, columns_cu[col_num_cu], font_style)

	for col_num_st in range(len(columns_st)):
		wst.write(row_num, col_num_st, columns_st[col_num_st], font_style)

	for col_num_pu in range(len(columns_pu)):
		wpu.write(row_num, col_num_pu, columns_pu[col_num_pu], font_style)

	for col_num_ps in range(len(columns_ps)):
		wps.write(row_num, col_num_ps, columns_ps[col_num_ps], font_style)

	for col_num_sa in range(len(columns_sa)):
		wsa.write(row_num, col_num_sa, columns_sa[col_num_sa], font_style)

	for col_num_ss in range(len(columns_ss)):
		wss.write(row_num, col_num_ss, columns_ss[col_num_ss], font_style)

	for col_num_sc in range(len(columns_sc)):
		wsc.write(row_num, col_num_sc, columns_sc[col_num_sc], font_style)



	# Sheet body, remaining rows
	font_style = xlwt.XFStyle()

	rows = company.objects.filter(pk=pk).values_list('User__username','id', 'created_date', 'modified_date', 'Name', 'bussiness_nature', 'maintain', 'Type_of_company', 'Address', 'Country', 'State','Financial_Year_From','Books_Begining_From','gst_enabled','composite_enable')

	for row in rows:
		row_num += 1
		for col_num in range(len(row)):
			ws.write(row_num, col_num, row[col_num], font_style)

	rows_g = group1.objects.filter(Company=company_details.pk).exclude(group_Name__icontains='Primary').values_list('group_Name','id','Master__group_Name','Nature_of_group1','balance_nature')

	for row in rows_g:
		row_num1 += 1
		for col_num in range(len(row)):
			wg.write(row_num1, col_num, row[col_num], font_style)

	rows_l = ledger1.objects.filter(Company=company_details.pk).values_list('group1_Name__group_Name','id','name','Balance_opening', 'group1_Name__balance_nature','User_Name','Address','State','Pin_Code','PanIt_No','GST_No')

	for row in rows_l:
		row_num2 += 1
		for col_num in range(len(row)):
			wl.write(row_num2, col_num, row[col_num], font_style)

	rows_j = journal.objects.filter(Company=company_details.pk).values_list('Date','voucher_id','voucher_type','By__name','To__name','Debit','Credit')

	for row in rows_j:
		row_num3 += 1
		for col_num in range(len(row)):
			wj.write(row_num3, col_num, row[col_num], font_style)

	rows_p = Particularspayment.objects.filter(payment__Company=company_details.pk).values_list('payment__date','payment__id','payment__account__name','particular__name','amount')

	for row in rows_p:
		row_num4 += 1
		for col_num in range(len(row)):
			wp.write(row_num4, col_num, row[col_num], font_style)

	rows_r = Particularsreceipt.objects.filter(receipt__Company=company_details.pk).values_list('receipt__date','receipt__id','receipt__account__name','particular__name','amount')

	for row in rows_r:
		row_num5 += 1
		for col_num in range(len(row)):
			wr.write(row_num5, col_num, row[col_num], font_style)

	rows_c = Particularscontra.objects.filter(contra__Company=company_details.pk).values_list('contra__date','contra__id','contra__account__name','particular__name','amount')

	for row in rows_c:
		row_num6 += 1
		for col_num in range(len(row)):
			wc.write(row_num6, col_num, row[col_num], font_style)

	rows_sg = Stockgroup.objects.filter(Company=company_details.pk).values_list('name','id','under__name')

	for row in rows_sg:
		row_num7 += 1
		for col_num in range(len(row)):
			wsg.write(row_num7, col_num, row[col_num], font_style)

	rows_sm = Simpleunits.objects.filter(Company=company_details.pk).values_list('symbol','id','formal')

	for row in rows_sm:
		row_num8 += 1
		for col_num in range(len(row)):
			wsm.write(row_num8, col_num, row[col_num], font_style)

	rows_cu = Compoundunits.objects.filter(Company=company_details.pk).values_list('firstunit','id','conversion','seconds_unit')

	for row in rows_cu:
		row_num9 += 1
		for col_num in range(len(row)):
			wcu.write(row_num9, col_num, row[col_num], font_style)

	rows_st = Stockdata.objects.filter(Company=company_details.pk).values_list('stock_name','id','unitsimple__symbol','Quantity','rate','opening','under__name','unitsimple__symbol')

	for row in rows_st:
		row_num10 += 1
		for col_num in range(len(row)):
			wst.write(row_num10, col_num, row[col_num], font_style)

	rows_pu = Purchase.objects.filter(Company=company_details.pk).values_list('date','id','ref_no','Party_ac__name','purchase__name','billname','Address','State','PAN','GSTIN','sub_total','cgst_alltotal','gst_alltotal','tax_alltotal','Total')

	for row in rows_pu:
		row_num11 += 1
		for col_num in range(len(row)):
			wpu.write(row_num11, col_num, row[col_num], font_style)


	rows_ps = Stock_Total.objects.filter(purchases__Company=company_details.pk).values_list('purchases__id','stockitem__stock_name','stockitem__unitsimple__symbol','Quantity_p','rate_p','Disc_p','gst_rate','stockitem__gst_rate','Total_p','cgst_total','gst_total','tax_total','grand_total')

	for row in rows_ps:
		row_num12 += 1
		for col_num in range(len(row)):
			wps.write(row_num12, col_num, row[col_num], font_style)

	rows_sa = Sales.objects.filter(Company=company_details.pk).values_list('date','id','ref_no','Party_ac__name','sales__name','billname','Address','State','PAN','GSTIN','sub_total','cgst_alltotal','gst_alltotal','tax_alltotal','Total')

	for row in rows_sa:
		row_num13 += 1
		for col_num in range(len(row)):
			wsa.write(row_num13, col_num, row[col_num], font_style)


	rows_ss = Stock_Total_sales.objects.filter(sales__Company=company_details.pk).values_list('sales__id','stockitem__stock_name','stockitem__unitsimple__symbol','Quantity','rate','Disc','gst_rate','stockitem__gst_rate','Total','cgst_total','gst_total','tax_total','grand_total')

	for row in rows_ss:
		row_num14 += 1
		for col_num in range(len(row)):
			wss.write(row_num14, col_num, row[col_num], font_style)

	rows_ss = stock_journal.objects.filter(Company=company_details.pk).values_list('stockitem__stock_name','stockitem__id','opening_stock','closing_quantity','closing_stock')

	for row in rows_ss:
		row_num15 += 1
		for col_num in range(len(row)):
			wsc.write(row_num15, col_num, row[col_num], font_style)

	wb.save(response)

	return response

@login_required
def company_upload(request):
	if request.method == 'POST':
		new_company = request.FILES['myfile']

		# call_command('loaddata', new_company)

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
			context['Products_legal'] = Product_activation.objects.filter(User=self.request.user,product__id = 10, is_active=True)
		return context

class companyDetailView(ProductExistsRequiredMixin,LoginRequiredMixin,DetailView):
	context_object_name = 'company_details'
	model = company
	template_name = 'company/Dashboard.html'

	def get_context_data(self, **kwargs):
		context = super(companyDetailView, self).get_context_data(**kwargs)
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		context['Products_legal'] = Product_activation.objects.filter(User=self.request.user,product__id = 10, is_active=True)
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

		capital_clo = company_details.Company_group.filter(group_Name__icontains='Capital Account').aggregate(the_sum=Coalesce(Sum('ledgergroups__Closing_balance'), Value(0)))['the_sum']
		capital_clo_m = company_details.Company_group.filter(Master__group_Name__icontains='Capital Account').aggregate(the_sum=Coalesce(Sum('ledgergroups__Closing_balance'), Value(0)))['the_sum']
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

		total_purchase 		= company_details.Company_group.filter(group_Name__icontains='Purchase Accounts').aggregate(the_sum=Coalesce(Sum('ledgergroups__Closing_balance'), Value(0)))['the_sum']
		total_sales 		= company_details.Company_group.filter(group_Name__icontains='Sales Account').aggregate(the_sum=Coalesce(Sum('ledgergroups__Closing_balance'), Value(0)))['the_sum']
		total_directexp 	= company_details.Company_group.filter(group_Name__icontains='Direct Expenses').aggregate(the_sum=Coalesce(Sum('ledgergroups__Closing_balance'), Value(0)))['the_sum']
		total_directinc 	= company_details.Company_group.filter(group_Name__icontains='Direct Incomes').aggregate(the_sum=Coalesce(Sum('ledgergroups__Closing_balance'), Value(0)))['the_sum']
		total_indirectexp 	= company_details.Company_group.filter(group_Name__icontains='Indirect Expense').aggregate(the_sum=Coalesce(Sum('ledgergroups__Closing_balance'), Value(0)))['the_sum']
		total_indirectinc 	= company_details.Company_group.filter(group_Name__icontains='Indirect Income').aggregate(the_sum=Coalesce(Sum('ledgergroups__Closing_balance'), Value(0)))['the_sum']
		
		

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

		# nett profit/loss calculation
		if gp >=0:
			if total_indirectinc < 0 and total_indirectexp < 0:
				np = (gp) + abs(total_indirectexp) - abs(total_indirectinc)
			elif total_indirectexp < 0:
				np = (gp) + abs(total_indirectinc) + abs(total_indirectexp)
			elif total_indirectinc < 0:
				np = (gp) - abs(total_indirectinc) - abs(total_indirectexp)
			else:
				np = (gp) + abs(total_indirectinc) - abs(total_indirectexp)
		else:
			if total_indirectinc < 0 and total_indirectexp < 0:
				np = abs(total_indirectexp) - abs(total_indirectinc) - abs(gp) 
			elif total_indirectinc < 0:
				np = abs(total_indirectinc) + abs(total_indirectexp) + abs(gp)
			elif total_indirectexp < 0:
				np = abs(total_indirectinc) + abs(total_indirectexp) - abs(gp)
			else:
				np = abs(total_indirectinc) - abs(total_indirectexp) - abs(gp) 


		if total_sales or total_sales != 0:
			context['gross_profit'] = (gp / total_sales) * 100
			context['nett_profit']	= (np / int(total_sales)) * 100
		else:
			context['gross_profit'] = 0	
			context['nett_profit']	= 0	

		context['nett_profit_total'] = np

		company_details.pl = np
		company_details.capital = capital_clo + capital_clo_m
		company_details.save()

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
						    Avg_purchase = Case(
						        When(quantity_purchase__gt=0, then=F('total_puchase') / F('quantity_purchase')),
						        default=None,
						        output_field=FloatField()
						    ),
						    Avg_sales = Case(
						        When(quantity__gt=0, then=F('total') / F('quantity')),
						        default=None,
						        output_field=FloatField()
						    )
						)


		results = collections.OrderedDict()
		result = Sales.objects.filter(Company=company_details.pk,date__gte=selectdatefield_details.Start_Date, date__lt=selectdatefield_details.End_Date).annotate(real_total = Case(When(sub_total__isnull=True, then=0),default=F('sub_total')))
		result_purchase = Purchase.objects.filter(Company=company_details.pk,date__gte=selectdatefield_details.Start_Date, date__lt=selectdatefield_details.End_Date).annotate(real_total_purchase = Case(When(sub_total__isnull=True, then=0),default=F('sub_total')))
		
		js_by_inexp  	= journal.objects.filter(Company=company_details.pk, By__group1_Name__group_Name__icontains='Indirect Expense', Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).annotate(real_total_debit = Case(When(Debit__isnull=True, then=0),default=F('Debit')))
		js_to_pur  	 	= journal.objects.filter(Company=company_details.pk, To__group1_Name__group_Name__icontains='Purchase Accounts', Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).annotate(real_total_credit = Case(When(Credit__isnull=True, then=0),default=F('Credit')))
		js_by_diexp  	= journal.objects.filter(Company=company_details.pk, By__group1_Name__group_Name__icontains='Direct Expenses', Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).annotate(real_total_debit = Case(When(Debit__isnull=True, then=0),default=F('Debit')))
		js_by_sal  	 	= journal.objects.filter(Company=company_details.pk, By__group1_Name__group_Name__icontains='Sales Account', Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).annotate(real_total_debit = Case(When(Debit__isnull=True, then=0),default=F('Debit')))
		js_by_diinc  	= journal.objects.filter(Company=company_details.pk, To__group1_Name__group_Name__icontains='Direct Incomes', Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).annotate(real_total_credit = Case(When(Credit__isnull=True, then=0),default=F('Credit')))
		js_by_ininc  	= journal.objects.filter(Company=company_details.pk, To__group1_Name__group_Name__icontains='Indirect Income', Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).annotate(real_total_credit = Case(When(Credit__isnull=True, then=0),default=F('Credit')))

		date_cursor = selectdatefield_details.Start_Date

		j = 0
		m = 0

		while date_cursor <= selectdatefield_details.End_Date:
			month_partial_total = result.filter(date__month=date_cursor.month).aggregate(partial_total=Sum('real_total'))['partial_total']
			month_partial_total_purchase = result_purchase.filter(date__month=date_cursor.month).aggregate(partial_total_purchase=Sum('real_total_purchase'))['partial_total_purchase']
			month_partial_total_inexp = js_by_inexp.filter(Date__month=date_cursor.month).aggregate(partial_total_debit=Sum('real_total_debit'))['partial_total_debit']
			month_partial_total_pur = js_to_pur.filter(Date__month=date_cursor.month).aggregate(partial_total_credit=Sum('real_total_credit'))['partial_total_credit']
			month_partial_total_diexp = js_by_diexp.filter(Date__month=date_cursor.month).aggregate(partial_total_debit=Sum('real_total_debit'))['partial_total_debit']
			month_partial_total_sal = js_by_sal.filter(Date__month=date_cursor.month).aggregate(partial_total_debit=Sum('real_total_debit'))['partial_total_debit']
			month_partial_total_diinc = js_by_diinc.filter(Date__month=date_cursor.month).aggregate(partial_total_credit=Sum('real_total_credit'))['partial_total_credit']
			month_partial_total_ininc = js_by_ininc.filter(Date__month=date_cursor.month).aggregate(partial_total_credit=Sum('real_total_credit'))['partial_total_credit']

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

			if month_partial_total_inexp == None:

				month_partial_total_inexp = int(0)

				g = month_partial_total_inexp 

			else:

				g = month_partial_total_inexp


			if month_partial_total_pur == None:

				month_partial_total_pur = int(0)

				f = month_partial_total_pur

			else:

				f = month_partial_total_pur

			if month_partial_total_diexp == None:

				month_partial_total_diexp = int(0)

				i = month_partial_total_diexp

			else:

				i = month_partial_total_diexp

			if month_partial_total_sal == None:

				month_partial_total_sal = int(0)

				h = month_partial_total_sal

			else:

				h = month_partial_total_sal

			if month_partial_total_sal == None:

				month_partial_total_diinc = int(0)

				k = month_partial_total_diinc

			else:

				k = month_partial_total_diinc

			if month_partial_total_ininc == None:

				month_partial_total_ininc = int(0)

				y = month_partial_total_ininc

			else:

				y = month_partial_total_ininc

			if h == 0 or f == 0 or i == 0 or k == 0:
				j = 0
			elif h == 0 and f == 0:
				j = j + k
			elif h == 0 and i == 0:
				j = j + k - f
			elif h == 0 and k == 0:
				j = j - f - i 
			elif k == 0 and f == 0:
				j = j + h - i 
			elif k == 0 and i == 0:
				j = j + h - f
			elif f == 0 and i == 0:
				j = j + h + k
			else:
				j = j + h + k - f - i  

			if y == 0 and g == 0:
				m = j
			elif y == 0:
				m = m + j - g
			elif g == 0:
				m = m + j + y
			else:
				m = m + j + y - g

			results[calendar.month_name[date_cursor.month]] =  [e,z,m]			

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
		context['Products_legal'] = Product_activation.objects.filter(User=self.request.user,product__id = 10, is_active=True)
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
		context['Products_legal'] = Product_activation.objects.filter(User=self.request.user,product__id = 10, is_active=True)
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
		Products_legal = Product_activation.objects.filter(product__id = 10, is_active=True)	
	else:
		Products_aggrement = Product_activation.objects.filter(product__id = 9, is_active=True)
		Products = Product_activation.objects.filter(User=request.user,product__id = 1, is_active=True)
		Todos = Todo.objects.filter(User=request.user,complete=False)
		Role_products = Role_product_activation.objects.filter(User=request.user,product__id = 1, is_active=True)
		Todos_total = Todo.objects.filter(User=request.user,complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		inbox = Message.objects.filter(reciever=request.user)
		inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		Products_legal = Product_activation.objects.filter(User=request.user,product__id = 10, is_active=True)

	context = {
		'company_details' 			: company_details,
		'inbox'			  			: inbox,
		'inbox_count'	  			: inbox_count,
		'send_count'	  			: send_count,
		'Products'		  			: Products,
		'Todos'			 			: Todos,
		'Todos_total' 	  			: Todos_total, 
		'Role_products' 			: Role_products,
		'Products_aggrement'		: Products_aggrement,
		'Products_legal' 			: Products_legal 

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
		Products_legal = Product_activation.objects.filter(product__id = 10, is_active=True)	
	else:
		Products_aggrement = Product_activation.objects.filter(product__id = 9, is_active=True)
		Products = Product_activation.objects.filter(User=request.user,product__id = 1, is_active=True)
		Todos = Todo.objects.filter(User=request.user,complete=False)
		Role_products = Role_product_activation.objects.filter(User=request.user,product__id = 1, is_active=True)
		Todos_total = Todo.objects.filter(User=request.user,complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		inbox = Message.objects.filter(reciever=request.user)
		inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		Products_legal = Product_activation.objects.filter(User=request.user,product__id = 10, is_active=True)

	context = {
		'company_details' 			: company_details,
		'inbox'			  			: inbox,
		'inbox_count'	  			: inbox_count,
		'send_count'	  			: send_count,
		'Products'		  			: Products,
		'Todos'			 			: Todos,
		'Todos_total' 	  			: Todos_total,
		'Role_products' 			: Role_products,
		'Products_aggrement' 		: Products_aggrement,
		'Products_legal' 			: Products_legal  

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

	if not request.user.is_authenticated:
		Products_aggrement = Product_activation.objects.filter(User=request.user,product__id = 9, is_active=True)
		Products = Product_activation.objects.filter(product__id = 1, is_active=True)
		Role_products = Role_product_activation.objects.filter(product__id = 1, is_active=True)
		Todos = Todo.objects.filter(complete=False)
		Todos_total = Todo.objects.filter(complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		inbox = Message.objects.all()
		inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		send_count = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		Products_legal = Product_activation.objects.filter(product__id = 10, is_active=True)	
	else:
		Products_aggrement = Product_activation.objects.filter(product__id = 9, is_active=True)
		Products = Product_activation.objects.filter(User=request.user,product__id = 1, is_active=True)
		Todos = Todo.objects.filter(User=request.user,complete=False)
		Role_products = Role_product_activation.objects.filter(User=request.user,product__id = 1, is_active=True)
		Todos_total = Todo.objects.filter(User=request.user,complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		inbox = Message.objects.filter(reciever=request.user)
		inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		Products_legal = Product_activation.objects.filter(User=request.user,product__id = 10, is_active=True)

	

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
		'Products_legal' 		: Products_legal

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
		Products_aggrement = Product_activation.objects.filter(User=request.user,product__id = 9, is_active=True)
		Products = Product_activation.objects.filter(product__id = 1, is_active=True)
		Role_products = Role_product_activation.objects.filter(product__id = 1, is_active=True)
		Todos = Todo.objects.filter(complete=False)
		Todos_total = Todo.objects.filter(complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		inbox = Message.objects.all()
		inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		send_count = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		Products_legal = Product_activation.objects.filter(product__id = 10, is_active=True)	
	else:
		Products_aggrement = Product_activation.objects.filter(product__id = 9, is_active=True)
		Products = Product_activation.objects.filter(User=request.user,product__id = 1, is_active=True)
		Todos = Todo.objects.filter(User=request.user,complete=False)
		Role_products = Role_product_activation.objects.filter(User=request.user,product__id = 1, is_active=True)
		Todos_total = Todo.objects.filter(User=request.user,complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		inbox = Message.objects.filter(reciever=request.user)
		inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		Products_legal = Product_activation.objects.filter(User=request.user,product__id = 10, is_active=True)

	context = {
		'company_details' 			: company_details,
		'inbox'			  			: inbox,
		'inbox_count'	  			: inbox_count,
		'send_count'	  			: send_count,
		'Products'		  			: Products,
		'Todos'			 			: Todos,
		'Todos_total' 	  			: Todos_total,
		'Role_products' 			: Role_products,
		'Products_aggrement' 		: Products_aggrement,
		'Products_legal' 			: Products_legal 

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

	if not request.user.is_authenticated:
		Products_aggrement = Product_activation.objects.filter(User=request.user,product__id = 9, is_active=True)
		Products = Product_activation.objects.filter(product__id = 1, is_active=True)
		Role_products = Role_product_activation.objects.filter(product__id = 1, is_active=True)
		Todos = Todo.objects.filter(complete=False)
		Todos_total = Todo.objects.filter(complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		inbox = Message.objects.all()
		inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		send_count = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		Products_legal = Product_activation.objects.filter(product__id = 10, is_active=True)	
	else:
		Products_aggrement = Product_activation.objects.filter(product__id = 9, is_active=True)
		Products = Product_activation.objects.filter(User=request.user,product__id = 1, is_active=True)
		Todos = Todo.objects.filter(User=request.user,complete=False)
		Role_products = Role_product_activation.objects.filter(User=request.user,product__id = 1, is_active=True)
		Todos_total = Todo.objects.filter(User=request.user,complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		inbox = Message.objects.filter(reciever=request.user)
		inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		Products_legal = Product_activation.objects.filter(User=request.user,product__id = 10, is_active=True)

	

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
		'Products_legal' 		: Products_legal

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
		Products_aggrement = Product_activation.objects.filter(User=request.user,product__id = 9, is_active=True)
		Products = Product_activation.objects.filter(product__id = 1, is_active=True)
		Role_products = Role_product_activation.objects.filter(product__id = 1, is_active=True)
		Todos = Todo.objects.filter(complete=False)
		Todos_total = Todo.objects.filter(complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		inbox = Message.objects.all()
		inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		send_count = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		Products_legal = Product_activation.objects.filter(product__id = 10, is_active=True)	
	else:
		Products_aggrement = Product_activation.objects.filter(product__id = 9, is_active=True)
		Products = Product_activation.objects.filter(User=request.user,product__id = 1, is_active=True)
		Todos = Todo.objects.filter(User=request.user,complete=False)
		Role_products = Role_product_activation.objects.filter(User=request.user,product__id = 1, is_active=True)
		Todos_total = Todo.objects.filter(User=request.user,complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		inbox = Message.objects.filter(reciever=request.user)
		inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		Products_legal = Product_activation.objects.filter(User=request.user,product__id = 10, is_active=True)

	context = {
		'company_details' 			: company_details,
		'inbox'			  			: inbox,
		'inbox_count'	  			: inbox_count,
		'send_count'	  			: send_count,
		'Products'		  			: Products,
		'Todos'			 			: Todos,
		'Todos_total' 	  			: Todos_total, 
		'Role_products' 			: Role_products,
		'Products_aggrement' 		: Products_aggrement,
		'Products_legal' 			: Products_legal

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

	if not request.user.is_authenticated:
		Products_aggrement = Product_activation.objects.filter(User=request.user,product__id = 9, is_active=True)
		Products = Product_activation.objects.filter(product__id = 1, is_active=True)
		Role_products = Role_product_activation.objects.filter(product__id = 1, is_active=True)
		Todos = Todo.objects.filter(complete=False)
		Todos_total = Todo.objects.filter(complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		inbox = Message.objects.all()
		inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		send_count = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		Products_legal = Product_activation.objects.filter(product__id = 10, is_active=True)	
	else:
		Products_aggrement = Product_activation.objects.filter(product__id = 9, is_active=True)
		Products = Product_activation.objects.filter(User=request.user,product__id = 1, is_active=True)
		Todos = Todo.objects.filter(User=request.user,complete=False)
		Role_products = Role_product_activation.objects.filter(User=request.user,product__id = 1, is_active=True)
		Todos_total = Todo.objects.filter(User=request.user,complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		inbox = Message.objects.filter(reciever=request.user)
		inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		Products_legal = Product_activation.objects.filter(User=request.user,product__id = 10, is_active=True)

	

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
		'Products_legal' 		: Products_legal,

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
		Products_aggrement = Product_activation.objects.filter(User=request.user,product__id = 9, is_active=True)
		Products = Product_activation.objects.filter(product__id = 1, is_active=True)
		Role_products = Role_product_activation.objects.filter(product__id = 1, is_active=True)
		Todos = Todo.objects.filter(complete=False)
		Todos_total = Todo.objects.filter(complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		inbox = Message.objects.all()
		inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		send_count = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		Products_legal = Product_activation.objects.filter(product__id = 10, is_active=True)	
	else:
		Products_aggrement = Product_activation.objects.filter(product__id = 9, is_active=True)
		Products = Product_activation.objects.filter(User=request.user,product__id = 1, is_active=True)
		Todos = Todo.objects.filter(User=request.user,complete=False)
		Role_products = Role_product_activation.objects.filter(User=request.user,product__id = 1, is_active=True)
		Todos_total = Todo.objects.filter(User=request.user,complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		inbox = Message.objects.filter(reciever=request.user)
		inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		Products_legal = Product_activation.objects.filter(User=request.user,product__id = 10, is_active=True)

	context = {
		'company_details' 			: company_details,
		'inbox'			  			: inbox,
		'inbox_count'	  			: inbox_count,
		'send_count'	  			: send_count,
		'Products'		  			: Products,
		'Todos'			 			: Todos,
		'Todos_total' 	  			: Todos_total,
		'Role_products' 			: Role_products,
		'Products_aggrement' 		: Products_aggrement,
		'Products_legal'            : Products_legal,

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

	if not request.user.is_authenticated:
		Products_aggrement = Product_activation.objects.filter(User=request.user,product__id = 9, is_active=True)
		Products = Product_activation.objects.filter(product__id = 1, is_active=True)
		Role_products = Role_product_activation.objects.filter(product__id = 1, is_active=True)
		Todos = Todo.objects.filter(complete=False)
		Todos_total = Todo.objects.filter(complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		inbox = Message.objects.all()
		inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		send_count = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		Products_legal = Product_activation.objects.filter(product__id = 10, is_active=True)	
	else:
		Products_aggrement = Product_activation.objects.filter(product__id = 9, is_active=True)
		Products = Product_activation.objects.filter(User=request.user,product__id = 1, is_active=True)
		Todos = Todo.objects.filter(User=request.user,complete=False)
		Role_products = Role_product_activation.objects.filter(User=request.user,product__id = 1, is_active=True)
		Todos_total = Todo.objects.filter(User=request.user,complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		inbox = Message.objects.filter(reciever=request.user)
		inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		Products_legal = Product_activation.objects.filter(User=request.user,product__id = 10, is_active=True)


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
		'Products_legal' 		: Products_legal,

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
		Products_aggrement = Product_activation.objects.filter(User=request.user,product__id = 9, is_active=True)
		Products = Product_activation.objects.filter(product__id = 1, is_active=True)
		Role_products = Role_product_activation.objects.filter(product__id = 1, is_active=True)
		Todos = Todo.objects.filter(complete=False)
		Todos_total = Todo.objects.filter(complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		inbox = Message.objects.all()
		inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		send_count = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		Products_legal = Product_activation.objects.filter(product__id = 10, is_active=True)	
	else:
		Products_aggrement = Product_activation.objects.filter(product__id = 9, is_active=True)
		Products = Product_activation.objects.filter(User=request.user,product__id = 1, is_active=True)
		Todos = Todo.objects.filter(User=request.user,complete=False)
		Role_products = Role_product_activation.objects.filter(User=request.user,product__id = 1, is_active=True)
		Todos_total = Todo.objects.filter(User=request.user,complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		inbox = Message.objects.filter(reciever=request.user)
		inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		Products_legal = Product_activation.objects.filter(User=request.user,product__id = 10, is_active=True)

	context = {
		'company_details' 			: company_details,
		'inbox'			  			: inbox,
		'inbox_count'	  			: inbox_count,
		'send_count'	  			: send_count,
		'Products'		  			: Products,
		'Todos'			 			: Todos,
		'Todos_total' 	  			: Todos_total, 
		'Role_products' 			: Role_products,
		'Products_aggrement' 		: Products_aggrement,
		'Products_legal' 			: Products_legal

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

	if not request.user.is_authenticated:
		Products_aggrement = Product_activation.objects.filter(User=request.user,product__id = 9, is_active=True)
		Products = Product_activation.objects.filter(product__id = 1, is_active=True)
		Role_products = Role_product_activation.objects.filter(product__id = 1, is_active=True)
		Todos = Todo.objects.filter(complete=False)
		Todos_total = Todo.objects.filter(complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		inbox = Message.objects.all()
		inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		send_count = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		Products_legal = Product_activation.objects.filter(product__id = 10, is_active=True)	
	else:
		Products_aggrement = Product_activation.objects.filter(product__id = 9, is_active=True)
		Products = Product_activation.objects.filter(User=request.user,product__id = 1, is_active=True)
		Todos = Todo.objects.filter(User=request.user,complete=False)
		Role_products = Role_product_activation.objects.filter(User=request.user,product__id = 1, is_active=True)
		Todos_total = Todo.objects.filter(User=request.user,complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		inbox = Message.objects.filter(reciever=request.user)
		inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		Products_legal = Product_activation.objects.filter(User=request.user,product__id = 10, is_active=True)
	

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
		'Products_legal' 		: Products_legal

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