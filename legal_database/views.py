from django.shortcuts import render
from userprofile.models import Profile, Product_activation, Role_product_activation, Role_product_activation, Post, Post_comment, Pro_services, achivements, Organisation, Organisation_member
from django.core.exceptions import PermissionDenied
from django.views.generic import (ListView,DetailView,
								  CreateView,UpdateView,DeleteView)
from legal_database.models import Categories, Cases, Central_bare_act, State_bare_act, Chapter, Section, Sub_section
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from aggrement.models import Aggrement, User_aggrement
from todogst.models import Todo
from messaging.models import Message 
from userprofile.models import Profile, Product_activation, Role_product_activation, Role_product_activation, Post, Post_comment, Pro_services, achivements, Organisation, Organisation_member
from django.db.models.functions import Coalesce 
from django.db.models import Case, When, CharField, Value, Sum, F, Q, ExpressionWrapper, Subquery, OuterRef, Count
from django.shortcuts import get_object_or_404
# Create your views here.

class ProductExistsRequiredMixin:

    def dispatch(self, request, *args, **kwargs):
        if Product_activation.objects.filter(User=self.request.user,product__id = 10, is_active=True):
            return super().dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied


class Categories_List_View(ProductExistsRequiredMixin,LoginRequiredMixin,ListView):
	model = Categories
	template_name = 'legal_database/categories_list.html'

	def get_queryset(self):
		return self.model.objects.all().order_by('id')

	def get_context_data(self, **kwargs):
		context = super(Categories_List_View, self).get_context_data(**kwargs) 
		context['categories_list'] = Categories.objects.all().order_by('id')
		context['categories_count'] = context['categories_list'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		context['categories_sact'] = context['categories_list'].aggregate(the_sum=Coalesce(Count('sb_acts'), Value(0)))['the_sum'] 
		context['categories_cbct'] = context['categories_list'].aggregate(the_sum=Coalesce(Count('cb_acts'), Value(0)))['the_sum'] 
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


def Central_bare_act_detail(request, pk):
	Central_bare_act_details = get_object_or_404(Central_bare_act, pk=pk)


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
		'Central_bare_act_details'	: Central_bare_act_details,
		'Products'					: Products,
		'Products_legal'			: Products_legal,
		'inbox'						: inbox,
		'inbox_count'				: inbox_count,
		'send_count'				: send_count,
		'Todos'		 				: Todos,
		'Todos_total' 				: Todos_total,
		'Role_products' 			: Role_products  	
		
	}
	return render(request, 'legal_database/central_act_details.html', context)

def State_bare_act_detail(request, pk):
	State_bare_act_details = get_object_or_404(State_bare_act, pk=pk)


	if not request.user.is_authenticated:
		Products = Product_activation.objects.filter(product__id = 1, is_active=True)
		Role_products = Role_product_activation.objects.filter(product__id = 1, is_active=True)
		Todos = Todo.objects.filter(complete=False)
		Todos_total = Todo.objects.filter(complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		inbox = Message.objects.all()
		inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		send_count = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		Products_legal = Product_activation.objects.filter(product__id = 10, is_active=True)	
	else:
		Products = Product_activation.objects.filter(User=request.user,product__id = 1, is_active=True)
		Todos = Todo.objects.filter(User=request.user,complete=False)
		Role_products = Role_product_activation.objects.filter(User=request.user,product__id = 1, is_active=True)
		Todos_total = Todo.objects.filter(User=request.user,complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		inbox = Message.objects.filter(reciever=request.user)
		inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		Products_legal = Product_activation.objects.filter(User=request.user,product__id = 10, is_active=True)



	context = {
		'State_bare_act_details'	: State_bare_act_details,
		'Products'					: Products,
		'Products_legal'			: Products_legal,
		'inbox'						: inbox,
		'inbox_count'				: inbox_count,
		'send_count'				: send_count,
		'Todos'		 				: Todos,
		'Todos_total' 				: Todos_total,
		'Role_products' 			: Role_products  	
		
	}
	return render(request, 'legal_database/state_act_details.html', context)



def Section_detail(request, pk):
	section_details = get_object_or_404(Section, pk=pk)


	if not request.user.is_authenticated:
		Products = Product_activation.objects.filter(product__id = 1, is_active=True)
		Role_products = Role_product_activation.objects.filter(product__id = 1, is_active=True)
		Todos = Todo.objects.filter(complete=False)
		Todos_total = Todo.objects.filter(complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		inbox = Message.objects.all()
		inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		send_count = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		Products_legal = Product_activation.objects.filter(product__id = 10, is_active=True)	
	else:
		Products = Product_activation.objects.filter(User=request.user,product__id = 1, is_active=True)
		Todos = Todo.objects.filter(User=request.user,complete=False)
		Role_products = Role_product_activation.objects.filter(User=request.user,product__id = 1, is_active=True)
		Todos_total = Todo.objects.filter(User=request.user,complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
		inbox = Message.objects.filter(reciever=request.user)
		inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
		Products_legal = Product_activation.objects.filter(User=request.user,product__id = 10, is_active=True)



	context = {
		'section_details'	: section_details,
		'Products'			: Products,
		'Products_legal'	: Products_legal,
		'inbox'				: inbox,
		'inbox_count'		: inbox_count,
		'send_count'		: send_count,
		'Todos'		 		: Todos,
		'Todos_total' 		: Todos_total,
		'Role_products' 	: Role_products  	
		
	}
	return render(request, 'legal_database/section_details.html', context)