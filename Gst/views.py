from django.shortcuts import render
from django.views.generic import (TemplateView,ListView,DetailView,
								  CreateView,UpdateView,DeleteView)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from ecommerce_integration.models import coupon, Product, Product_review, Services, API
from Gst.models import Gst_input,Gst_output,Stock_gst
from accounting_double_entry.models import journal,group1,ledger1,selectdatefield,Payment,Particularspayment,Receipt,Particularsreceipt,Contra,Particularscontra,Multijournal,Multijournaltotal
from stockkeeping.models import Stockgroup,Simpleunits,Compoundunits,Stockdata,Purchase,Sales,Stock_Total,Stock_Total_sales
from django.core.exceptions import PermissionDenied
from ecommerce_integration.decorators import product_1_activation
from django.shortcuts import get_object_or_404
from company.models import company
from userprofile.models import Profile, Product_activation, Role_product_activation
from todogst.models import Todo
from messaging.models import Message 
from itertools import zip_longest
from django.db.models import Case, When, CharField, Value, Sum, F, Q, ExpressionWrapper, Subquery, OuterRef, Count
from django.db.models.fields import DecimalField
from django.db.models.functions import Coalesce 
# Create your views here.



class ProductExistsRequiredMixin:

    def dispatch(self, request, *args, **kwargs):
        if Product_activation.objects.filter(User=self.request.user,product__id = 1, is_active=True) or Role_product_activation.objects.filter(User=request.user,product__id = 1, is_active=True):
            return super().dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied


class Gstr_1(ProductExistsRequiredMixin,TemplateView):
    template_name = "Gst/gstr1.html"

    def get_context_data(self, **kwargs):
        context = super(Gstr_1, self).get_context_data(**kwargs) 
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
    


class Gstr_2A(ProductExistsRequiredMixin,TemplateView):
    template_name = "Gst/gstr_2A.html"

    def get_context_data(self, **kwargs):
        context = super(Gstr_2A, self).get_context_data(**kwargs) 
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

class Gstr_3B(ProductExistsRequiredMixin,TemplateView):
    template_name = "Gst/gstr_3B.html"

    def get_context_data(self, **kwargs):
        context = super(Gstr_3B, self).get_context_data(**kwargs) 
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

class income_tax(ProductExistsRequiredMixin,TemplateView):
    template_name = "income_tax/income_tax.html"

    def get_context_data(self, **kwargs):
        context = super(income_tax, self).get_context_data(**kwargs) 
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
