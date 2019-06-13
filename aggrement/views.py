from django.shortcuts import render
from aggrement.models import Aggrement, User_aggrement
from django.views.generic import (ListView,DetailView,
								  CreateView,UpdateView,DeleteView)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from aggrement.forms import User_aggrement_form, Aggrement_form
from django.db.models.functions import Coalesce 
from django.db.models import Case, When, CharField, Value, Sum, F, Q, ExpressionWrapper, Subquery, OuterRef, Count
from todogst.models import Todo
from messaging.models import Message 
from userprofile.models import Profile, Product_activation, Role_product_activation, Role_product_activation, Post, Post_comment, Pro_services, achivements, Organisation, Organisation_member
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
import json
from django.core import serializers
from django.http import HttpResponse
from datetime import datetime
# Create your views here.

class ProductExistsRequiredMixin:

    def dispatch(self, request, *args, **kwargs):
        if Product_activation.objects.filter(User=self.request.user,product__id = 9, is_active=True):
            return super().dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

@login_required
def get_aggrement_Object(request):
	all_objects = Aggrement.objects.all()
	data = serializers.serialize('json', all_objects)
	data = json.dumps(json.loads(data), indent=4)
	response = HttpResponse(data , content_type='application/json')
	response['Content-Disposition'] = 'attachment; filename={}-{}.json'.format('Aggrement',datetime.now()) 
	return response

@login_required
def aggrement_upload(request):
	if request.method == 'POST':
		new_aggreement = request.FILES['myfile']

		obj_generator = serializers.json.Deserializer(new_aggreement)
		
		for obj in obj_generator:
			obj.save()

	return render(request, 'aggrement/import_aggrement.html')



class Aggrement_List_View(ProductExistsRequiredMixin,LoginRequiredMixin,ListView):
	model = Aggrement
	paginate_by = 25
	template_name = 'aggrement/aggrement_list.html'

	def get_queryset(self):
		return self.model.objects.all().order_by('id')

	def get_context_data(self, **kwargs):
		context = super(Aggrement_List_View, self).get_context_data(**kwargs) 
		context['aggrement_list'] = Aggrement.objects.all().order_by('id')
		context['aggrement_count'] = Aggrement.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['Products'] = Product_activation.objects.filter(User=self.request.user,product__id = 1, is_active=True)
		context['Products_aggrement'] = Product_activation.objects.filter(User=self.request.user,product__id = 9, is_active=True)
		context['Role_products'] = Role_product_activation.objects.filter(User=self.request.user,product__id = 1, is_active=True)
		context['Products_legal'] = Product_activation.objects.filter(User=self.request.user,product__id = 10, is_active=True)
		return context


class Aggrement_createview(LoginRequiredMixin,CreateView):
	form_class = Aggrement_form
	template_name = 'aggrement/only_aggrement_form.html'


	def get_context_data(self, **kwargs):
		context = super(Aggrement_createview, self).get_context_data(**kwargs)
		context['Products_aggrement'] = Product_activation.objects.filter(User=self.request.user,product__id = 9, is_active=True)
		context['Products'] = Product_activation.objects.filter(User=self.request.user,product__id = 1, is_active=True)
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		context['Products_legal'] = Product_activation.objects.filter(User=self.request.user,product__id = 10, is_active=True)
		return context




class Saved_aggrement_List_View(ProductExistsRequiredMixin,LoginRequiredMixin,ListView):
	model = User_aggrement
	paginate_by = 25
	template_name = 'aggrement/saved_aggrement_saved_list.html'

	def get_queryset(self):
		return self.model.objects.all().order_by('id')

	def get_context_data(self, **kwargs):
		context = super(Saved_aggrement_List_View, self).get_context_data(**kwargs) 
		context['aggrement_list'] = User_aggrement.objects.all().order_by('id')
		context['aggrement_count'] = User_aggrement.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['Products'] = Product_activation.objects.filter(User=self.request.user,product__id = 1, is_active=True)
		context['Products_aggrement'] = Product_activation.objects.filter(User=self.request.user,product__id = 9, is_active=True)
		context['Role_products'] = Role_product_activation.objects.filter(User=self.request.user,product__id = 1, is_active=True)
		context['Products_legal'] = Product_activation.objects.filter(User=self.request.user,product__id = 10, is_active=True)
		return context



class Aggrement_update_view(ProductExistsRequiredMixin,LoginRequiredMixin,UpdateView):
	model = User_aggrement
	form_class  = User_aggrement_form
	template_name = "aggrement/aggrement_form.html"


	def get_success_url(self,**kwargs):
		return reverse('aggrement:saved_aggrement')


	def get_context_data(self, **kwargs):
		context = super(Aggrement_update_view, self).get_context_data(**kwargs) 
		aggrement_details = get_object_or_404(Aggrement, pk=self.kwargs['pk1'])
		context['aggrement_details'] = aggrement_details
		context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
		context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		context['inbox'] = Message.objects.filter(reciever=self.request.user)
		context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		context['Products'] = Product_activation.objects.filter(User=self.request.user,product__id = 1, is_active=True)
		context['Products_aggrement'] = Product_activation.objects.filter(User=self.request.user,product__id = 9, is_active=True)
		context['Role_products'] = Role_product_activation.objects.filter(User=self.request.user,product__id = 1, is_active=True)
		context['Products_legal'] = Product_activation.objects.filter(User=self.request.user,product__id = 10, is_active=True)
		return context


def search(request):
	template = 'aggrement/aggrement_list.html'

	query = request.GET.get('q')

	if query:
		result = Aggrement.objects.filter(Q(title__icontains=query) | Q(act__icontains=query) | Q(section__icontains=query))
	else:
		result = Aggrement.objects.all().order_by('id')

	aggrement_count = result.count()

	if not request.user.is_authenticated:
		Products_aggrement = Product_activation.objects.filter(product__id = 9, is_active=True)
		Products = Product_activation.objects.filter(product__id = 1, is_active=True)
		Role_products = Role_product_activation.objects.filter(product__id = 1, is_active=True)
		Todos = Todo.objects.filter(complete=False)
		Todos_total = Todo.objects.filter(complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		inbox = Message.objects.all()
		inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		send_count = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		Products_legal = Product_activation.objects.filter(product__id = 10, is_active=True)
		
	else:
		Products_aggrement = Product_activation.objects.filter(User=request.user,product__id = 9, is_active=True)
		Products = Product_activation.objects.filter(User=request.user,product__id = 1, is_active=True)
		Todos = Todo.objects.filter(User=request.user,complete=False)
		Role_products = Role_product_activation.objects.filter(User=request.user,product__id = 1, is_active=True)
		Todos_total = Todo.objects.filter(User=request.user,complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		inbox = Message.objects.filter(reciever=request.user)
		inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		Products_legal = Product_activation.objects.filter(User=request.user,product__id = 10, is_active=True)
	
	context = {
		'aggrement_list'	 : result,
		'aggrement_count' 	 : aggrement_count,
		'Products'			 : Products,
		'inbox'				 : inbox,
		'inbox_count'		 : inbox_count,
		'send_count'		 : send_count,
		'Todos'				 : Todos,
		'Todos_total' 		 : Todos_total,
		'Role_products' 	 : Role_products,
		'Products_aggrement' : Products_aggrement,

	}

	return render(request, template, context)


@login_required
def add_user_aggrement(request, pk):
	aggrement_details = Aggrement.objects.get(pk=pk) 

	new_user_aggrement = User_aggrement(User=request.user,aggrement=aggrement_details,textbody=aggrement_details.textbody)
	new_user_aggrement.save()

	return redirect(reverse('aggrement:saved_aggrement'))