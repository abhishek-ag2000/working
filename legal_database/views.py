"""
Views
"""
from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.functions import Coalesce
from django.db.models import Value, Count
from django.shortcuts import get_object_or_404
from user_profile.models import ProductActivated, RoleBasedProductActivated
from legal_database.models import Categories, CentralBareAct, StateBareAct, Section

from messaging.models import Message


class ProductExistsRequiredMixin:
    """
    Legal Database Product Activate Check
    """

    def dispatch(self, request, *args, **kwargs):
        """
        Returns response after validation
        """
        if ProductActivated.objects.filter(user=self.request.user, product__id=10, is_active=True):
            return super().dispatch(request, *args, **kwargs)

        raise PermissionDenied


class HelpCategoryListView(ProductExistsRequiredMixin, LoginRequiredMixin, ListView):
    """
    Categories List View
    """
    model = Categories
    template_name = 'legal_database/categories_list.html'

    def get_queryset(self):
        return self.model.objects.all().order_by('id')

    def get_context_data(self, **kwargs):
        context = super(HelpCategoryListView, self).get_context_data(**kwargs)
        context['categories_list'] = Categories.objects.all().order_by('id')
        context['categories_count'] = context['categories_list'].aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['categories_sact'] = context['categories_list'].aggregate(
            the_sum=Coalesce(Count('sb_acts'), Value(0)))['the_sum']
        context['categories_cbct'] = context['categories_list'].aggregate(
            the_sum=Coalesce(Count('cb_acts'), Value(0)))['the_sum']

        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['our_product'] = ProductActivated.objects.filter(
            user=self.request.user, product__id=1, is_active=True)
        context['product_aggrement'] = ProductActivated.objects.filter(
            user=self.request.user, product__id=9, is_active=True)
        context['role_product_1'] = RoleBasedProductActivated.objects.filter(
            user=self.request.user, product__id=1, is_active=True)
        context['product_legal'] = ProductActivated.objects.filter(
            user=self.request.user, product__id=10, is_active=True)
        return context


def central_bare_act_detail(request, central_bare_act_pk):
    """
    Function Based CentralBareAct Detail View
    """
    Central_bare_act_details = get_object_or_404(CentralBareAct, pk=central_bare_act_pk)

    if not request.user.is_authenticated:
        product_aggrement = ProductActivated.objects.filter(
            user=request.user, product__id=9, is_active=True)
        our_product = ProductActivated.objects.filter(
            product__id=1, is_active=True)
        role_product = RoleBasedProductActivated.objects.filter(
            product__id=1, is_active=True)
        inbox = Message.objects.all()
        inbox_count = inbox.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.all().aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        product_legal = ProductActivated.objects.filter(
            product__id=10, is_active=True)
    else:
        product_aggrement = ProductActivated.objects.filter(
            product__id=9, is_active=True)
        our_product = ProductActivated.objects.filter(
            user=request.user, product__id=1, is_active=True)
        role_product = RoleBasedProductActivated.objects.filter(
            user=request.user, product__id=1, is_active=True)
        inbox = Message.objects.filter(reciever=request.user)
        inbox_count = inbox.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.filter(sender=request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        product_legal = ProductActivated.objects.filter(
            user=request.user, product__id=10, is_active=True)

    context = {
        'Central_bare_act_details': Central_bare_act_details,
        'our_product': our_product,
        'product_legal': product_legal,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
        'role_product': role_product
    }

    return render(request, 'legal_database/central_act_details.html', context)


def state_bare_act_detail(request, state_bare_act_pk):
    """
    Function Based StateBareAct Detail View
    """
    State_bare_act_details = get_object_or_404(StateBareAct, pk=state_bare_act_pk)

    if not request.user.is_authenticated:
        our_product = ProductActivated.objects.filter(
            product__id=1, is_active=True)
        role_product = RoleBasedProductActivated.objects.filter(
            product__id=1, is_active=True)
        inbox = Message.objects.all()
        inbox_count = inbox.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.all().aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        product_legal = ProductActivated.objects.filter(
            product__id=10, is_active=True)
    else:
        our_product = ProductActivated.objects.filter(
            user=request.user, product__id=1, is_active=True)
        role_product = RoleBasedProductActivated.objects.filter(
            user=request.user, product__id=1, is_active=True)
        inbox = Message.objects.filter(reciever=request.user)
        inbox_count = inbox.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.filter(sender=request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        product_legal = ProductActivated.objects.filter(
            user=request.user, product__id=10, is_active=True)

    context = {
        'State_bare_act_details': State_bare_act_details,
        'our_product': our_product,
        'product_legal': product_legal,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
        'role_product': role_product

    }
    return render(request, 'legal_database/state_act_details.html', context)


def section_detail(request, section_pk):
    """
    Function Based Section Detail View
    """
    section_details = get_object_or_404(Section, pk=section_pk)

    if not request.user.is_authenticated:
        our_product = ProductActivated.objects.filter(
            product__id=1, is_active=True)
        role_product = RoleBasedProductActivated.objects.filter(
            product__id=1, is_active=True)
        inbox = Message.objects.all()
        inbox_count = inbox.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.all().aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        product_legal = ProductActivated.objects.filter(
            product__id=10, is_active=True)
    else:
        our_product = ProductActivated.objects.filter(
            user=request.user, product__id=1, is_active=True)
        role_product = RoleBasedProductActivated.objects.filter(
            user=request.user, product__id=1, is_active=True)
        inbox = Message.objects.filter(reciever=request.user)
        inbox_count = inbox.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.filter(sender=request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        product_legal = ProductActivated.objects.filter(
            user=request.user, product__id=10, is_active=True)

    context = {
        'section_details': section_details,
        'our_product': our_product,
        'product_legal': product_legal,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
        'role_product': role_product
    }
    return render(request, 'legal_database/section_details.html', context)
