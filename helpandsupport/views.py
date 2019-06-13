from django.shortcuts import render

from django.views.generic import (ListView,DetailView,
								  CreateView,UpdateView,DeleteView)
from helpandsupport.models import HelpCategories,Articles,Article_Answers,Article_Questions
from helpandsupport.forms import Questionform
from django.shortcuts import get_object_or_404
from ecommerce_integration.models import coupon, Product, Product_review, Services, API
from todogst.models import Todo
from userprofile.models import Profile, Product_activation, Role_product_activation
from messaging.models import Message
from django.db.models.functions import Coalesce
from django.db.models import Value, Sum, Count, F, ExpressionWrapper, Subquery, OuterRef, FloatField
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect, JsonResponse
# Create your views here.


class CategoriesListView(ListView):
	model = HelpCategories
	template_name = 'home.html'

	def get_queryset(self):
		return HelpCategories.objects.all().order_by('-id')

	def get_context_data(self, **kwargs):
		context = super(CategoriesListView, self).get_context_data(**kwargs)
		context['categoriest'] = HelpCategories.objects.all().order_by('-id')
		if self.request.user.is_authenticated:
			context['Products'] = Product_activation.objects.filter(User=self.request.user,product__id = 1, is_active=True)
			context['Role_products'] = Role_product_activation.objects.filter(User=self.request.user,product__id = 1, is_active=True)
			context['Todos'] = Todo.objects.filter(User=self.request.user, complete=False)
			context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
			context['inbox'] = Message.objects.filter(reciever=self.request.user)
			context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
			context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
			context['Products_legal'] = Product_activation.objects.filter(User=self.request.user,product__id = 10, is_active=True)
		else:
			context['Products'] = Product_activation.objects.filter(product__id = 1, is_active=True)
			context['Role_products'] = Role_product_activation.objects.filter(product__id = 1, is_active=True)
			context['Todos'] = Todo.objects.filter(complete=False)
			context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
			context['inbox'] = Message.objects.all()
			context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
			context['send_count'] = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']		
			context['Products_legal'] = Product_activation.objects.filter(product__id = 10, is_active=True)	
		return context


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
			context['Products_legal'] = Product_activation.objects.filter(User=self.request.user,product__id = 10, is_active=True)
		else:
			context['Products'] = Product_activation.objects.filter(product__id = 1, is_active=True)
			context['Role_products'] = Role_product_activation.objects.filter(product__id = 1, is_active=True)
			context['Todos'] = Todo.objects.filter(complete=False)
			context['Todos_total'] = context['Todos'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
			context['inbox'] = Message.objects.all()
			context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
			context['send_count'] = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']		
			context['Products_legal'] = Product_activation.objects.filter(product__id = 10, is_active=True)	

		return context


def ArticleDetailView(request, slug1,slug):
	categories_slug = get_object_or_404(HelpCategories, slug=slug1)
	article_details = get_object_or_404(Articles,slug=slug)
	questions = Article_Questions.objects.filter(Article=article_details).order_by('-id')

	if request.method == "POST":
		question_form = Questionform(request.POST or None)
		if question_form.is_valid():
			text = request.POST.get('text')
			question = Article_Questions.objects.create(Article=article_details, User=request.user, text=text)
			question.save()
			return HttpResponseRedirect(article_details.get_absolute_url())
	else:
		question_form = Questionform()

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

		'questions'				: questions,
		'question_form'			: question_form,
		'article_details' 		: article_details,
		'categories_slug' 		: categories_slug,
		'Products'				: Products,
		'inbox'					: inbox,
		'inbox_count'			: inbox_count,
		'send_count'			: send_count,
		'Todos'		 			: Todos,
		'Todos_total' 			: Todos_total,
		'Role_products' 		: Role_products,  
		'Products_legal'		: Products_legal,
		'Products_aggrement' 	: Products_aggrement
		
	}

	if request.is_ajax():
		html = render_to_string('questions.html',context, request=request)
		return JsonResponse({'form' : html})

	return render(request, 'articledetail.html', context)



# def save_all(request,form,template_name):
# 	data = dict()
# 	if request.method == 'POST':
# 		if form.is_valid():
# 			form.save()
# 			data['form_is_valid'] = True
# 			questions_list = Article_Questions.objects.all().order_by('-id')
# 			data['questions_list'] = render_to_string('questions.html',{'questions_list':questions_list})
# 		else:
# 			data['form_is_valid'] = False
# 	context = {

# 		'form':form,
# 	}
# 	data['html_form'] = render_to_string(template_name,context,request=request)

# 	return JsonResponse(data)

# def question_create(request):
# 	if request.method == 'POST':
# 		form = Questionform(request.POST or None)
# 	else:
# 		form = Questionform()

# 	context = {
# 		'form' : form,
# 	}

# 	return save_all(request,context,'question_create.html')