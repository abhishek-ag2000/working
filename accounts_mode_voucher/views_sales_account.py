"""
Views for Sale Voucher
"""
import calendar
import collections
import dateutil
from itertools import zip_longest
from num2words import num2words
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Value, Sum, Count, Case, When, F, Q
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
from stock_keeping.models_sale import SaleVoucher
from .models_sale_accounts import SaleVoucherAccounts, SaleTermAccounts, SaleTaxAccounts
from .forms_sale_accounts import SaleAccountsForm, SALE_TERM_FORM_SET, SALE_TAX_FORM_SET


class SalesListAccountsView(ProductExistsRequiredMixin, LoginRequiredMixin, ListView):
    """
    Sales List View
    """
    model = SaleVoucherAccounts
    template_name = 'sales/sales_list.html'
    paginate_by = 15

    def get_queryset(self):
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        return self.model.objects.filter(company=self.kwargs['company_pk'], voucher_date__gte=period_selected.start_date, voucher_date__lte=period_selected.end_date).order_by('-voucher_date')

    def get_context_data(self, **kwargs):
        context = super(SalesListAccountsView, self).get_context_data(**kwargs)
        company = get_object_or_404(
            Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected

        context['sales_accounts_list'] = SaleVoucherAccounts.objects.filter(company=self.kwargs['company_pk'], voucher_date__gte=period_selected.start_date, voucher_date__lte=period_selected.end_date).order_by('-voucher_date')
        context['sales_inventory_list'] = SaleVoucher.objects.filter(company=self.kwargs['company_pk'], voucher_date__gte=period_selected.start_date, voucher_date__lte=period_selected.end_date).order_by('-voucher_date')

        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        return context


class SalesDetailsView(ProductExistsRequiredMixin, UserPassesTestMixin, LoginRequiredMixin, DetailView):
    """
    Sales Details View
    """
    context_object_name = 'sale_voucher'
    model = SaleVoucherAccounts
    template_name = 'sales/sales_details.html'

    def get_object(self):
        company_pk = self.kwargs['company_pk']
        sales_pk = self.kwargs['sales_pk']
        period_selected_pk = self.kwargs['period_selected_pk']
        get_object_or_404(PeriodSelected, pk=period_selected_pk)
        get_object_or_404(Company, pk=company_pk)
        sale_voucher = get_object_or_404(SaleVoucherAccounts, pk=sales_pk)
        return sale_voucher

    def test_func(self):
        company = get_object_or_404(
            Company, pk=self.kwargs['company_pk'])
        sale_voucher = self.get_object()
        if self.request.user in company.auditor.all() or self.request.user in company.accountant.all() or self.request.user in company.sale_personel.all() or self.request.user == sale_voucher.user:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super(SalesDetailsView, self).get_context_data(**kwargs)
        company = get_object_or_404(
            Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        sale_voucher = get_object_or_404(SaleVoucherAccounts, pk=self.kwargs['sales_pk'])

        # saving the extra_charges
        extra_charge_sale = SaleTermAccounts.objects.filter(sale_voucher=sale_voucher.pk)
        for g in extra_charge_sale:
            if g.ledger != None:
                g.save()
                g.ledger.save()
                sale_voucher.save()

        context['extra_charge_sale_total'] = extra_charge_sale.aggregate(
            the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']

        context['extra_charge_sale_count'] = extra_charge_sale.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        extra_gst_sale = SaleTaxAccounts.objects.filter(sale_voucher=sale_voucher.pk)
        for g in extra_gst_sale:
            if g.ledger != None:
                g.save()
                g.ledger.save()
                
        # saving the party ledger
        sale_voucher.party_ac.save()
        # saving the party ledger group
        sale_voucher.party_ac.ledger_group.save()

        extra_gst_sales_central = SaleTaxAccounts.objects.filter(
            sale_voucher=sale_voucher.pk, ledger__tax_type='Central Tax').count()

        extra_gst_sales_state = SaleTaxAccounts.objects.filter(
            sale_voucher=sale_voucher.pk, ledger__tax_type='State Tax').count()

        extra_gst_sales_integrated = SaleTaxAccounts.objects.filter(
            sale_voucher=sale_voucher.pk, ledger__tax_type='Integrated Tax').count()

        tax_invoice_total = sale_voucher.sale_voucher_tax_accounts.aggregate(
            the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']
        extra_total = sale_voucher.sale_voucher_term_accounts.aggregate(
            the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']

        if tax_invoice_total or extra_total:
            total = tax_invoice_total + extra_total

        sale_voucher.total = total
        sale_voucher.save()

        context['extra_gst_sales_central'] = extra_gst_sales_central
        context['extra_gst_sales_state'] = extra_gst_sales_state
        context['extra_gst_sales_integrated'] = extra_gst_sales_integrated
        context['in_word'] = num2words(sale_voucher.total, lang='en_IN')
        context['total'] = total
        context['extra_charge_sales'] = extra_charge_sale
        context['extra_gst_sale'] = extra_gst_sale
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        return context


class SalesCreateView(ProductExistsRequiredMixin, LoginRequiredMixin, CreateView):
    """
    Sales Create View
    """
    form_class = SaleAccountsForm
    template_name = 'sales/sales_form.html'

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        sales_list = SaleVoucherAccounts.objects.filter(company=company.pk).order_by('-id')
        for sale_voucher in sales_list:
            if sale_voucher:
                return reverse('accounts_mode_voucher:salesdetail', kwargs={'company_pk': company.pk, 'sales_pk': sale_voucher.pk, 'period_selected_pk': period_selected.pk})

    def form_valid(self, form):
        form.instance.user = self.request.user
        company = Company.objects.get(pk=self.kwargs['company_pk'])
        form.instance.company = company
        counter = SaleVoucherAccounts.objects.filter(user=self.request.user, company=company).count() + 1
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

            if company.gst_enabled == 'Yes':
                extra_gst = context['extra_gst'] 
                self.object = form.save()
                if extra_gst.is_valid():
                    extra_gst.instance = self.object
                    extra_gst.save()

        return super(SalesCreateView, self).form_valid(form)

    def get_form_kwargs(self):
        data = super(SalesCreateView, self).get_form_kwargs()
        data.update(
            company=Company.objects.get(pk=self.kwargs['company_pk']),
        )
        return data

    def get_context_data(self, **kwargs):
        context = super(SalesCreateView, self).get_context_data(**kwargs)
        context['profile_details'] = Profile.objects.all()
        company = get_object_or_404(
            Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        if self.request.POST:
            context['extra_charges'] = SALE_TERM_FORM_SET(
                self.request.POST, form_kwargs={'company': company.pk})
            if company.gst_enabled == 'Yes':
                context['extra_gst'] = SALE_TAX_FORM_SET(
                    self.request.POST, form_kwargs={'company': company.pk})
        else:
            context['extra_charges'] = SALE_TERM_FORM_SET(
                form_kwargs={'company': company.pk})
            if company.gst_enabled == 'Yes':
                context['extra_gst'] = SALE_TAX_FORM_SET(
                    form_kwargs={'company': company.pk})
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        return context


class SalesUpdateView(ProductExistsRequiredMixin, UserPassesTestMixin, LoginRequiredMixin, UpdateView):
    """
    Sales Update View
    """
    model = SaleVoucherAccounts
    form_class = SaleAccountsForm
    template_name = 'sales/sales_form.html'

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        sale_voucher = get_object_or_404(SaleVoucherAccounts, pk=self.kwargs['sales_pk'])
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        return reverse('accounts_mode_voucher:salesdetail', kwargs={'company_pk': company.pk, 'sales_pk': sale_voucher.pk, 'period_selected_pk': period_selected.pk})

    def get_object(self):
        return get_object_or_404(SaleVoucherAccounts, pk=self.kwargs['sales_pk'])

    def test_func(self):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        sale_voucher = self.get_object()
        if self.request.user in company.accountant.all() or self.request.user in company.sale_personel.all() or self.request.user == sale_voucher.user:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super(SalesUpdateView, self).get_context_data(**kwargs)

        sale_voucher = get_object_or_404(SaleVoucherAccounts, pk=self.kwargs['sales_pk'])
        sales_particular = SaleVoucherAccounts.objects.get(pk=sale_voucher.pk)
        context['profile_details'] = Profile.objects.all()
        company = get_object_or_404(
            Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        if self.request.POST:
            #context['stocksales'] = SaleStockFormSet(self.request.POST, instance=sales_particular, form_kwargs={'company': company.pk})
            context['extra_charges'] = SALE_TERM_FORM_SET(
                self.request.POST, instance=sales_particular, form_kwargs={'company': company.pk})
            if company.gst_enabled == 'Yes':
                context['extra_gst'] = SALE_TAX_FORM_SET(
                    self.request.POST, instance=sales_particular, form_kwargs={'company': company.pk})
        else:
            #context['stocksales'] = SaleStockFormSet(instance=sales_particular, form_kwargs={'company': company.pk})
            context['extra_charges'] = SALE_TERM_FORM_SET(
                instance=sales_particular, form_kwargs={'company': company.pk})
            if company.gst_enabled == 'Yes':
                context['extra_gst'] = SALE_TAX_FORM_SET(
                    instance=sales_particular, form_kwargs={'company': company.pk})
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        company = Company.objects.get(pk=self.kwargs['company_pk'])
        form.instance.company = company

        context = self.get_context_data()
        extra_charges = context['extra_charges']

        if not extra_charges.is_valid():
            # formset for stock item is invalid; render the form with error
            return self.render_to_response(context)

        with transaction.atomic():
            extra_charges.save()

            if company.gst_enabled == 'Yes':
                extra_gst = context['extra_gst'] # TODO: this formset should be validated as stocksales formset
                if extra_gst.is_valid():
                    extra_gst.save()

        return super(SalesUpdateView, self).form_valid(form)

    def get_form_kwargs(self):
        data = super(SalesUpdateView, self).get_form_kwargs()
        data.update(
            company=Company.objects.get(pk=self.kwargs['company_pk'])
        )
        return data


class SalesDeleteView(ProductExistsRequiredMixin, UserPassesTestMixin, LoginRequiredMixin, DeleteView):
    """
    Sales Delete View
    """
    model = SaleVoucherAccounts
    template_name = "sales/sales_confirm_delete.html"

    def get_success_url(self, **kwargs):
        company = get_object_or_404(
            Company, pk=self.kwargs['company_pk'])
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        return reverse('accounts_mode_voucher:saleslist', kwargs={'company_pk': company.pk, 'period_selected_pk': period_selected.pk})

    def get_object(self):
        company_pk = self.kwargs['company_pk']
        sales_pk = self.kwargs['sales_pk']
        get_object_or_404(Company, pk=company_pk)
        sale_voucher = get_object_or_404(SaleVoucherAccounts, pk=sales_pk)
        return sale_voucher

    def test_func(self):
        company = get_object_or_404(
            Company, pk=self.kwargs['company_pk'])
        sale_voucher = self.get_object()
        if self.request.user in company.accountant.all() or self.request.user in company.sale_personel.all() or self.request.user == sale_voucher.user:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super(SalesDeleteView, self).get_context_data(**kwargs)
        company = get_object_or_404(
            Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        return context
