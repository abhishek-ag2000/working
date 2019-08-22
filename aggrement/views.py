"""
Views
"""
import json
from datetime import datetime
from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models.functions import Coalesce
from django.db.models import Value, Q, Count
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from django.core import serializers
from django.http import HttpResponse
from user_profile.models import ProductActivated, RoleBasedProductActivated

from messaging.models import Message
from .models import Aggrement, UserAggrements
from .forms import AggrementForm, UserAggrementForm


class ProductExistsRequiredMixin:
    """
    Bracket Line Product Existence Check
    """

    def dispatch(self, request, *args, **kwargs):
        """
        Dispatch response
        """
        if ProductActivated.objects.filter(user=self.request.user, product__id=9, is_active=True):
            return super().dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied


@login_required
def get_aggrement_object(request):
    """
    Download object in json
    """
    all_objects = Aggrement.objects.all()
    data = serializers.serialize('json', all_objects)
    data = json.dumps(json.loads(data), indent=4)
    response = HttpResponse(data, content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename={}-{}.json'.format('Aggrement', datetime.now())
    return response


@login_required
def aggrement_upload(request):
    """
    Aggrement Upload View
    """
    if request.method == 'POST':
        new_aggreement = request.FILES['myfile']
        obj_generator = serializers.json.Deserializer(new_aggreement)

        for obj in obj_generator:
            obj.save()

    return render(request, 'aggrement/import_aggrement.html')


class AggrementListView(ProductExistsRequiredMixin, LoginRequiredMixin, ListView):
    """
    Aggrement List View
    """
    model = Aggrement
    paginate_by = 25
    template_name = 'aggrement/aggrement_list.html'

    def get_queryset(self):
        return self.model.objects.all().order_by('id')

    def get_context_data(self, **kwargs):
        context = super(AggrementListView, self).get_context_data(**kwargs)
        context['aggrement_list'] = Aggrement.objects.all().order_by('id')
        context['aggrement_count'] = Aggrement.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['active_product_1'] = ProductActivated.objects.filter(user=self.request.user, product__id=1, is_active=True)
        context['products_aggrement'] = ProductActivated.objects.filter(user=self.request.user, product__id=9, is_active=True)
        context['role_products'] = RoleBasedProductActivated.objects.filter(user=self.request.user, product__id=1, is_active=True)
        context['products_legal'] = ProductActivated.objects.filter(user=self.request.user, product__id=10, is_active=True)
        return context


class AggrementCreateView(LoginRequiredMixin, CreateView):
    """
    Aggrement Create View
    """
    form_class = AggrementForm
    template_name = 'aggrement/only_aggrement_form.html'

    def get_success_url(self, **kwargs):
        return reverse('aggrement:aggrementlist')


    def get_context_data(self, **kwargs):
        context = super(AggrementCreateView, self).get_context_data(**kwargs)
        context['products_aggrement'] = ProductActivated.objects.filter(user=self.request.user, product__id=9, is_active=True)
        context['active_product_1'] = ProductActivated.objects.filter(user=self.request.user, product__id=1, is_active=True)
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['products_legal'] = ProductActivated.objects.filter(user=self.request.user, product__id=10, is_active=True)
        return context


class SavedAggrementListView(ProductExistsRequiredMixin, LoginRequiredMixin, ListView):
    """
    Saved Aggrement List View
    """
    model = UserAggrements
    paginate_by = 25
    template_name = 'aggrement/saved_aggrement_saved_list.html'

    def get_queryset(self):
        return self.model.objects.all().order_by('id')

    def get_context_data(self, **kwargs):
        context = super(SavedAggrementListView, self).get_context_data(**kwargs)
        context['aggrement_list'] = UserAggrements.objects.all().order_by('id')
        context['aggrement_count'] = UserAggrements.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['active_product_1'] = ProductActivated.objects.filter(user=self.request.user, product__id=1, is_active=True)
        context['products_aggrement'] = ProductActivated.objects.filter(user=self.request.user, product__id=9, is_active=True)
        context['role_products'] = RoleBasedProductActivated.objects.filter(user=self.request.user, product__id=1, is_active=True)
        context['products_legal'] = ProductActivated.objects.filter(user=self.request.user, product__id=10, is_active=True)
        return context


class AggrementUpdateView(ProductExistsRequiredMixin, LoginRequiredMixin, UpdateView):
    """
    Aggrement Update View
    """
    model = UserAggrements
    form_class = UserAggrementForm
    template_name = "aggrement/aggrement_form.html"

    def get_success_url(self, **kwargs):
        return reverse('aggrement:saved_aggrement')

    def get_context_data(self, **kwargs):
        context = super(AggrementUpdateView, self).get_context_data(**kwargs)
        aggrement_details = get_object_or_404(Aggrement, pk=self.kwargs['company_pk'])
        context['aggrement_details'] = aggrement_details
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['active_product_1'] = ProductActivated.objects.filter(user=self.request.user, product__id=1, is_active=True)
        context['products_aggrement'] = ProductActivated.objects.filter(user=self.request.user, product__id=9, is_active=True)
        context['role_products'] = RoleBasedProductActivated.objects.filter(user=self.request.user, product__id=1, is_active=True)
        context['products_legal'] = ProductActivated.objects.filter(user=self.request.user, product__id=10, is_active=True)
        return context


def search(request):
    """
    Aggrement search view
    """
    template = 'aggrement/aggrement_list.html'

    query = request.GET.get('q')

    if query:
        result = Aggrement.objects.filter(Q(title__icontains=query) | Q(act__icontains=query) | Q(section__icontains=query))
    else:
        result = Aggrement.objects.all().order_by('id')

    aggrement_count = result.count()

    if not request.user.is_authenticated:
        products_aggrement = ProductActivated.objects.filter(product__id=9, is_active=True)
        products = ProductActivated.objects.filter(product__id=1, is_active=True)
        role_products = RoleBasedProductActivated.objects.filter(product__id=1, is_active=True)
        inbox = Message.objects.all()
        inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

    else:
        products_aggrement = ProductActivated.objects.filter(user=request.user, product__id=9, is_active=True)
        products = ProductActivated.objects.filter(user=request.user, product__id=1, is_active=True)
        role_products = RoleBasedProductActivated.objects.filter(user=request.user, product__id=1, is_active=True)
        inbox = Message.objects.filter(reciever=request.user)
        inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

    context = {
        'aggrement_list': result,
        'aggrement_count': aggrement_count,
        'products': products,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
        'role_products': role_products,
        'products_aggrement': products_aggrement,
    }

    return render(request, template, context)


@login_required
def add_user_aggrement(request, aggrement_pk):
    """
    Add user aggrement
    """
    aggrement_details = Aggrement.objects.get(pk=aggrement_pk)

    new_user_aggrement = UserAggrements(user=request.user, aggrement=aggrement_details, textbody=aggrement_details.textbody)
    new_user_aggrement.save()

    return redirect(reverse('aggrement:saved_aggrement'))
