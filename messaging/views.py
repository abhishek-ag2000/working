from django.shortcuts import render
from django.urls import reverse
from .forms import messageform
from django.views.generic import (ListView,DetailView,
								  CreateView,UpdateView,DeleteView)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from todogst.models import Todo
from userprofile.models import Profile, Product_activation, Role_product_activation
from .models import Message
from django.db.models.functions import Coalesce 
from django.db.models import Case, When, CharField, Value, Sum, F, Q, ExpressionWrapper, Subquery, OuterRef, Count
# Create your views here.


class messageinbox(LoginRequiredMixin,ListView):
	model = Message
	template_name = "message/message_inbox.html"
	paginate_by = 10

	def get_queryset(self):
		return Message.objects.filter(reciever=self.request.user)

	def get_context_data(self, **kwargs):
		context = super(messageinbox, self).get_context_data(**kwargs)
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

class messagesend(LoginRequiredMixin,ListView):
	model = Message
	template_name = "message/message_send.html"
	paginate_by = 10

	def get_queryset(self):
		return Message.objects.filter(sender=self.request.user)

	def get_context_data(self, **kwargs):
		context = super(messagesend, self).get_context_data(**kwargs)
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

class messagecreate(LoginRequiredMixin,CreateView):
	form_class = messageform
	template_name = "message/message_form.html"

	def get_success_url(self,**kwargs):
		return reverse('messaging:messagesend')


	def form_valid(self, form):
		form.instance.sender = self.request.user
		obj = form.save(commit=False)
		if self.request.FILES:
			for f in self.request.FILES.getlist('attchment'):
				obj = self.model.objects.create(file=f)
		return super(messagecreate, self).form_valid(form)

	def get_context_data(self, **kwargs):
		context = super(messagecreate, self).get_context_data(**kwargs)
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

@login_required
def message_details(request, pk):
	message_details = get_object_or_404(Message, pk=pk)


	context = {
        'Products_aggrement': Product_activation.objects.filter(User=request.user,product__id = 9, is_active=True),
		'inbox'				: Message.objects.filter(reciever=request.user),
		'message_details' 	: message_details,
		'send_count'		: Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'],
		'inbox_count'		: Message.objects.filter(reciever=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'],
		'Products'			: Product_activation.objects.filter(User=request.user,product__id = 1, is_active=True),
		'Todos'				: Todo.objects.filter(User=request.user, complete=False),
		'Todos_total' 		: Todo.objects.filter(User=request.user, complete=False).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'], 
		'Role_products' 	: Role_product_activation.objects.filter(User=request.user,product__id = 1, is_active=True),
        'Products_legal'    : Product_activation.objects.filter(User=request.user,product__id = 10, is_active=True)
	}

	return render(request, 'message/message_details.html', context)