"""
Views for Purchase Voucher
"""
import calendar
import collections
import dateutil
from num2words import num2words
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Value, Sum, Count, Case, When, F
from django.db.models.functions import Coalesce
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse
from company.models import Company
from user_profile.models import Profile
from messaging.models import Message

from ecommerce_integration.decorators import product_1_activation
from accounting_entry.models import PeriodSelected
from accounting_entry.mixins import ProductExistsRequiredMixin
from .model_purchase_accounts import PurchaseVoucherAccounts, PurchaseTermAccounts, PurchaseTaxAccounts
from .form_purchase_accounts import PurchaseAccountsForm, PURCHASE_TERM_FORM_SET, PURCHASE_TAX_FORM_SET




class PurchaseDetailsView(LoginRequiredMixin,  UserPassesTestMixin, DetailView):
    """
    Purchase Details View
    """
    context_object_name = 'purchase_details'
    model = PurchaseVoucherAccounts
    template_name = 'purchase/purchase_details.html'

    def get_object(self):
        return get_object_or_404(PurchaseVoucherAccounts, pk=self.kwargs['purchase_pk'])

    def test_func(self):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        purchase_voucher = self.get_object()
        if self.request.user in company.auditor.all() or self.request.user in company.accountant.all() or self.request.user in company.purchase_personel.all() or self.request.user == purchase_voucher.user:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super(PurchaseDetailsView, self).get_context_data(**kwargs)
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        purchase_details = get_object_or_404(PurchaseVoucherAccounts, pk=self.kwargs['purchase_pk'])


        extra_charge_purchases = PurchaseTermAccounts.objects.filter(purchase_voucher=purchase_details.pk)
        for g in extra_charge_purchases:
            g.save()
            purchase_details.save()

        context['extra_charge_purchases_sum'] = extra_charge_purchases.aggregate(the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']

        # saving the gst ledger

        extra_gst_purchase = PurchaseTaxAccounts.objects.filter(purchase_voucher=purchase_details.pk)
        for g in extra_gst_purchase:
            if g.ledger != None:
                g.save()

        tax_total = purchase_details.purchase_voucher_tax_accounts.aggregate(
            the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']
        extra_total = purchase_details.purchase_voucher_term_accounts.aggregate(
            the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']
        if tax_total or extra_total:
            total = tax_total + extra_total

        purchase_details.total = total
        purchase_details.save()


        extra_gst_purchase_central = PurchaseTaxAccounts.objects.filter(purchase_voucher=purchase_details.pk, ledger__tax_type='Central Tax').count()

        extra_gst_purchase_state = PurchaseTaxAccounts.objects.filter(purchase_voucher=purchase_details.pk, ledger__tax_type='State Tax').count()

        extra_gst_purchase_integrated = PurchaseTaxAccounts.objects.filter(purchase_voucher=purchase_details.pk, ledger__tax_type='Integrated Tax').count()

        context['extra_gst_purchase_central'] = extra_gst_purchase_central
        context['extra_gst_purchase_state'] = extra_gst_purchase_state
        context['extra_gst_purchase_integrated'] = extra_gst_purchase_integrated
        context['in_word'] = num2words(purchase_details.total, lang='en_IN')
        context['total'] = total
        context['extra_charge_purchases'] = extra_charge_purchases
        context['extra_gst_purchase'] = extra_gst_purchase
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        return context


class PurchaseCreateView(ProductExistsRequiredMixin,  LoginRequiredMixin, CreateView):
    """
    Purchase Create View
    """
    form_class = PurchaseAccountsForm
    template_name = 'purchase/purchase_form.html'

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        purchase_voucher = PurchaseVoucherAccounts.objects.filter(company=company.pk, voucher_date__gte=period_selected.start_date, voucher_date__lte=period_selected.end_date).order_by('-id')
        for p in purchase_voucher:
            if p:
                return reverse('accounts_mode_voucher:purchasedetail', kwargs={'company_pk': company.pk, 'purchase_pk': p.pk, 'period_selected_pk': period_selected.pk})
            else:
                return reverse('accounts_mode_voucher:purchaselist', kwargs={'company_pk': company.pk, 'period_selected_pk': period_selected.pk})

    def form_valid(self, form):
        form.instance.user = self.request.user
        c = Company.objects.get(pk=self.kwargs['company_pk'])
        form.instance.company = c
        counter = PurchaseVoucherAccounts.objects.filter(user=self.request.user, company=c).count() + 1
        form.instance.counter = counter
        context = self.get_context_data()

        extra_charges = context['extra_charges']

        if not extra_charges.is_valid():
            # formset for stock item is invalid; render the form with error
            return self.render_to_response(context)

        with transaction.atomic():
            self.object = form.save()
            extra_charges.instance = self.object
            extra_charges.save()

            if c.gst_enabled == 'Yes':
                extra_gst = context['extra_gst']
                self.object = form.save()
                if extra_gst.is_valid():
                    extra_gst.instance = self.object
                    extra_gst.save()
        return super(PurchaseCreateView, self).form_valid(form)


    def get_context_data(self, **kwargs):
        context = super(PurchaseCreateView, self).get_context_data(**kwargs)
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        if self.request.POST:
            context['extra_charges'] = PURCHASE_TERM_FORM_SET(self.request.POST, form_kwargs={'company': company.pk})
            if company.gst_enabled == 'Yes':
                context['extra_gst'] = PURCHASE_TAX_FORM_SET(self.request.POST, form_kwargs={'company': company.pk})
        else:
            context['extra_charges'] = PURCHASE_TERM_FORM_SET(form_kwargs={'company': company.pk})
            if company.gst_enabled == 'Yes':
                context['extra_gst'] = PURCHASE_TAX_FORM_SET(form_kwargs={'company': company.pk})
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        return context

    def get_form_kwargs(self):
        data = super(PurchaseCreateView, self).get_form_kwargs()
        data.update(
            Company=Company.objects.get(pk=self.kwargs['company_pk'])
        )
        return data


class PurchaseUpdateView(ProductExistsRequiredMixin,  UserPassesTestMixin, LoginRequiredMixin, UpdateView):
    """
    Purchase Update View
    """
    model = PurchaseVoucherAccounts
    form_class = PurchaseAccountsForm
    template_name = 'purchase/purchase_form.html'

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        purchase_details = get_object_or_404(PurchaseVoucherAccounts, pk=self.kwargs['purchase_pk'])
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        return reverse('accounts_mode_voucher:purchasedetail', kwargs={'company_pk': company.pk, 'purchase_pk': purchase_details.pk, 'period_selected_pk': period_selected.pk})

    def get_object(self):
        company_pk = self.kwargs['company_pk']
        purchase_pk = self.kwargs['purchase_pk']
        get_object_or_404(Company, pk=company_pk)
        purchase = get_object_or_404(PurchaseVoucherAccounts, pk=purchase_pk)
        return purchase

    def test_func(self):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        purchase_voucher = self.get_object()
        if self.request.user in company.accountant.all() or self.request.user in company.purchase_personel.all() or self.request.user == purchase_voucher.user:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super(PurchaseUpdateView, self).get_context_data(**kwargs)
        purchase_details = get_object_or_404(PurchaseVoucherAccounts, pk=self.kwargs['purchase_pk'])
        purchase_voucher = PurchaseVoucherAccounts.objects.get(pk=purchase_details.pk)
        context['profile_details'] = Profile.objects.all()
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        if self.request.POST:
            context['extra_charges'] = PURCHASE_TERM_FORM_SET(self.request.POST, instance=purchase_voucher, form_kwargs={'company': company.pk})
            if company.gst_enabled == 'Yes':
                context['extra_gst'] = PURCHASE_TAX_FORM_SET(self.request.POST, instance=purchase_voucher, form_kwargs={'company': company.pk})
        else:
            context['extra_charges'] = PURCHASE_TERM_FORM_SET(instance=purchase_voucher, form_kwargs={'company': company.pk})
            if company.gst_enabled == 'Yes':
                context['extra_gst'] = PURCHASE_TAX_FORM_SET(instance=purchase_voucher, form_kwargs={'company': company.pk})
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        c = Company.objects.get(pk=self.kwargs['company_pk'])
        form.instance.company = c
        context = self.get_context_data()
        extra_charges = context['extra_charges']

        if not extra_charges.is_valid():
            # formset for stock item is invalid; render the form with error
            return self.render_to_response(context)

        with transaction.atomic():
            extra_charges.save()
            if c.gst_enabled == 'Yes':
                extra_gst = context['extra_gst']
                if extra_gst.is_valid():
                    extra_gst.save()
        return super(PurchaseUpdateView, self).form_valid(form)

    def get_form_kwargs(self):
        data = super(PurchaseUpdateView, self).get_form_kwargs()
        data.update(
            Company=Company.objects.get(pk=self.kwargs['company_pk'])
        )
        return data


class PurchaseDeleteView(ProductExistsRequiredMixin,  UserPassesTestMixin, LoginRequiredMixin, DeleteView):
    """
    Purchase Delete View
    """
    model = PurchaseVoucherAccounts
    template_name = "purchase/purchase_confirm_delete.html"

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        return reverse('stock_keeping:purchaselist', kwargs={'company_pk': company.pk, 'period_selected_pk': period_selected.pk})

    def get_object(self):
        company_pk = self.kwargs['company_pk']
        purchase_pk = self.kwargs['purchase_pk']
        get_object_or_404(Company, pk=company_pk)
        purchase = get_object_or_404(PurchaseVoucherAccounts, pk=purchase_pk)
        return purchase

    def test_func(self):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        purchase_voucher = self.get_object()
        if self.request.user in company.accountant.all() or self.request.user in company.purchase_personel.all() or self.request.user == purchase_voucher.user:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super(PurchaseDeleteView, self).get_context_data(**kwargs)
        context['profile_details'] = Profile.objects.all()
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        return context
