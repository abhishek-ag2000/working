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
from accounts_mode_voucher.model_purchase_accounts import PurchaseVoucherAccounts
from .mixins import CompanyAccountsWithInventoryMixin
from .decorators import company_account_with_invenroty_decorator
from accounts_mode_voucher.model_purchase_accounts import PurchaseVoucherAccounts, PurchaseTermAccounts, PurchaseTaxAccounts
from .models_purchase import PurchaseVoucher, PurchaseStock, PurchaseTerm, PurchaseTax
from .forms_purchase import PurchaseForm, PURCHASE_STOCK_FORM_SET, PURCHASE_TERM_FORM_SET, PURCHASE_TAX_FORM_SET


class PurchaseListView(ProductExistsRequiredMixin,  LoginRequiredMixin, ListView):
    """
    Purchase List View
    """
    context_object_name = 'purchase_list'
    model = PurchaseVoucher
    template_name = 'stock_keeping/purchase/purchase_list.html'
    paginate_by = 15

    def get_queryset(self):
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        return self.model.objects.filter(company=self.kwargs['company_pk'], voucher_date__gte=period_selected.start_date, voucher_date__lte=period_selected.end_date).order_by('-voucher_date')

    def get_context_data(self, **kwargs):
        context = super(PurchaseListView, self).get_context_data(**kwargs)
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected

        context['purchase_accounts_list'] = PurchaseVoucherAccounts.objects.filter(company=self.kwargs['company_pk'], voucher_date__gte=period_selected.start_date, voucher_date__lte=period_selected.end_date).order_by('-voucher_date')
        context['purchase_inventory_list'] = PurchaseVoucher.objects.filter(company=self.kwargs['company_pk'], voucher_date__gte=period_selected.start_date, voucher_date__lte=period_selected.end_date).order_by('-voucher_date')

        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        return context

class PurchaseDetailsView(LoginRequiredMixin,  UserPassesTestMixin, DetailView):
    """
    Purchase Details View
    """
    context_object_name = 'purchase_details'
    model = PurchaseVoucher
    template_name = 'stock_keeping/purchase/purchase_details.html'

    def get_object(self):
        return get_object_or_404(PurchaseVoucher, pk=self.kwargs['purchase_pk'])

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
        purchase_details = get_object_or_404(PurchaseVoucher, pk=self.kwargs['purchase_pk'])
        qsob = PurchaseStock.objects.filter(purchase_voucher=purchase_details.pk)

        # saving the stock and  closing stock of particular puirchase
        purchase_stock = PurchaseStock.objects.filter(purchase_voucher=purchase_details)
        for obj in purchase_stock:
            if obj.stock_item:
                obj.save()
                obj.stock_item.save()
                purchase_details.save()

        # saving the extra_charges
        extra_charge_purchases = PurchaseTerm.objects.filter(purchase_voucher=purchase_details.pk)
        for g in extra_charge_purchases:
            g.save()
            g.ledger.save()

        context['extra_charge_purchases_sum'] = extra_charge_purchases.aggregate(the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']

        # saving the gst ledger

        extra_gst_purchase = PurchaseTax.objects.filter(purchase_voucher=purchase_details.pk)
        for g in extra_gst_purchase:
            if g.ledger != None:
                g.save()
                g.ledger.save()

        tax_total = purchase_details.purchase_voucher_tax.aggregate(
            the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']
        extra_total = purchase_details.purchase_voucher_term.aggregate(
            the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']
        stock_total = purchase_details.purchase_voucher_stock.aggregate(
            the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']
        
        if tax_total or extra_total or stock_total:
            total = tax_total + extra_total + stock_total


        extra_gst_purchase_central = PurchaseTax.objects.filter(purchase_voucher=purchase_details.pk, ledger__tax_type='Central Tax').count()

        extra_gst_purchase_state = PurchaseTax.objects.filter(purchase_voucher=purchase_details.pk, ledger__tax_type='State Tax').count()

        extra_gst_purchase_integrated = PurchaseTax.objects.filter(purchase_voucher=purchase_details.pk, ledger__tax_type='Integrated Tax').count()

        context['extra_gst_purchase_central'] = extra_gst_purchase_central
        context['extra_gst_purchase_state'] = extra_gst_purchase_state
        context['extra_gst_purchase_integrated'] = extra_gst_purchase_integrated
        context['in_word'] = num2words(purchase_details.total, lang='en_IN')
        context['extra_charge_purchases'] = extra_charge_purchases
        context['extra_gst_purchase'] = extra_gst_purchase
        context['stocklist'] = qsob
        context['total'] = total
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        return context


class PurchaseCreateView(ProductExistsRequiredMixin,  LoginRequiredMixin, CreateView):
    """
    Purchase Create View
    """
    form_class = PurchaseForm
    template_name = 'stock_keeping/purchase/purchase_form.html'

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        purchase_voucher = PurchaseVoucher.objects.filter(company=company.pk, voucher_date__gte=period_selected.start_date, voucher_date__lte=period_selected.end_date).order_by('-id')
        for p in purchase_voucher:
            if p:
                return reverse('stock_keeping:purchasedetail', kwargs={'company_pk': company.pk, 'purchase_pk': p.pk, 'period_selected_pk': period_selected.pk})
            else:
                return reverse('stock_keeping:purchaselist', kwargs={'company_pk': company.pk, 'period_selected_pk': period_selected.pk})

    def get_context_data(self, **kwargs):
        context = super(PurchaseCreateView, self).get_context_data(**kwargs)
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        if self.request.POST:
            context['stocks'] = PURCHASE_STOCK_FORM_SET(self.request.POST, form_kwargs={'company': company.pk})
            context['extra_charges'] = PURCHASE_TERM_FORM_SET(self.request.POST, form_kwargs={'company': company.pk})
            if company.gst_enabled == 'Yes':
                context['extra_gst'] = PURCHASE_TAX_FORM_SET(self.request.POST, form_kwargs={'company': company.pk})
        else:
            context['stocks'] = PURCHASE_STOCK_FORM_SET(form_kwargs={'company': company.pk})
            context['extra_charges'] = PURCHASE_TERM_FORM_SET(form_kwargs={'company': company.pk})
            if company.gst_enabled == 'Yes':
                context['extra_gst'] = PURCHASE_TAX_FORM_SET(form_kwargs={'company': company.pk})
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        c = Company.objects.get(pk=self.kwargs['company_pk'])
        form.instance.company = c
        counter = PurchaseVoucher.objects.filter(user=self.request.user, company=c).count() + 1
        form.instance.counter = counter
        context = self.get_context_data()
        stocks = context['stocks']
        extra_charges = context['extra_charges']

        if not stocks.is_valid() or not extra_charges.is_valid():
            print("Not Valid")
            print(extra_charges.errors)
            return self.render_to_response(context)



        with transaction.atomic():
            self.object = form.save()
            stocks.instance = self.object
            stocks.save()
        
            self.object = form.save()
            extra_charges.instance = self.object
            extra_charges.save()

        
            with transaction.atomic():
                self.object = form.save()
                extra_gst = context['extra_gst']
                if extra_gst.is_valid():
                    extra_gst.instance = self.object
                    extra_gst.save()
        return super(PurchaseCreateView, self).form_valid(form)

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
    model = PurchaseVoucher
    form_class = PurchaseForm
    template_name = 'stock_keeping/purchase/purchase_form.html'

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        purchase_details = get_object_or_404(PurchaseVoucher, pk=self.kwargs['purchase_pk'])
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        return reverse('stock_keeping:purchasedetail', kwargs={'company_pk': company.pk, 'purchase_pk': purchase_details.pk, 'period_selected_pk': period_selected.pk})

    def get_object(self):
        company_pk = self.kwargs['company_pk']
        purchase_pk = self.kwargs['purchase_pk']
        get_object_or_404(Company, pk=company_pk)
        purchase = get_object_or_404(PurchaseVoucher, pk=purchase_pk)
        return purchase

    def test_func(self):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        purchase_voucher = self.get_object()
        if self.request.user in company.accountant.all() or self.request.user in company.purchase_personel.all() or self.request.user == purchase_voucher.user:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super(PurchaseUpdateView, self).get_context_data(**kwargs)
        purchase_details = get_object_or_404(PurchaseVoucher, pk=self.kwargs['purchase_pk'])
        purchase_voucher = PurchaseVoucher.objects.get(pk=purchase_details.pk)
        context['profile_details'] = Profile.objects.all()
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        if self.request.POST:
            context['stocks'] = PURCHASE_STOCK_FORM_SET(self.request.POST, instance=purchase_voucher, form_kwargs={'company': company.pk})
            context['extra_charges'] = PURCHASE_TERM_FORM_SET(self.request.POST, instance=purchase_voucher, form_kwargs={'company': company.pk})
            if company.gst_enabled == 'Yes':
                context['extra_gst'] = PURCHASE_TAX_FORM_SET(self.request.POST, instance=purchase_voucher, form_kwargs={'company': company.pk})
        else:
            context['stocks'] = PURCHASE_STOCK_FORM_SET(instance=purchase_voucher, form_kwargs={'company': company.pk})
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
        stockpurchase = context['stocks']
        if stockpurchase.is_valid():
            stockpurchase.save()
        extra_charges = context['extra_charges']
        if extra_charges.is_valid():
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
    model = PurchaseVoucher
    template_name = "stock_keeping/purchase/purchase_confirm_delete.html"

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        return reverse('stock_keeping:purchaselist', kwargs={'company_pk': company.pk, 'period_selected_pk': period_selected.pk})

    def get_object(self):
        company_pk = self.kwargs['company_pk']
        purchase_pk = self.kwargs['purchase_pk']
        get_object_or_404(Company, pk=company_pk)
        purchase = get_object_or_404(PurchaseVoucher, pk=purchase_pk)
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


##################################### PurchaseVoucher Register Views #####################################

class PurchaseRegisterView(ProductExistsRequiredMixin,  LoginRequiredMixin, ListView):
    """
    Purchase Register View
    """
    model = PurchaseVoucher
    template_name = 'stock_keeping/purchase/Purchase_Register.html'

    def get_context_data(self, **kwargs):
        context = super(PurchaseRegisterView, self).get_context_data(**kwargs)
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['company'] = company
        context['period_selected'] = period_selected

        results = collections.OrderedDict()
        result = PurchaseVoucher.objects.filter(company=company.pk, voucher_date__gte=period_selected.start_date, voucher_date__lt=period_selected.end_date).annotate(
            real_total=Case(When(total__isnull=True, then=0), default=F('total')))

        result_account = PurchaseVoucherAccounts.objects.filter(company=company.pk, voucher_date__gte=period_selected.start_date, voucher_date__lt=period_selected.end_date).annotate(
            real_total=Case(When(total__isnull=True, then=0), default=F('total')))

        date_cursor = period_selected.start_date

        z = 0

        while date_cursor <= period_selected.end_date:
            # print(date_cursor.month)
            month_partial_total = result.filter(voucher_date__month=date_cursor.month, voucher_date__year=date_cursor.year).aggregate(partial_total=Sum('real_total'))['partial_total']
            month_partial_total_accounts = result_account.filter(voucher_date__month=date_cursor.month, voucher_date__year=date_cursor.year).aggregate(partial_total=Sum('real_total'))['partial_total']

            if not month_partial_total:

                month_partial_total = 0

                g = month_partial_total

            else:

                g = month_partial_total

            if not month_partial_total_accounts:

                month_partial_total_accounts = 0

                f = month_partial_total_accounts

            else:

                f = month_partial_total_accounts

            e = f + g 
            z = z + e

            results[(date_cursor.month, date_cursor.year)] = [e, z]

            date_cursor += dateutil.relativedelta.relativedelta(months=1)

        total_purchase_inv = result.aggregate(the_sum=Coalesce(Sum('real_total'), Value(0)))['the_sum']

        total_purchase_accounts = result_account.aggregate(the_sum=Coalesce(Sum('real_total'), Value(0)))['the_sum']

        if not total_purchase_inv:
            total_purchase_inv = int(0)

        if not total_purchase_accounts:
            total_purchase_accounts = int(0)

        total_purchase = total_purchase_inv + total_purchase_accounts

        context['data'] = results.items()

        context['total_purchase'] = total_purchase
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        return context


@login_required
@product_1_activation
@company_account_with_invenroty_decorator
def purchase_register_datewise(request, month, year, company_pk, period_selected_pk):
    """
    Purchase Register View For a specific month
    """
    company = get_object_or_404(Company, pk=company_pk)
    period_selected = get_object_or_404(PeriodSelected, pk=period_selected_pk)

    result = PurchaseVoucher.objects.filter(company=company.pk, voucher_date__month=month, voucher_date__year=year, voucher_date__gte=period_selected.start_date, voucher_date__lt=period_selected.end_date).order_by('-voucher_date')

    result_account = PurchaseVoucherAccounts.objects.filter(company=company.pk, voucher_date__month=month, voucher_date__year=year, voucher_date__gte=period_selected.start_date, voucher_date__lt=period_selected.end_date).order_by('-voucher_date')

    total_purchase_inv = result.aggregate(partial_total=Sum('total'))['partial_total']

    total_purchase_accounts = result_account.aggregate(partial_total=Sum('total'))['partial_total']

    if not total_purchase_inv:
        total_purchase_inv = int(0)

    if not total_purchase_accounts:
        total_purchase_accounts = int(0)

    total_purchase = total_purchase_accounts + total_purchase_inv

    inbox = Message.objects.filter(reciever=request.user)
    inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
    send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

    context = {
        'company': company,
        'period_selected': period_selected,
        'result': result,
        'result_account' : result_account,
        'total_purchase': total_purchase,
        'm': calendar.month_name[int(month)],
        'y': year,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
    }

    return render(request, 'stock_keeping/purchase/Purchase_Register_Datewise.html', context)
