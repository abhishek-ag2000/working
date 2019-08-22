"""
Views
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models.functions import Coalesce
from django.db.models import Value, Count
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import ListView, CreateView

from user_profile.models import ProductActivated, RoleBasedProductActivated
from .models import Message
from .forms import MessageForm


class MessageInbox(LoginRequiredMixin, ListView):
    """
    Message Inbox View
    """
    model = Message
    template_name = "message/message_inbox.html"
    paginate_by = 10

    def get_queryset(self):
        return Message.objects.filter(reciever=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(MessageInbox, self).get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            context['active_product_1'] = ProductActivated.objects.filter(
                user=self.request.user, product__id=1, is_active=True)
            context['role_product_1'] = RoleBasedProductActivated.objects.filter(
                user=self.request.user, product__id=1, is_active=True)

            context['inbox'] = Message.objects.filter(
                reciever=self.request.user)
            context['inbox_count'] = context['inbox'].aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['product_legal'] = ProductActivated.objects.filter(
                user=self.request.user, product__id=10, is_active=True)
        else:
            context['active_product_1'] = ProductActivated.objects.filter(
                product__id=1, is_active=True)
            context['role_product_1'] = RoleBasedProductActivated.objects.filter(
                product__id=1, is_active=True)

            context['inbox'] = Message.objects.all()
            context['inbox_count'] = context['inbox'].aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.all().aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['product_legal'] = ProductActivated.objects.filter(
                product__id=10, is_active=True)
        return context


class MessageSend(LoginRequiredMixin, ListView):
    """
    Message Send Items View
    """
    model = Message
    template_name = "message/message_send.html"
    paginate_by = 10

    def get_queryset(self):
        return Message.objects.filter(sender=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(MessageSend, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['active_product_1'] = ProductActivated.objects.filter(
                user=self.request.user, product__id=1, is_active=True)
            context['role_product_1'] = RoleBasedProductActivated.objects.filter(
                user=self.request.user, product__id=1, is_active=True)

            context['inbox'] = Message.objects.filter(
                reciever=self.request.user)
            context['inbox_count'] = context['inbox'].aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['product_legal'] = ProductActivated.objects.filter(
                user=self.request.user, product__id=10, is_active=True)
        else:
            context['active_product_1'] = ProductActivated.objects.filter(
                product__id=1, is_active=True)
            context['role_product_1'] = RoleBasedProductActivated.objects.filter(
                product__id=1, is_active=True)

            context['inbox'] = Message.objects.all()
            context['inbox_count'] = context['inbox'].aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.all().aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['product_legal'] = ProductActivated.objects.filter(
                product__id=10, is_active=True)
        return context


class MessageCreate(LoginRequiredMixin, CreateView):
    """
    Compose Message View
    """
    form_class = MessageForm
    template_name = "message/message_form.html"

    def get_success_url(self, **kwargs):
        return reverse('messaging:messagesend')

    def form_valid(self, form):
        form.instance.sender = self.request.user
        obj = form.save(commit=False)
        if self.request.FILES:
            for f in self.request.FILES.getlist('attchment'):
                obj = self.model.objects.create(file=f)
        return super(MessageCreate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(MessageCreate, self).get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            context['active_product_1'] = ProductActivated.objects.filter(
                user=self.request.user, product__id=1, is_active=True)
            context['role_product_1'] = RoleBasedProductActivated.objects.filter(
                user=self.request.user, product__id=1, is_active=True)

            context['inbox'] = Message.objects.filter(
                reciever=self.request.user)
            context['inbox_count'] = context['inbox'].aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['product_legal'] = ProductActivated.objects.filter(
                user=self.request.user, product__id=10, is_active=True)
        else:
            context['active_product_1'] = ProductActivated.objects.filter(
                product__id=1, is_active=True)
            context['role_product_1'] = RoleBasedProductActivated.objects.filter(
                product__id=1, is_active=True)

            context['inbox'] = Message.objects.all()
            context['inbox_count'] = context['inbox'].aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.all().aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['product_legal'] = ProductActivated.objects.filter(
                product__id=10, is_active=True)
        return context


@login_required
def message_details(request, message_pk):
    """
    Function Based Message Details View
    """
    message = get_object_or_404(Message, pk=message_pk)

    context = {
        'product_aggrement': ProductActivated.objects.filter(user=request.user, product__id=9, is_active=True),
        'inbox': Message.objects.filter(reciever=request.user),
        'message_details': message,
        'send_count': Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'],
        'inbox_count': Message.objects.filter(reciever=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'],
        'Products': ProductActivated.objects.filter(user=request.user, product__id=1, is_active=True),
        'role_product': RoleBasedProductActivated.objects.filter(user=request.user, product__id=1, is_active=True),
        'product_legal': ProductActivated.objects.filter(user=request.user, product__id=10, is_active=True)
    }

    return render(request, 'message/message_details.html', context)
