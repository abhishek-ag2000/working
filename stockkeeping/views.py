from django.shortcuts import render
from django.views.generic import (View,ListView,DetailView,
								  CreateView,UpdateView,DeleteView)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from accounting_double_entry.models import group1,ledger1,journal,selectdatefield,Pl_journal
from company.models import company
from stockkeeping.models import stock_journal,Stockgroup,Simpleunits,Compoundunits,Stockdata,Purchase,Sales,Stock_Total,Stock_Total_sales
from stockkeeping.forms import Stockgroup_form,Simpleunits_form,Compoundunits_form,Stockdata_form,Purchase_form,Sales_form,Purchase_formSet,Sales_formSet,Stock_Totalform
from userprofile.models import Profile, Product_activation, Role_product_activation
from messaging.models import Message
from ecommerce_integration.models import coupon, Product, Product_review, Services, API
from todogst.models import Todo
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models.functions import Coalesce
from django.db.models import Case, When, CharField, Value, Sum, Count, F,Q, ExpressionWrapper, Subquery, OuterRef, FloatField
from django.db.models.fields import DecimalField
import calendar
import dateutil
import collections
from ecommerce_integration.decorators import product_1_activation
from stockkeeping.decorators import Company_only_accounts
from django.core.exceptions import PermissionDenied
from itertools import zip_longest
from dateutil.rrule import rrule, MONTHLY
# Create your views here.


class ProductExistsRequiredMixin:

    def dispatch(self, request, *args, **kwargs):
        if Product_activation.objects.filter(User=self.request.user,product__id = 1, is_active=True) or Role_product_activation.objects.filter(User=request.user,product__id = 1, is_active=True):
            return super().dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied


# Mixins for Companys having Accounts with Inventory
class Company_only_accounts_mixins:

	def dispatch(self, request, *args, **kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		if company.objects.filter(pk=company_details.pk,maintain = 'Accounts with Inventory'):
			return super().dispatch(request, *args, **kwargs)
		else:
			raise PermissionDenied

class Company_accounts_inventory_mixins:

	def dispatch(self, request, *args, **kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk1'])
		if company.objects.filter(pk=company_details.pk,maintain = 'Accounts with Inventory'):
			return super().dispatch(request, *args, **kwargs)
		else:
			raise PermissionDenied

##################################### Simple Unit Views #####################################

class Simpleunits_listview(ProductExistsRequiredMixin,Company_only_accounts_mixins,LoginRequiredMixin,ListView):
	model = Simpleunits
	template_name = 'stockkeeping/simpleunits/simpleunits_list.html'
	paginate_by = 15


	def get_queryset(self):
		return self.model.objects.filter(Company=self.kwargs['pk'])

	def get_context_data(self, **kwargs):
		context = super(Simpleunits_listview, self).get_context_data(**kwargs) 
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

class Simpleunits_detailsview(ProductExistsRequiredMixin,Company_accounts_inventory_mixins,LoginRequiredMixin,DetailView):
	context_object_name = 'simpleunits_details'
	model = Simpleunits
	template_name = 'stockkeeping/simpleunits/simpleunits_details.html'

	def get_object(self):
		pk1 = self.kwargs['pk1']
		pk2 = self.kwargs['pk2']
		pk3 = self.kwargs['pk3']
		get_object_or_404(selectdatefield, pk=pk3)
		get_object_or_404(company, pk=pk1)
		simpleunit = get_object_or_404(Simpleunits, pk=pk2)
		return simpleunit


	def get_context_data(self, **kwargs):
		context = super(Simpleunits_detailsview, self).get_context_data(**kwargs) 
		context['profile_details'] = Profile.objects.all()
		company_details = get_object_or_404(company, pk=self.kwargs['pk1'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		return context

class Simpleunits_createview(ProductExistsRequiredMixin,Company_only_accounts_mixins,LoginRequiredMixin,CreateView):
	form_class  = Simpleunits_form
	template_name = "stockkeeping/simpleunits/simpleunits_form.html"

	def get_success_url(self,**kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		return reverse('stockkeeping:simplelist', kwargs={'pk':company_details.pk, 'pk3':selectdatefield_details.pk})

	def form_valid(self, form):
		form.instance.User = self.request.user
		c = company.objects.get(pk=self.kwargs['pk'])
		form.instance.Company = c
		counter = Simpleunits.objects.filter(User=self.request.user, Company=c).count() + 1
		form.instance.counter = counter
		return super(Simpleunits_createview, self).form_valid(form)

	def get_context_data(self, **kwargs):
		context = super(Simpleunits_createview, self).get_context_data(**kwargs) 
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

class Simpleunits_updateview(ProductExistsRequiredMixin,Company_accounts_inventory_mixins,LoginRequiredMixin,UpdateView):
	model = Simpleunits
	form_class  = Simpleunits_form
	template_name = "stockkeeping/simpleunits/simpleunits_form.html"


	def get_success_url(self,**kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk1'])
		simpleunits_details  = get_object_or_404(Simpleunits, pk=self.kwargs['pk2'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		return reverse('stockkeeping:simpledetail', kwargs={'pk1':company_details.pk, 'pk2':group1_details.pk,'pk3':selectdatefield_details.pk})

	def get_object(self):
		pk1 = self.kwargs['pk1']
		pk2 = self.kwargs['pk2']
		get_object_or_404(company, pk=pk1)
		simpleunit = get_object_or_404(Simpleunits, pk=pk2)
		return simpleunit

	def get_context_data(self, **kwargs):
		context = super(Simpleunits_updateview, self).get_context_data(**kwargs) 
		context['profile_details'] = Profile.objects.all()
		company_details = get_object_or_404(company, pk=self.kwargs['pk1'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		return context


class Simpleunits_deleteview(ProductExistsRequiredMixin,Company_only_accounts_mixins,LoginRequiredMixin,DeleteView):
	model = Simpleunits
	template_name = "stockkeeping/simpleunits/simpleunits_confirm_delete.html"

	def get_success_url(self,**kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		return reverse('stockkeeping:simplelist', kwargs={'pk':company_details.pk, 'pk3':selectdatefield_details.pk})

	def get_object(self):
		pk = self.kwargs['pk']
		pk2 = self.kwargs['pk2']
		get_object_or_404(company, pk=pk)
		simpleunit = get_object_or_404(Simpleunits, pk=pk2)
		return simpleunit

	def get_context_data(self, **kwargs):
		context = super(Simpleunits_deleteview, self).get_context_data(**kwargs) 
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


##################################### Compound Unit Views #####################################



class Compoundunit_listview(ProductExistsRequiredMixin,Company_only_accounts_mixins,LoginRequiredMixin,ListView):
	model = Compoundunits
	template_name = 'stockkeeping/compoundunits/compoundunits_list.html'
	paginate_by = 15


	def get_queryset(self):
		return self.model.objects.filter(Company=self.kwargs['pk'])

	def get_context_data(self, **kwargs):
		context = super(Compoundunit_listview, self).get_context_data(**kwargs) 
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


class Compoundunits_detailsview(ProductExistsRequiredMixin,Company_accounts_inventory_mixins,LoginRequiredMixin,DetailView):
	context_object_name = 'compoundunits_details'
	model = Compoundunits
	template_name = 'stockkeeping/compoundunits/compoundunits_details.html'

	def get_object(self):
		pk1 = self.kwargs['pk1']
		pk2 = self.kwargs['pk2']
		pk3 = self.kwargs['pk3']
		get_object_or_404(selectdatefield, pk=pk3)
		get_object_or_404(company, pk=pk1)
		compoundunit = get_object_or_404(Compoundunits, pk=pk2)
		return compoundunit


	def get_context_data(self, **kwargs):
		context = super(Compoundunits_detailsview, self).get_context_data(**kwargs) 
		context['profile_details'] = Profile.objects.all()
		company_details = get_object_or_404(company, pk=self.kwargs['pk1'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		return context

class Compoundunits_createview(ProductExistsRequiredMixin,Company_only_accounts_mixins,LoginRequiredMixin,CreateView):
	form_class  = Compoundunits_form
	template_name = "stockkeeping/compoundunits/compoundunits_form.html"

	def get_success_url(self,**kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		return reverse('stockkeeping:compoundlist', kwargs={'pk':company_details.pk, 'pk3':selectdatefield_details.pk})

	def form_valid(self, form):
		form.instance.User = self.request.user
		c = company.objects.get(pk=self.kwargs['pk'])
		form.instance.Company = c
		counter = Compoundunits.objects.filter(User=self.request.user, Company=c).count() + 1
		form.instance.counter = counter
		return super(Compoundunits_createview, self).form_valid(form)

	def get_form_kwargs(self):
		data = super(Compoundunits_createview, self).get_form_kwargs()
		data.update(
			User=self.request.user,
			Company=company.objects.get(pk=self.kwargs['pk'])
			)
		return data

	def get_context_data(self, **kwargs):
		context = super(Compoundunits_createview, self).get_context_data(**kwargs) 
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

class Compoundunits_updateview(ProductExistsRequiredMixin,Company_accounts_inventory_mixins,LoginRequiredMixin,UpdateView):
	model = Compoundunits
	form_class  = Compoundunits_form
	template_name = "stockkeeping/compoundunits/compoundunits_form.html"


	def get_success_url(self,**kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk1'])
		compoundunits_details  = get_object_or_404(Compoundunits, pk=self.kwargs['pk2'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		return reverse('stockkeeping:compounddetail', kwargs={'pk1':company_details.pk, 'pk2':compoundunits_details.pk,'pk3':selectdatefield_details.pk})

	def get_object(self):
		pk1 = self.kwargs['pk1']
		pk2 = self.kwargs['pk2']
		get_object_or_404(company, pk=pk1)
		compoundunit = get_object_or_404(Compoundunits, pk=pk2)
		return compoundunit

	def get_form_kwargs(self):
		data = super(Compoundunits_updateview, self).get_form_kwargs()
		data.update(
			User=self.request.user,
			Company=company.objects.get(pk=self.kwargs['pk1'])
			)
		return data

	def get_context_data(self, **kwargs):
		context = super(Compoundunits_updateview, self).get_context_data(**kwargs) 
		context['profile_details'] = Profile.objects.all()
		company_details = get_object_or_404(company, pk=self.kwargs['pk1'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		return context

class Compoundunits_deleteview(ProductExistsRequiredMixin,Company_only_accounts_mixins,LoginRequiredMixin,DeleteView):
	model = Compoundunits
	template_name = "stockkeeping/compoundunits/compoundunits_confirm_delete.html"

	def get_success_url(self,**kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		return reverse('stockkeeping:compoundlist', kwargs={'pk':company_details.pk, 'pk3':selectdatefield_details.pk})

	def get_object(self):
		pk1 = self.kwargs['pk']
		pk2 = self.kwargs['pk2']
		get_object_or_404(company, pk=pk1)
		compoundunit = get_object_or_404(Compoundunits, pk=pk2)
		return compoundunit

	def get_context_data(self, **kwargs):
		context = super(Compoundunits_deleteview, self).get_context_data(**kwargs) 
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

		
##################################### Stockgroup Views #####################################

class Stockgroup_listview(ProductExistsRequiredMixin,Company_only_accounts_mixins,LoginRequiredMixin,ListView):
	model = Stockgroup
	template_name = 'stockkeeping/stockgroup/stockgroup_list.html'
	paginate_by = 15


	def get_queryset(self):
		return self.model.objects.filter(Company=self.kwargs['pk'])

	def get_context_data(self, **kwargs):
		context = super(Stockgroup_listview, self).get_context_data(**kwargs) 
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

class Stockgroup_detailsview(ProductExistsRequiredMixin,Company_accounts_inventory_mixins,LoginRequiredMixin,DetailView):
	context_object_name = 'stockgrp_details'
	model = Stockgroup
	template_name = 'stockkeeping/stockgroup/stockgroup_details.html'

	def get_object(self):
		pk1 = self.kwargs['pk1']
		pk2 = self.kwargs['pk2']
		pk3 = self.kwargs['pk3']
		get_object_or_404(selectdatefield, pk=pk3)
		get_object_or_404(company, pk=pk1)
		stockgroup = get_object_or_404(Stockgroup, pk=pk2)
		return Stockgroup


	def get_context_data(self, **kwargs):
		context = super(Stockgroup_detailsview, self).get_context_data(**kwargs) 
		context['profile_details'] = Profile.objects.all()
		stockgrp_details = get_object_or_404(Stockgroup, pk=self.kwargs['pk2'])
		context['stockgrp_details'] = stockgrp_details
		company_details = get_object_or_404(company, pk=self.kwargs['pk1'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		return context

class Stockgroup_createview(ProductExistsRequiredMixin,Company_only_accounts_mixins,LoginRequiredMixin,CreateView):
	form_class  = Stockgroup_form
	template_name = "stockkeeping/stockgroup/stockgroup_form.html"

	def get_success_url(self,**kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		return reverse('stockkeeping:stockgrouplist', kwargs={'pk':company_details.pk, 'pk3':selectdatefield_details.pk})

	def form_valid(self, form):
		form.instance.User = self.request.user
		c = company.objects.get(pk=self.kwargs['pk'])
		form.instance.Company = c
		counter = Stockgroup.objects.filter(User=self.request.user, Company=c).count() + 1
		form.instance.counter = counter
		return super(Stockgroup_createview, self).form_valid(form)

	def get_form_kwargs(self):
		data = super(Stockgroup_createview, self).get_form_kwargs()
		data.update(
			User=self.request.user,
			Company=company.objects.get(pk=self.kwargs['pk'])
			)
		return data

	def get_context_data(self, **kwargs):
		context = super(Stockgroup_createview, self).get_context_data(**kwargs) 
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

class Stockgroup_updateview(ProductExistsRequiredMixin,Company_accounts_inventory_mixins,LoginRequiredMixin,UpdateView):
	model = Stockgroup
	form_class  = Stockgroup_form
	template_name = "stockkeeping/stockgroup/stockgroup_form.html"


	def get_success_url(self,**kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk1'])
		stockgroup_details  = get_object_or_404(Stockgroup, pk=self.kwargs['pk2'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		return reverse('stockkeeping:stockgroupdetail', kwargs={'pk1':company_details.pk, 'pk2':stockgroup_details.pk,'pk3':selectdatefield_details.pk})

	def get_object(self):
		pk1 = self.kwargs['pk1']
		pk2 = self.kwargs['pk2']
		get_object_or_404(company, pk=pk1)
		stockgroup = get_object_or_404(Stockgroup, pk=pk2)
		return stockgroup

	def get_form_kwargs(self):
		data = super(Stockgroup_updateview, self).get_form_kwargs()
		data.update(
			User=self.request.user,
			Company=company.objects.get(pk=self.kwargs['pk1'])
			)
		return data

	def get_context_data(self, **kwargs):
		context = super(Stockgroup_updateview, self).get_context_data(**kwargs) 
		context['profile_details'] = Profile.objects.all()
		company_details = get_object_or_404(company, pk=self.kwargs['pk1'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		return context

class Stockgroup_deleteview(ProductExistsRequiredMixin,Company_only_accounts_mixins,LoginRequiredMixin,DeleteView):
	model = Stockgroup
	template_name = "stockkeeping/stockgroup/stockgroup_confirm_delete.html"

	def get_success_url(self,**kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		return reverse('stockkeeping:stockgrouplist', kwargs={'pk':company_details.pk, 'pk3':selectdatefield_details.pk})

	def get_object(self):
		pk1 = self.kwargs['pk']
		pk2 = self.kwargs['pk2']
		get_object_or_404(company, pk=pk1)
		stockgroup = get_object_or_404(Stockgroup, pk=pk2)
		return stockgroup

	def get_context_data(self, **kwargs):
		context = super(Stockgroup_deleteview, self).get_context_data(**kwargs) 
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

##################################### Stockitems Monthly Views #####################################

@login_required
@product_1_activation
@Company_only_accounts
def Stockitems_Monthly_view(request, pk, pk2, pk3):
	company_details = get_object_or_404(company, pk=pk)
	selectdatefield_details = get_object_or_404(selectdatefield, pk=pk3)
	stockdata_details = get_object_or_404(Stockdata, pk=pk2)


	opening_balance = stockdata_details.opening
	opening_quantity = stockdata_details.Quantity
	results = collections.OrderedDict()
	result1 = Stock_Total_sales.objects.filter(sales__Company=company_details.pk, stockitem=stockdata_details.pk, sales__date__gte=selectdatefield_details.Start_Date, sales__date__lt=selectdatefield_details.End_Date).annotate(real_total_quantity_s = Case(When(Quantity__isnull=True, then=0),default=F('Quantity')))
	result2 = Stock_Total.objects.filter(purchases__Company=company_details.pk, stockitem=stockdata_details.pk, purchases__date__gte=selectdatefield_details.Start_Date, purchases__date__lt=selectdatefield_details.End_Date).annotate(real_total_quantity_p = Case(When(Quantity_p__isnull=True, then=0),default=F('Quantity_p')))
	result3 = Stock_Total.objects.filter(purchases__Company=company_details.pk, stockitem=stockdata_details.pk, purchases__date__gte=selectdatefield_details.Start_Date, purchases__date__lt=selectdatefield_details.End_Date).annotate(real_total_p = Case(When(Total_p__isnull=True, then=0),default=F('Total_p')))
	result4 = Stock_Total_sales.objects.filter(sales__Company=company_details.pk, stockitem=stockdata_details.pk, sales__date__gte=selectdatefield_details.Start_Date, sales__date__lt=selectdatefield_details.End_Date).annotate(real_total_s = Case(When(Total__isnull=True, then=0),default=F('Total')))

	date_cursor = selectdatefield_details.Start_Date

	w = 0
	x = 0
	y = 0
	z = 0

	while date_cursor <= selectdatefield_details.End_Date:
		month_partial_purchase_quantity = result2.filter(purchases__date__month=date_cursor.month).aggregate(partial_total_purchase_quantity=Sum('real_total_quantity_p'))['partial_total_purchase_quantity']
		month_partial_sale_quantity = result1.filter(sales__date__month=date_cursor.month).aggregate(partial_total_sale_quantity=Sum('real_total_quantity_s'))['partial_total_sale_quantity']
		month_partial_purchase = result3.filter(purchases__date__month=date_cursor.month).aggregate(partial_total_purchase=Sum('real_total_p'))['partial_total_purchase']
		month_partial_sale = result4.filter(sales__date__month=date_cursor.month).aggregate(partial_total_sale=Sum('real_total_s'))['partial_total_sale']

		if month_partial_purchase_quantity == None:

			month_partial_purchase_quantity = int(0)
			e = month_partial_purchase_quantity
		else:
			e = month_partial_purchase_quantity

		if month_partial_sale_quantity == None:

			month_partial_sale_quantity = int(0)
			f = month_partial_sale_quantity
		else:
			f = month_partial_sale_quantity	

		if month_partial_purchase == None:

			month_partial_purchase = int(0)
			g = month_partial_purchase
		else:
			g = month_partial_purchase


		if month_partial_sale == None:

			month_partial_sale = int(0)
			h = month_partial_sale
		else:
			h = month_partial_sale


		w = w + e - f

		x = x + e 

		y = y + g 

		if x == 0:
			z = ((y + opening_balance) * (w + opening_quantity))
		else:
			z = ((y + opening_balance) / (x + opening_quantity) * (w + opening_quantity))			

		results[date_cursor.month] =  [w,e,f,g,h,z]			
		date_cursor += dateutil.relativedelta.relativedelta(months=1)

	total_purchase_quantity = result2.aggregate(the_sum=Coalesce(Sum('real_total_quantity_p'), Value(0)))['the_sum']
	total_sale_quantity = result1.aggregate(the_sum=Coalesce(Sum('real_total_quantity_s'), Value(0)))['the_sum']
	total_purchase = result3.aggregate(the_sum=Coalesce(Sum('real_total_p'), Value(0)))['the_sum']
	total_sale = result4.aggregate(the_sum=Coalesce(Sum('real_total_s'), Value(0)))['the_sum']


	Closing_balance = z

	inbox = Message.objects.filter(reciever=request.user)
	inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
	send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']


	context = {

		'company_details'             : company_details,
		'stockdata_details'           : stockdata_details,
		'selectdatefield_details' 	  : selectdatefield_details,
		'total_purchase_quantity'     : total_purchase_quantity,
		'total_sale_quantity'         : total_sale_quantity,
		'total_purchase'			  : total_purchase,
		'total_sale'                  : total_sale,
		'data'			              : results.items(),
		'Closing_balance'			  : Closing_balance,
		'inbox'						  : inbox,
		'inbox_count'				  : inbox_count,
		'send_count'				  : send_count,
		'Todos'					      : Todo.objects.filter(User=request.user, complete=False),
		'Todos_total' 			      : Todo.objects.filter(User=request.user, complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 

				
	}

	return render(request, 'stockkeeping/stockitem/Stock_Monthly.html', context)

@login_required
@product_1_activation
@Company_only_accounts
def stock_summary_datewise(request,month,pk,pk2,pk3):
	company_details = get_object_or_404(company, pk=pk)
	selectdatefield_details = get_object_or_404(selectdatefield, pk=pk3)
	stockdata_details = get_object_or_404(Stockdata, pk=pk2)


	result1 = Stock_Total_sales.objects.filter(sales__Company=company_details.pk, stockitem=stockdata_details.pk, sales__date__month=month, sales__date__gte=selectdatefield_details.Start_Date, sales__date__lt=selectdatefield_details.End_Date)
	result2 = Stock_Total.objects.filter(purchases__Company=company_details.pk, stockitem=stockdata_details.pk, purchases__date__month=month, purchases__date__gte=selectdatefield_details.Start_Date, purchases__date__lt=selectdatefield_details.End_Date)
	result3 = Stock_Total.objects.filter(purchases__Company=company_details.pk, stockitem=stockdata_details.pk, purchases__date__month=month, purchases__date__gte=selectdatefield_details.Start_Date, purchases__date__lt=selectdatefield_details.End_Date)
	result4 = Stock_Total_sales.objects.filter(sales__Company=company_details.pk, stockitem=stockdata_details.pk, sales__date__month=month, sales__date__gte=selectdatefield_details.Start_Date, sales__date__lt=selectdatefield_details.End_Date)

	new   = zip_longest(result1,result2)
	
	total_purchase_quantity = result2.aggregate(the_sum=Coalesce(Sum('Quantity_p'), Value(0)))['the_sum']
	total_sale_quantity = result1.aggregate(the_sum=Coalesce(Sum('Quantity'), Value(0)))['the_sum']
	total_purchase = result3.aggregate(the_sum=Coalesce(Sum('Total_p'), Value(0)))['the_sum']
	total_sale = result4.aggregate(the_sum=Coalesce(Sum('Total'), Value(0)))['the_sum']



	qs  = Stock_Total_sales.objects.filter(sales__Company=company_details.pk, stockitem=stockdata_details.pk, sales__date__month__gte=selectdatefield_details.Start_Date.month, sales__date__month__lte=month)
	qs2 = Stock_Total.objects.filter(purchases__Company=company_details.pk, stockitem=stockdata_details.pk, purchases__date__month__gte=selectdatefield_details.Start_Date.month, purchases__date__month__lte=month)
	qs3 = Stock_Total.objects.filter(purchases__Company=company_details.pk, stockitem=stockdata_details.pk, purchases__date__month__gte=selectdatefield_details.Start_Date.month, purchases__date__month__lte=month)
	qs4 = Stock_Total_sales.objects.filter(sales__Company=company_details.pk, stockitem=stockdata_details.pk, sales__date__month__gte=selectdatefield_details.Start_Date.month, sales__date__month__lte=month)	
	

	total_debit = qs.aggregate(the_sum=Coalesce(Sum('Quantity'), Value(0)))['the_sum']
	total_credit = qs2.aggregate(the_sum=Coalesce(Sum('Quantity_p'), Value(0)))['the_sum']
	total_debitpl = qs3.aggregate(the_sum=Coalesce(Sum('Total_p'), Value(0)))['the_sum']
	total_creditpl = qs4.aggregate(the_sum=Coalesce(Sum('Total'), Value(0)))['the_sum']

	closing_quantity = stockdata_details.Quantity + total_credit - total_debit

	if total_credit != 0:
		closing_balance = (((total_debitpl + stockdata_details.opening) / (total_credit + stockdata_details.Quantity)) * closing_quantity)
	else: 
		closing_balance = ((total_debitpl + stockdata_details.opening) * (closing_quantity + stockdata_details.Quantity))


	inbox = Message.objects.filter(reciever=request.user)
	inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
	send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']


	context = {

		'company_details'             : company_details,
		'selectdatefield_details' 	  : selectdatefield_details,
		'stockdata_details' 		  : stockdata_details,
		'm' 					  	  : calendar.month_name[int(month)],
		'new' 						  : new,
		'closing_quantity' 			  : closing_quantity,
		'closing_balance' 			  : closing_balance,
		'total_purchase_quantity' 	  : total_purchase_quantity,
		'total_sale_quantity' 		  : total_sale_quantity,
		'total_purchase' 			  : total_purchase,
		'total_sale' 				  : total_sale,
		'inbox'						  : inbox,
		'inbox_count'				  : inbox_count,
		'send_count'				  : send_count,
		'Todos'					      : Todo.objects.filter(User=request.user, complete=False),
		'Todos_total' 			      : Todo.objects.filter(User=request.user, complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 

				
	}

	return render(request, 'stockkeeping/stockitem/stock_daily.html', context)



##################################### Stockitems Views #####################################

class closing_list_view(ProductExistsRequiredMixin,Company_only_accounts_mixins,LoginRequiredMixin,ListView):
	model = Stockdata
	paginate_by = 15

	def get_template_names(self):
		if True:  
			return ['stockkeeping/closing_stock.html']
		else:
			return ['stockkeeping/stockitem/stockdata_list.html']


	def get_queryset(self):
		return self.model.objects.filter(Company=self.kwargs['pk']).order_by('-id')

	def get_context_data(self, **kwargs):
		context = super(closing_list_view, self).get_context_data(**kwargs) 
		context['profile_details'] = Profile.objects.all()
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		context['stock_journal'] = stock_journal.objects.filter(Company=company_details.pk).order_by('-closing_stock') 
		# qs = Stockdata.objects.filter(Company=company_details.pk)
		# qs = qs.annotate(
  #   		sales_sum = Subquery(
  #   			Stock_Total_sales.objects.filter(sales__Company=company_details.pk,
  #   				stockitem = OuterRef('pk'),sales__date__gte=selectdatefield_details.Start_Date, sales__date__lt=selectdatefield_details.End_Date
  #   				).values(
  #   					'stockitem'
  #   				).annotate(
  #   					the_sum = Sum('Quantity')
  #   				).values('the_sum'),
  #   			output_field=FloatField()),
  #   		purchase_sum =  Subquery(
  #   			Stock_Total.objects.filter(purchases__Company=company_details.pk,
  #   				stockitem = OuterRef('pk'),purchases__date__gte=selectdatefield_details.Start_Date, purchases__date__lt=selectdatefield_details.End_Date
  #   				).values(
  #   					'stockitem'
  #   				).annotate(
  #   					the_sum = Sum('Quantity_p')
  #   				).values(
  #   					'the_sum'
  #   				),
  #   			output_field=FloatField()),
  #   		purchase_tot = Subquery(
  #   			Stock_Total.objects.filter(purchases__Company=company_details.pk,
  #   				stockitem = OuterRef('pk'),purchases__date__gte=selectdatefield_details.Start_Date, purchases__date__lt=selectdatefield_details.End_Date
  #   				).values(
  #   					'stockitem'
  #   				).annotate(
  #   					the_sum = Sum('Total_p')
  #   				).values(
  #   					'the_sum'
  #   				),
  #   			output_field=FloatField()),
		# )

		# qs1 = qs.annotate(
	 #    	difference = ExpressionWrapper(F('purchase_sum') - F('sales_sum'), output_field=FloatField()),
	 #    	total = ExpressionWrapper((F('purchase_tot') / F('purchase_sum')) * (F('purchase_sum') - F('sales_sum')), output_field=FloatField())
		# ) 
		# context['Totalquantity'] = qs1.values()
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		return context

class Stockdata_listview(LoginRequiredMixin,Company_only_accounts_mixins,ListView):
	model = Stockdata
	template_name = 'stockkeeping/stockitem/stockdata_list.html'
	paginate_by = 15


	def get_queryset(self):
		return self.model.objects.filter(Company=self.kwargs['pk'])

	def get_context_data(self, **kwargs):
		context = super(Stockdata_listview, self).get_context_data(**kwargs)
		context['profile_details'] = Profile.objects.all()
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		context['stockdata_list'] =  Stockdata.objects.filter(Company=company_details.pk)
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		return context


class Stockdata_detailsview(ProductExistsRequiredMixin,Company_accounts_inventory_mixins,LoginRequiredMixin,DetailView):
	context_object_name = 'stockdata_details'
	model = Stockdata
	template_name = 'stockkeeping/stockitem/stockdata_details.html'

	def get_object(self):
		pk1 = self.kwargs['pk1']
		pk2 = self.kwargs['pk2']
		pk3 = self.kwargs['pk3']
		get_object_or_404(selectdatefield, pk=pk3)
		get_object_or_404(company, pk=pk1)
		stockdata = get_object_or_404(Stockdata, pk=pk2)
		return stockdata


	def get_context_data(self, **kwargs):
		context = super(Stockdata_detailsview, self).get_context_data(**kwargs) 
		context['profile_details'] = Profile.objects.all()
		company_details = get_object_or_404(company, pk=self.kwargs['pk1'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		return context

class Stockdata_createview(ProductExistsRequiredMixin,Company_only_accounts_mixins,LoginRequiredMixin,CreateView):
	form_class  = Stockdata_form
	template_name = "stockkeeping/stockitem/stockdata_form.html"

	def get_success_url(self,**kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		return reverse('stockkeeping:stockdatalist', kwargs={'pk':company_details.pk, 'pk3':selectdatefield_details.pk})

	def form_valid(self, form):
		form.instance.User = self.request.user
		c = company.objects.get(pk=self.kwargs['pk'])
		form.instance.Company = c
		counter = Stockdata.objects.filter(User=self.request.user, Company=c).count() + 1
		form.instance.counter = counter
		return super(Stockdata_createview, self).form_valid(form)

	def get_form_kwargs(self):
		data = super(Stockdata_createview, self).get_form_kwargs()
		data.update(
			User=self.request.user,
			Company=company.objects.get(pk=self.kwargs['pk'])
			)
		return data

	def get_context_data(self, **kwargs):
		context = super(Stockdata_createview, self).get_context_data(**kwargs) 
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

class Stockdata_updateview(ProductExistsRequiredMixin,Company_accounts_inventory_mixins,LoginRequiredMixin,UpdateView):
	model = Stockdata
	form_class  = Stockdata_form
	template_name = "stockkeeping/stockitem/stockdata_form.html"


	def get_success_url(self,**kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk1'])
		stockdata_details  = get_object_or_404(Stockdata, pk=self.kwargs['pk2'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		return reverse('stockkeeping:stockdatadetail', kwargs={'pk1':company_details.pk, 'pk2':stockdata_details.pk,'pk3':selectdatefield_details.pk})

	def get_object(self):
		pk1 = self.kwargs['pk1']
		pk2 = self.kwargs['pk2']
		get_object_or_404(company, pk=pk1)
		stockdata = get_object_or_404(Stockdata, pk=pk2)
		return stockdata

	def get_form_kwargs(self):
		data = super(Stockdata_updateview, self).get_form_kwargs()
		data.update(
			User=self.request.user,
			Company=company.objects.get(pk=self.kwargs['pk1'])
			)
		return data

	def get_context_data(self, **kwargs):
		context = super(Stockdata_updateview, self).get_context_data(**kwargs) 
		context['profile_details'] = Profile.objects.all()
		company_details = get_object_or_404(company, pk=self.kwargs['pk1'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		return context

class Stockdata_deleteview(ProductExistsRequiredMixin,Company_only_accounts_mixins,LoginRequiredMixin,DeleteView):
	model = Stockdata
	template_name = "stockkeeping/stockitem/stockdataunits_confirm_delete.html"

	def get_success_url(self,**kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		return reverse('stockkeeping:stockdatalist', kwargs={'pk':company_details.pk, 'pk3':selectdatefield_details.pk})

	def get_object(self):
		pk1 = self.kwargs['pk']
		pk2 = self.kwargs['pk2']
		get_object_or_404(company, pk=pk1)
		compoundunit = get_object_or_404(Stockdata, pk=pk2)
		return compoundunit

	def get_context_data(self, **kwargs):
		context = super(Stockdata_deleteview, self).get_context_data(**kwargs) 
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

##################################### Purchase Views with inventory #####################################

class Purchase_listview(ProductExistsRequiredMixin,Company_only_accounts_mixins,LoginRequiredMixin,ListView):
	model = Purchase
	template_name = 'stockkeeping/purchase/purchase_list.html'
	paginate_by = 15


	def get_queryset(self):
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		return self.model.objects.filter(Company=self.kwargs['pk'], date__gte=selectdatefield_details.Start_Date, date__lte=selectdatefield_details.End_Date).order_by('-id')

	def get_context_data(self, **kwargs):
		context = super(Purchase_listview, self).get_context_data(**kwargs) 
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


class Purchase_detailsview(LoginRequiredMixin,Company_accounts_inventory_mixins,DetailView):
	context_object_name = 'purchase_details'
	model = Purchase
	template_name = 'stockkeeping/purchase/purchase_details.html'

	def get_object(self):
		pk1 = self.kwargs['pk1']
		pk2 = self.kwargs['pk2']
		pk3 = self.kwargs['pk3']
		get_object_or_404(selectdatefield, pk=pk3)
		get_object_or_404(company, pk=pk1)
		purchase = get_object_or_404(Purchase, pk=pk2)
		return purchase


	def get_context_data(self, **kwargs):
		context = super(Purchase_detailsview, self).get_context_data(**kwargs) 
		company_details = get_object_or_404(company, pk=self.kwargs['pk1'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		purchase_details = get_object_or_404(Purchase, pk=self.kwargs['pk2'])
		qsob  = Stock_Total.objects.filter(purchases=purchase_details.pk)
		context['stocklist'] = qsob
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		return context

class Purchase_createview(ProductExistsRequiredMixin,Company_only_accounts_mixins,LoginRequiredMixin,CreateView):
	form_class  = Purchase_form
	template_name = 'stockkeeping/purchase/purchase_form.html'

	def get_success_url(self,**kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		purchases = Purchase.objects.filter(Company=company_details.pk, date__gte=selectdatefield_details.Start_Date, date__lte=selectdatefield_details.End_Date).order_by('-id')
		for p in purchases:
			if p:
				return reverse('stockkeeping:purchasedetail', kwargs={'pk1':company_details.pk, 'pk2':p.pk,'pk3':selectdatefield_details.pk})

	def get_context_data(self, **kwargs):
		context = super(Purchase_createview, self).get_context_data(**kwargs) 
		context['profile_details'] = Profile.objects.all()
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		if self.request.POST:
			context['stocks'] = Purchase_formSet(self.request.POST, form_kwargs = {'Company': company_details.pk})
		else:
			context['stocks'] = Purchase_formSet(form_kwargs = {'Company': company_details.pk})

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
		return super(Purchase_createview, self).form_valid(form)

	def get_form_kwargs(self):
		data = super(Purchase_createview, self).get_form_kwargs()
		data.update(
			User=self.request.user,
			Company=company.objects.get(pk=self.kwargs['pk'])
			)
		return data



class Purchase_updateview(ProductExistsRequiredMixin,Company_accounts_inventory_mixins,LoginRequiredMixin,UpdateView):
	model = Purchase
	form_class  = Purchase_form
	template_name = 'stockkeeping/purchase/purchase_form.html'


	def get_success_url(self,**kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk1'])
		purchase_details  = get_object_or_404(Purchase, pk=self.kwargs['pk2'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		return reverse('stockkeeping:purchasedetail', kwargs={'pk1':company_details.pk, 'pk2':purchase_details.pk,'pk3':selectdatefield_details.pk})

	def get_object(self):
		pk1 = self.kwargs['pk1']
		pk2 = self.kwargs['pk2']
		get_object_or_404(company, pk=pk1)
		purchase = get_object_or_404(Purchase, pk=pk2)
		return purchase


	def get_context_data(self, **kwargs):
		context = super(Purchase_updateview, self).get_context_data(**kwargs)
		purchase_details  = get_object_or_404(Purchase, pk=self.kwargs['pk2'])
		purchases = Purchase.objects.get(pk=purchase_details.pk)
		context['profile_details'] = Profile.objects.all()
		company_details = get_object_or_404(company, pk=self.kwargs['pk1'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		if self.request.POST:
			context['stocks'] = Purchase_formSet(self.request.POST,instance=purchases, form_kwargs = {'Company': company_details.pk})
		else:
			context['stocks'] = Purchase_formSet(instance=purchases, form_kwargs = {'Company': company_details.pk})
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
		return super(Purchase_updateview, self).form_valid(form)

	def get_form_kwargs(self):
		data = super(Purchase_updateview, self).get_form_kwargs()
		data.update(
			User=self.request.user,
			Company=company.objects.get(pk=self.kwargs['pk1'])
			)
		return data

class Purchase_deleteview(ProductExistsRequiredMixin,Company_only_accounts_mixins,LoginRequiredMixin,DeleteView):
	model = Purchase
	template_name = "stockkeeping/purchase/purchase_confirm_delete.html"

	def get_success_url(self,**kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		return reverse('stockkeeping:purchaselist', kwargs={'pk':company_details.pk, 'pk3':selectdatefield_details.pk})

	def get_object(self):
		pk1 = self.kwargs['pk']
		pk2 = self.kwargs['pk2']
		get_object_or_404(company, pk=pk1)
		purchase = get_object_or_404(Purchase, pk=pk2)
		return purchase

	def get_context_data(self, **kwargs):
		context = super(Purchase_deleteview, self).get_context_data(**kwargs) 
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

class Purchase_Register_view(ProductExistsRequiredMixin,Company_only_accounts_mixins,LoginRequiredMixin,ListView):
	model = Purchase
	template_name = 'stockkeeping/purchase/Purchase_Register.html'

	def get_context_data(self, **kwargs):
		context = super(Purchase_Register_view, self).get_context_data(**kwargs)
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['company_details'] = company_details
		context['selectdatefield_details'] = selectdatefield_details

		results = collections.OrderedDict()
		result = Purchase.objects.filter(Company=company_details.pk,date__gte=selectdatefield_details.Start_Date, date__lt=selectdatefield_details.End_Date).annotate(real_total = Case(When(sub_total__isnull=True, then=0),default=F('sub_total')))
		date_cursor = selectdatefield_details.Start_Date

		z = 0

		while date_cursor <= selectdatefield_details.End_Date:
			print(date_cursor.month)
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
def purchase_register_datewise(request,month,pk,pk3):
	company_details = get_object_or_404(company, pk=pk)
	selectdatefield_details = get_object_or_404(selectdatefield, pk=pk3)

	result = Purchase.objects.filter(Company=company_details.pk, date__month=month, date__gte=selectdatefield_details.Start_Date, date__lt=selectdatefield_details.End_Date)

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

	return render(request, 'stockkeeping/purchase/Purchase_Register_Datewise.html', context)


##################################### Sales Register Views #####################################



class Sales_Register_view(ProductExistsRequiredMixin,Company_only_accounts_mixins,LoginRequiredMixin,ListView):
	model = Sales
	template_name = 'stockkeeping/sales/Sales_Register.html'

	def get_context_data(self, **kwargs):
		context = super(Sales_Register_view, self).get_context_data(**kwargs)
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['company_details'] = company_details
		context['selectdatefield_details'] = selectdatefield_details

		results = collections.OrderedDict()
		result = Sales.objects.filter(Company=company_details.pk,date__gte=selectdatefield_details.Start_Date, date__lt=selectdatefield_details.End_Date).annotate(real_total = Case(When(sub_total__isnull=True, then=0),default=F('sub_total')))
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
def sales_register_datewise(request,month,pk,pk3):
	company_details = get_object_or_404(company, pk=pk)
	selectdatefield_details = get_object_or_404(selectdatefield, pk=pk3)

	result = Sales.objects.filter(Company=company_details.pk, date__month=month, date__gte=selectdatefield_details.Start_Date, date__lt=selectdatefield_details.End_Date)

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

	return render(request, 'stockkeeping/sales/Sales_Register_Datewise.html', context)


##################################### Sales Views #####################################

class Sales_listview(ProductExistsRequiredMixin,Company_only_accounts_mixins,LoginRequiredMixin,ListView):
	model = Sales
	template_name = 'stockkeeping/sales/sales_list.html'
	paginate_by = 15


	def get_queryset(self):
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		return self.model.objects.filter(Company=self.kwargs['pk'], date__gte=selectdatefield_details.Start_Date, date__lte=selectdatefield_details.End_Date).order_by('-id')

	def get_context_data(self, **kwargs):
		context = super(Sales_listview, self).get_context_data(**kwargs) 
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



class Sales_detailsview(ProductExistsRequiredMixin,Company_accounts_inventory_mixins,LoginRequiredMixin,DetailView):
	context_object_name = 'sales_details'
	model = Sales
	template_name = 'stockkeeping/sales/sales_details.html'

	def get_object(self):
		pk1 = self.kwargs['pk1']
		pk2 = self.kwargs['pk2']
		pk3 = self.kwargs['pk3']
		get_object_or_404(selectdatefield, pk=pk3)
		get_object_or_404(company, pk=pk1)
		sales = get_object_or_404(Sales, pk=pk2)
		return sales


	def get_context_data(self, **kwargs):
		context = super(Sales_detailsview, self).get_context_data(**kwargs) 
		context['profile_details'] = Profile.objects.all()
		company_details = get_object_or_404(company, pk=self.kwargs['pk1'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		sales_details = get_object_or_404(Sales, pk=self.kwargs['pk2'])
		qsjb  = Stock_Total_sales.objects.filter(sales=sales_details.pk)
		context['stocklist'] = qsjb
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		return context

class Sales_createview(ProductExistsRequiredMixin,Company_only_accounts_mixins,LoginRequiredMixin,CreateView):
	form_class  = Sales_form
	template_name = 'stockkeeping/sales/sales_form.html'

	def get_success_url(self,**kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		sales_list = Sales.objects.filter(Company=company_details.pk, date__gte=selectdatefield_details.Start_Date, date__lte=selectdatefield_details.End_Date).order_by('-id')
		for s in sales_list:
			if s:
				return reverse('stockkeeping:salesdetail', kwargs={'pk1':company_details.pk, 'pk2':s.pk,'pk3':selectdatefield_details.pk})


	def form_valid(self, form):
		form.instance.User = self.request.user
		c = company.objects.get(pk=self.kwargs['pk'])
		form.instance.Company = c
		counter = Sales.objects.filter(User=self.request.user, Company=c).count() + 1
		form.instance.counter = counter
		context = self.get_context_data()
		stocksales = context['stocksales']
		with transaction.atomic():
			self.object = form.save()
			if stocksales.is_valid():
				stocksales.instance = self.object
				stocksales.save()
		return super(Sales_createview, self).form_valid(form)

	def get_form_kwargs(self):
		data = super(Sales_createview, self).get_form_kwargs()
		data.update(
			User=self.request.user,
			Company=company.objects.get(pk=self.kwargs['pk']),
			)
		return data

	def get_context_data(self, **kwargs):
		context = super(Sales_createview, self).get_context_data(**kwargs) 
		context['profile_details'] = Profile.objects.all()
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		if self.request.POST:
			context['stocksales'] = Sales_formSet(self.request.POST, form_kwargs = {'Company': company_details.pk})
		else:
			context['stocksales'] = Sales_formSet(form_kwargs = {'Company': company_details.pk})
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		return context





class Sales_updateview(ProductExistsRequiredMixin,Company_accounts_inventory_mixins,LoginRequiredMixin,UpdateView):
	model = Sales
	form_class  = Sales_form
	template_name = 'stockkeeping/sales/sales_form.html'


	def get_success_url(self,**kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk1'])
		sales_details  = get_object_or_404(Sales, pk=self.kwargs['pk2'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		return reverse('stockkeeping:salesdetail', kwargs={'pk1':company_details.pk, 'pk2':sales_details.pk,'pk3':selectdatefield_details.pk})

	def get_object(self):
		pk1 = self.kwargs['pk1']
		pk2 = self.kwargs['pk2']
		get_object_or_404(company, pk=pk1)
		sales = get_object_or_404(Sales, pk=pk2)
		return sales

	def get_context_data(self, **kwargs):
		context = super(Sales_updateview, self).get_context_data(**kwargs)
		sales_details  = get_object_or_404(Sales, pk=self.kwargs['pk2'])
		sales_particular = Sales.objects.get(pk=sales_details.pk)
		context['profile_details'] = Profile.objects.all()
		company_details = get_object_or_404(company, pk=self.kwargs['pk1'])
		context['company_details'] = company_details
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		context['selectdatefield_details'] = selectdatefield_details
		if self.request.POST:
			context['stocksales'] = Sales_formSet(self.request.POST, instance=sales_particular, form_kwargs = {'Company': company_details.pk})
		else:
			context['stocksales'] = Sales_formSet(instance=sales_particular, form_kwargs = {'Company': company_details.pk})
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
		stocksales = context['stocksales']
		if stocksales.is_valid():
			stocksales.save()
		return super(Sales_updateview, self).form_valid(form)

	def get_form_kwargs(self):
		data = super(Sales_updateview, self).get_form_kwargs()
		data.update(
			User=self.request.user,
			Company=company.objects.get(pk=self.kwargs['pk1'])
			)
		return data



class Sales_deleteview(ProductExistsRequiredMixin,Company_only_accounts_mixins,LoginRequiredMixin,DeleteView):
	model = Sales
	template_name = "stockkeeping/sales/sales_confirm_delete.html"

	def get_success_url(self,**kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		return reverse('stockkeeping:saleslist', kwargs={'pk':company_details.pk, 'pk3':selectdatefield_details.pk})

	def get_object(self):
		pk1 = self.kwargs['pk']
		pk2 = self.kwargs['pk2']
		get_object_or_404(company, pk=pk1)
		sales = get_object_or_404(Sales, pk=pk2)
		return sales

	def get_context_data(self, **kwargs):
		context = super(Sales_deleteview, self).get_context_data(**kwargs) 
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



##################################### Stock_Total #####################################

class Stock_Total_createview(ProductExistsRequiredMixin,Company_only_accounts_mixins,LoginRequiredMixin,CreateView):
	form_class  = Stock_Totalform
	template_name = 'stockkeeping/purchase/purchase_form.html'

	def get_success_url(self,**kwargs):
		company_details = get_object_or_404(company, pk=self.kwargs['pk'])
		selectdatefield_details = get_object_or_404(selectdatefield, pk=self.kwargs['pk3'])
		return reverse('stockkeeping:purchaselist', kwargs={'pk':company_details.pk, 'pk3':selectdatefield_details.pk})

	def get_context_data(self, **kwargs):
		context = super(Stock_Total_createview, self).get_context_data(**kwargs) 
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

	def form_valid(self, form):
		form.instance.User = self.request.user

		c = company.objects.get(pk=self.kwargs['pk'])
		form.instance.Company = c

	def get_form_kwargs(self):
		data = super(Stock_Total_createview, self).get_form_kwargs()
		data.update(
			User=self.request.user,
			Company=company.objects.get(pk=self.kwargs['pk'])

			)
		return data



##################################### Profit & Loss A/c #####################################


@login_required
@product_1_activation
def profit_and_loss_view(request,pk,pk3):
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


	if  lddi < 0 and lddt < 0:
		gp = abs(ldsc) + abs(qs2) + abs(lddt) - abs(qo2) - abs(ldc) - abs(lddi)
	elif lddt < 0:
		gp = abs(ldsc) + abs(qs2) + abs(lddi) + abs(lddt) - abs(qo2) - abs(ldc)
	elif lddi < 0:
		gp = abs(ldsc) + abs(qs2) - abs(lddi) - abs(qo2) - abs(ldc) - abs(lddt)
	else:	
		gp = abs(ldsc) + abs(qs2) + abs(lddi) - abs(qo2) - abs(ldc) - abs(lddt)


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


	return render(request, 'stockkeeping/P&L.html', context)

##################################### Trial Balance #####################################

@login_required
@product_1_activation
def trial_balance_view(request,pk,pk3):
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
	return render(request, 'stockkeeping/Trial_Balance/trial_bal.html', context)



##################################### Balance Sheet #####################################

@login_required
@product_1_activation
def balance_sheet_view(request,pk,pk3):
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

	return render(request, 'stockkeeping/balance_sheet.html', context)



