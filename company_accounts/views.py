from django.shortcuts import render
from django.views.generic import (ListView,DetailView,
								  CreateView,UpdateView,DeleteView)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from accounting_double_entry.models import selectdatefield
from company_accounts.models import Purchase_accounts,Sales_accounts,Purchase_Total,Sales_total
from company_accounts.forms import Purchase_form,Sales_form,Purchase_formSet,Sales_ledger_formSet
from userprofile.models import Profile, Product_activation, Role_product_activation
from company.models import company
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
import datetime
import calendar
import dateutil
import collections   
from django.db import transaction  
from django.forms import inlineformset_factory
from django.http import JsonResponse
from django.template.loader import render_to_string
from ecommerce_integration.decorators import product_1_activation
from company_accounts.decorators import Company_only_accounts
from django.core.exceptions import PermissionDenied
from todogst.models import Todo
from messaging.models import Message 
from django.db.models.functions import Coalesce 
from django.db.models import Case, When, CharField, Value, Sum, F, Q, ExpressionWrapper, Subquery, OuterRef, Count
from django.db.models.fields import DecimalField


# Accounting product activation view
class ProductExistsRequiredMixin:

    def dispatch(self, request, *args, **kwargs):
        if Product_activation.objects.filter(User=self.request.user,product__id = 1, is_active=True) or Role_product_activation.objects.filter(User=request.user,product__id = 1, is_active=True):
            return super().dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

# Mixins for Companys having only accounts
class Company_with_accounts_mixins:

    def dispatch(self, request, *args, **kwargs):
        if company.objects.filter(maintain = 'Accounts Only'):
            return super().dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied


# Create your views here.

################################################### Group Views #################################################


class Purchase_accounts_listview(ProductExistsRequiredMixin,Company_with_accounts_mixins,LoginRequiredMixin,ListView):
	model = Purchase_accounts
	template_name = 'company_accounts/purchase/purchase_list.html'
	paginate_by = 15


	def get_queryset(self):
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		return self.model.objects.filter(Company=self.kwargs['pk'], date__gte=selectdatefield_details.Start_Date, date__lte=selectdatefield_details.End_Date).order_by('-id')

	def get_context_data(self, **kwargs):
		context = super(Purchase_accounts_listview, self).get_context_data(**kwargs) 
		context['profile_details'] = Profile.objects.all()
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		return context

class Purchase_accounts_detailsview(LoginRequiredMixin,Company_with_accounts_mixins,DetailView):
	context_object_name = 'purchase_details'
	model = Purchase_accounts
	template_name = 'company_accounts/purchase/purchase_details.html'

	def get_object(self):
		pk1 = self.kwargs['pk1']
		pk2 = self.kwargs['pk2']
		pk3 = self.kwargs['pk3']
		get_object_or_404(selectdatefield, pk=pk3)
		get_object_or_404(company, pk=pk1)
		purchase = get_object_or_404(Purchase_accounts, pk=pk2)
		return purchase


	def get_context_data(self, **kwargs):
		context = super(Purchase_accounts_detailsview, self).get_context_data(**kwargs) 
		company_details = get_object_or_404(company, pk=self.kwargs['pk1'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		purchase_details = get_object_or_404(Purchase_accounts, pk=self.kwargs['pk2'])
		qsob  = Stock_Total.objects.filter(purchases=purchase_details.pk)
		context['stocklist'] = qsob
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		return context

class Purchase_accounts_createview(ProductExistsRequiredMixin,Company_with_accounts_mixins,LoginRequiredMixin,CreateView):
	form_class  = Purchase_form
	template_name = 'company_accounts/purchase/purchase_form.html'

	def get_success_url(self,**kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		purchases = Purchase_accounts.objects.filter(Company=company_details.pk, date__gte=selectdatefield_details.Start_Date, date__lte=selectdatefield_details.End_Date).order_by('-id')
		for p in purchases:
			if p:
				return reverse('company_accounts:purchasedetail', kwargs={'pk1':company_details.pk, 'pk2':p.pk,'pk3':selectdatefield_details.pk})

	def get_context_data(self, **kwargs):
		context = super(Purchase_accounts_createview, self).get_context_data(**kwargs) 
		context['profile_details'] = Profile.objects.all()
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		if self.request.POST:
			context['stocks'] = Purchase_formSet(self.request.POST)
		else:
			context['stocks'] = Purchase_formSet()

		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		return context

	def form_valid(self, form):
		form.instance.User = self.request.user
		c = company.objects.get(pk=self.kwargs['pk'])
		form.instance.Company = c
		counter = Purchase.objects.filter(User=self.request.user, Company=c).count() + 1
		form.instance.counter = counter
		context = self.get_context_data()
		stocks = context['stocks']
		with transaction.atomic():
			self.object = form.save()
			if stocks.is_valid():
				stocks.instance = self.object
				stocks.save()
		return super(Purchase_accounts_createview, self).form_valid(form)

	def get_form_kwargs(self):
		data = super(Purchase_accounts_createview, self).get_form_kwargs()
		data.update(
			User=self.request.user,
			Company=company.objects.get(pk=self.kwargs['pk'])
			)
		return data


class Purchase_accounts_updateview(ProductExistsRequiredMixin,Company_with_accounts_mixins,LoginRequiredMixin,UpdateView):
	model = Purchase_accounts
	form_class  = Purchase_form
	template_name = 'company_accounts/purchase/purchase_form.html'


	def get_success_url(self,**kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk1'])
		purchase_details  = get_object_or_404(Purchase_accounts, pk=self.kwargs['pk2'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		return reverse('company_accounts:purchasedetail', kwargs={'pk1':company_details.pk, 'pk2':purchase_details.pk,'pk3':selectdatefield_details.pk})

	def get_object(self):
		pk1 = self.kwargs['pk1']
		pk2 = self.kwargs['pk2']
		get_object_or_404(company, pk=pk1)
		purchase = get_object_or_404(Purchase_accounts, pk=pk2)
		return purchase


	def get_context_data(self, **kwargs):
		context = super(Purchase_accounts_updateview, self).get_context_data(**kwargs)
		purchase_details  = get_object_or_404(Purchase_accounts, pk=self.kwargs['pk2'])
		purchases = Purchase_accounts.objects.get(pk=purchase_details.pk)
		context['profile_details'] = Profile.objects.all()
		company_details = get_object_or_404(company, pk=self.kwargs['pk1'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		if self.request.POST:
			context['stocks'] = Purchase_formSet(self.request.POST,instance=purchases)
		else:
			context['stocks'] = Purchase_formSet(instance=purchases)
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		return context

	def form_valid(self, form):
		form.instance.User = self.request.user
		c = company.objects.get(pk=self.kwargs['pk1'])
		form.instance.Company = c
		context = self.get_context_data()
		stockpurchase = context['stocks']
		if stockpurchase.is_valid():
			stockpurchase.save()
		return super(Purchase_accounts_updateview, self).form_valid(form)

	def get_form_kwargs(self):
		data = super(Purchase_accounts_updateview, self).get_form_kwargs()
		data.update(
			User=self.request.user,
			Company=company.objects.get(pk=self.kwargs['pk1'])
			)
		return data

class Purchase_accounts_deleteview(ProductExistsRequiredMixin,Company_with_accounts_mixins,LoginRequiredMixin,DeleteView):
	model = Purchase_accounts
	template_name = "company_accounts/purchase/purchase_confirm_delete.html"

	def get_success_url(self,**kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		return reverse('company_accounts:purchaselist', kwargs={'pk':company_details.pk, 'pk3':selectdatefield_details.pk})

	def get_object(self):
		pk1 = self.kwargs['pk']
		pk2 = self.kwargs['pk2']
		get_object_or_404(company, pk=pk1)
		purchase = get_object_or_404(Purchase_accounts, pk=pk2)
		return purchase

	def get_context_data(self, **kwargs):
		context = super(Purchase_accounts_deleteview, self).get_context_data(**kwargs) 
		context['profile_details'] = Profile.objects.all()
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		return context

##################################### Purchase Register Views #####################################

class Purchase_accounts_Register_view(ProductExistsRequiredMixin,Company_with_accounts_mixins,LoginRequiredMixin,ListView):
	model = Purchase_accounts
	template_name = 'company_accounts/purchase/Purchase_Register.html'

	def get_context_data(self, **kwargs):
		context = super(Purchase_accounts_Register_view, self).get_context_data(**kwargs)
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['company_details'] = company_details
		context['selectdatefield_details'] = selectdatefield_details

		results = collections.OrderedDict()
		result = Purchase_accounts.objects.filter(Company=company_details.pk,date__gte=selectdatefield_details.Start_Date, date__lt=selectdatefield_details.End_Date).annotate(real_total = Case(When(sub_total__isnull=True, then=0),default=F('sub_total')))
		date_cursor = selectdatefield_details.Start_Date

		z = 0

		while date_cursor <= selectdatefield_details.End_Date:
			month_partial_total = result.filter(date__month=date_cursor.month).aggregate(partial_total=Sum('real_total'))['partial_total']

			if month_partial_total == None:

				month_partial_total = int(0)

				e = month_partial_total

			else:

				e = month_partial_total


			z = z + e
			
			results[date_cursor.month] =  [e,z]			

			date_cursor += dateutil.relativedelta.relativedelta(months=1)

		total_purchase = result.aggregate(the_sum=Coalesce(Sum('real_total'), Value(0)))['the_sum']

		context['data'] = results.items()
		
		context['total_purchase'] = total_purchase
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		return context


@login_required
@product_1_activation
@Company_only_accounts
def purchase_accounts_register_datewise(request,month,pk,pk3):
	company_details = get_object_or_404(company, pk=pk)
	selectdatefield_details = get_object_or_404(selectdatefield, pk=pk3)

	result = Purchase_accounts.objects.filter(Company=company_details.pk, date__month=month, date__gte=selectdatefield_details.Start_Date, date__lt=selectdatefield_details.End_Date)

	total_purchase = result.aggregate(partial_total=Sum('sub_total'))['partial_total']

	inbox = Message.objects.filter(reciever=request.user)
	inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
	send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']


	context = {

		'company_details'             : company_details,
		'selectdatefield_details' 	  : selectdatefield_details,
		'result' 		  			  : result,
		'total_purchase' 			  : total_purchase,
		'm' 					  	  : calendar.month_name[int(month)],
		'inbox'						  : inbox,
		'inbox_count'				  : inbox_count,
		'send_count'				  : send_count,
		'Todos'					      : Todo.objects.filter(User=request.user, complete=False),
		'Todos_total' 			      : Todo.objects.filter(User=request.user, complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 

				
	}

	return render(request, 'company_accounts/purchase/Purchase_Register_Datewise.html', context)

##################################### Sales Register Views #####################################



class Sales_accounts_Register_view(ProductExistsRequiredMixin,Company_with_accounts_mixins,LoginRequiredMixin,ListView):
	model = Sales_accounts
	template_name = 'company_accounts/sales/Sales_Register.html'

	def get_context_data(self, **kwargs):
		context = super(Sales_accounts_Register_view, self).get_context_data(**kwargs)
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['company_details'] = company_details
		context['selectdatefield_details'] = selectdatefield_details

		results = collections.OrderedDict()
		result = Sales_accounts.objects.filter(Company=company_details.pk,date__gte=selectdatefield_details.Start_Date, date__lt=selectdatefield_details.End_Date).annotate(real_total = Case(When(sub_total__isnull=True, then=0),default=F('sub_total')))
		date_cursor = selectdatefield_details.Start_Date

		z = 0

		while date_cursor <= selectdatefield_details.End_Date:
			month_partial_total = result.filter(date__month=date_cursor.month).aggregate(partial_total=Sum('real_total'))['partial_total']

			if month_partial_total == None:

				month_partial_total = int(0)

				e = month_partial_total

			else:

				e = month_partial_total


			z = z + e
			

			results[date_cursor.month] =  [e,z]			

			date_cursor += dateutil.relativedelta.relativedelta(months=1)

		total_sale = result.aggregate(the_sum=Coalesce(Sum('real_total'), Value(0)))['the_sum']

		context['Debit'] = e
		context['data'] = results.items()
		
		context['total_sale'] = total_sale
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		return context


@login_required
@product_1_activation
@Company_only_accounts
def sales_accounts_register_datewise(request,month,pk,pk3):
	company_details = get_object_or_404(company, pk=pk)
	selectdatefield_details = get_object_or_404(selectdatefield, pk=pk3)

	result = Sales_accounts.objects.filter(Company=company_details.pk, date__month=month, date__gte=selectdatefield_details.Start_Date, date__lt=selectdatefield_details.End_Date)

	total_purchase = result.aggregate(partial_total=Sum('sub_total'))['partial_total']

	inbox = Message.objects.filter(reciever=request.user)
	inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
	send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']


	context = {

		'company_details'             : company_details,
		'selectdatefield_details' 	  : selectdatefield_details,
		'result' 		  			  : result,
		'total_purchase' 			  : total_purchase,
		'm' 					  	  : calendar.month_name[int(month)],
		'inbox'						  : inbox,
		'inbox_count'				  : inbox_count,
		'send_count'				  : send_count,
		'Todos'					      : Todo.objects.filter(User=request.user, complete=False),
		'Todos_total' 			      : Todo.objects.filter(User=request.user, complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 

				
	}

	return render(request, 'company_accounts/sales/Sales_Register_Datewise.html', context)


##################################### Sales Views #####################################


class Sales_accounts_listview(ProductExistsRequiredMixin,Company_with_accounts_mixins,LoginRequiredMixin,ListView):
	model = Sales_accounts
	template_name = 'company_accounts/sales/sales_list.html'

	def get_queryset(self):
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		return self.model.objects.filter(Company=self.kwargs['pk'], date__gte=selectdatefield_details.Start_Date, date__lte=selectdatefield_details.End_Date).order_by('-id')

	def get_context_data(self, **kwargs):
		context = super(Sales_accounts_listview, self).get_context_data(**kwargs) 
		context['profile_details'] = Profile.objects.all()
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		return context

class Sales_accounts_detailsview(ProductExistsRequiredMixin,Company_with_accounts_mixins,LoginRequiredMixin,DetailView):
	context_object_name = 'sales_details'
	model = Sales_accounts
	template_name = 'company_accounts/sales/sales_details.html'

	def get_object(self):
		pk1 = self.kwargs['pk1']
		pk2 = self.kwargs['pk2']
		pk3 = self.kwargs['pk3']
		get_object_or_404(selectdatefield, pk=pk3)
		get_object_or_404(company, pk=pk1)
		sales = get_object_or_404(Sales_accounts, pk=pk2)
		return sales


	def get_context_data(self, **kwargs):
		context = super(Sales_accounts_detailsview, self).get_context_data(**kwargs) 
		context['profile_details'] = Profile.objects.all()
		company_details = get_object_or_404(company, pk=self.kwargs['pk1'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		sales_details = get_object_or_404(Sales_accounts, pk=self.kwargs['pk2'])
		qsjb  = Stock_Total_sales.objects.filter(sales=sales_details.pk)
		context['stocklist'] = qsjb
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		return context

class Sales_accounts_createview(ProductExistsRequiredMixin,Company_with_accounts_mixins,LoginRequiredMixin,CreateView):
	form_class  = Sales_form
	template_name = 'company_accounts/sales/sales_form.html'

	def get_success_url(self,**kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		sales_list = Sales_accounts.objects.filter(Company=company_details.pk, date__gte=selectdatefield_details.Start_Date, date__lte=selectdatefield_details.End_Date).order_by('-id')
		for s in sales_list:
			if s:
				return reverse('company_accounts:salesdetail', kwargs={'pk1':company_details.pk, 'pk2':s.pk,'pk3':selectdatefield_details.pk})


	def form_valid(self, form):
		form.instance.User = self.request.user
		c = company.objects.get(pk=self.kwargs['pk'])
		form.instance.Company = c
		counter = Sales_accounts.objects.filter(User=self.request.user, Company=c).count() + 1
		form.instance.counter = counter
		context = self.get_context_data()
		salesledger = context['salesledger']
		with transaction.atomic():
			self.object = form.save()
			if salesledger.is_valid():
				salesledger.instance = self.object
				salesledger.save()
		return super(Sales_accounts_createview, self).form_valid(form)

	def get_form_kwargs(self):
		data = super(Sales_accounts_createview, self).get_form_kwargs()
		data.update(
			User=self.request.user,
			Company=company.objects.get(pk=self.kwargs['pk'])
			)
		return data

	def get_context_data(self, **kwargs):
		context = super(Sales_accounts_createview, self).get_context_data(**kwargs) 
		context['profile_details'] = Profile.objects.all()
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		if self.request.POST:
			context['salesledger'] = Sales_ledger_formSet(self.request.POST)
		else:
			context['salesledger'] = Sales_ledger_formSet()
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		return context

class Sales_accounts_updateview(ProductExistsRequiredMixin,Company_with_accounts_mixins,LoginRequiredMixin,UpdateView):
	model = Sales_accounts
	form_class  = Sales_form
	template_name = 'company_accounts/sales/sales_form.html'


	def get_success_url(self,**kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk1'])
		sales_details  = get_object_or_404(Sales_accounts, pk=self.kwargs['pk2'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		return reverse('company_accounts:salesdetail', kwargs={'pk1':company_details.pk, 'pk2':sales_details.pk,'pk3':selectdatefield_details.pk})

	def get_object(self):
		pk1 = self.kwargs['pk1']
		pk2 = self.kwargs['pk2']
		get_object_or_404(company, pk=pk1)
		sales = get_object_or_404(Sales_accounts, pk=pk2)
		return sales

	def get_context_data(self, **kwargs):
		context = super(Sales_accounts_updateview, self).get_context_data(**kwargs)
		sales_details  = get_object_or_404(Sales_accounts, pk=self.kwargs['pk2'])
		sales_particular = Sales_accounts.objects.get(pk=sales_details.pk)
		context['profile_details'] = Profile.objects.all()
		company_details = get_object_or_404(company, pk=self.kwargs['pk1'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		if self.request.POST:
			context['salesledger'] = Sales_ledger_formSet(self.request.POST, instance=sales_particular)
		else:
			context['salesledger'] = Sales_ledger_formSet(instance=sales_particular)
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		return context

	def form_valid(self, form):
		form.instance.User = self.request.user
		c = company.objects.get(pk=self.kwargs['pk1'])
		form.instance.Company = c
		context = self.get_context_data()
		salesledger = context['salesledger']
		if salesledger.is_valid():
			salesledger.save()
		return super(Sales_accounts_updateview, self).form_valid(form)

	def get_form_kwargs(self):
		data = super(Sales_accounts_updateview, self).get_form_kwargs()
		data.update(
			User=self.request.user,
			Company=company.objects.get(pk=self.kwargs['pk1'])
			)
		return data


class Sales_accounts_deleteview(ProductExistsRequiredMixin,Company_with_accounts_mixins,LoginRequiredMixin,DeleteView):
	model = Sales_accounts
	template_name = "company_accounts/sales/sales_confirm_delete.html"

	def get_success_url(self,**kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		return reverse('stockkeeping:saleslist', kwargs={'pk':company_details.pk, 'pk3':selectdatefield_details.pk})

	def get_object(self):
		pk1 = self.kwargs['pk']
		pk2 = self.kwargs['pk2']
		get_object_or_404(company, pk=pk1)
		sales = get_object_or_404(Sales_accounts, pk=pk2)
		return sales

	def get_context_data(self, **kwargs):
		context = super(Sales_accounts_deleteview, self).get_context_data(**kwargs) 
		context['profile_details'] = Profile.objects.all()
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		return context	