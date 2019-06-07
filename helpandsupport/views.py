from django.shortcuts import render

from django.views.generic import (ListView,DetailView,
								  CreateView,UpdateView,DeleteView)
from helpandsupport.models import HelpCategories,Articles,Article_Answers,Article_Questions
from django.shortcuts import get_object_or_404
from ecommerce_integration.models import coupon, Product, Product_review, Services, API
from todogst.models import Todo
from userprofile.models import Profile, Product_activation, Role_product_activation
from messaging.models import Message
from django.db.models.functions import Coalesce
from django.db.models import Value, Sum, Count, F, ExpressionWrapper, Subquery, OuterRef, FloatField

# Create your views here.
class CategoriesListView(ListView):
	model = HelpCategories
	template_name = 'home.html' # <app>/<model>_<viewtype>.html
	context_object_name = 'HelpCategories'
	#ordering = ["-  "]

# Create your views here.
class CategoryDetailView(DetailView):
	model = HelpCategories
	template_name = 'catdetail.html'

	def get_context_data(self, **kwargs):
		context = super(CategoryDetailView, self).get_context_data(**kwargs) 
		#context['categories_list'] = categories.objects.all()
		if self.request.user.is_authenticated:
			context['Products'] = Product_activation.objects.filter(User=self.request.user,product__id = 1, is_active=True)
			context['Role_products'] = Role_product_activation.objects.filter(User=self.request.user,product__id = 1, is_active=True)
			context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
			context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
			context['inbox'] = Message.objects.filter(reciever=self.request.user)
			context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
			context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 

		else:
			context['Products'] = Product_activation.objects.filter(product__id = 1, is_active=True)
			context['Role_products'] = Role_product_activation.objects.filter(product__id = 1, is_active=True)
			context['Todos'] = Todo.objects.filter(complete=False)
			context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
			context['inbox'] = Message.objects.all()
			context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
			context['send_count'] = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']		

		return context


class ArticleDetailView(DetailView):
	model = Articles
	template_name = 'articledetail.html'

	def get_context_data(self, **kwargs):
		context = super(ArticleDetailView, self).get_context_data(**kwargs) 
		context['categories_slug'] = get_object_or_404(HelpCategories,slug=self.kwargs['slug1'])

		if self.request.user.is_authenticated:
			context['Products'] = Product_activation.objects.filter(User=self.request.user,product__id = 1, is_active=True)
			context['Role_products'] = Role_product_activation.objects.filter(User=self.request.user,product__id = 1, is_active=True)
			context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
			context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
			context['inbox'] = Message.objects.filter(reciever=self.request.user)
			context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
			context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 

		else:
			context['Products'] = Product_activation.objects.filter(product__id = 1, is_active=True)
			context['Role_products'] = Role_product_activation.objects.filter(product__id = 1, is_active=True)
			context['Todos'] = Todo.objects.filter(complete=False)
			context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
			context['inbox'] = Message.objects.all()
			context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
			context['send_count'] = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']		

		return context

