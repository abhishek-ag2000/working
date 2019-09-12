"""
Views for Sale Voucher
"""
import calendar
import collections
import dateutil
from num2words import num2words
from itertools import zip_longest
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
from accounts_mode_voucher.models_sale_accounts import SaleVoucherAccounts
from .decorators import company_account_with_invenroty_decorator
from .models_sale import SaleVoucher, SaleStock, SaleTerm, SaleTax
from .forms_sale import SaleForm, SALE_STOCK_FORM_SET, SALE_TERM_FORM_SET, SALE_TAX_FORM_SET


class SalesRegisterView(ProductExistsRequiredMixin, LoginRequiredMixin, ListView):
    """
    Sales Register View
    """
    model = SaleVoucher
    template_name = 'stock_keeping/sales/Sales_Register.html'

    def get_context_data(self, **kwargs):
        context = super(SalesRegisterView,
                        self).get_context_data(**kwargs)
        company = get_object_or_404(
            Company, pk=self.kwargs['company_pk'])
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['company'] = company
        context['period_selected'] = period_selected

        results = collections.OrderedDict()
        result = SaleVoucher.objects.filter(company=company.pk, voucher_date__gte=period_selected.start_date, voucher_date__lt=period_selected.end_date).annotate(
            real_total=Case(When(total__isnull=True, then=0), default=F('total')))

        result_accounts = SaleVoucherAccounts.objects.filter(company=company.pk, voucher_date__gte=period_selected.start_date, voucher_date__lt=period_selected.end_date).annotate(
            real_total=Case(When(total__isnull=True, then=0), default=F('total')))

        date_cursor = period_selected.start_date

        z = 0

        while date_cursor < period_selected.end_date:
            month_partial_total = result.filter(voucher_date__month=date_cursor.month, voucher_date__year=date_cursor.year).aggregate(
                partial_total=Sum('real_total'))['partial_total']
            month_partial_total_accounts = result_accounts.filter(voucher_date__month=date_cursor.month, voucher_date__year=date_cursor.year).aggregate(
                partial_total=Sum('real_total'))['partial_total']

            if not month_partial_total:

                month_partial_total = int(0)

                g = month_partial_total

            else:

                g = month_partial_total

            if not month_partial_total_accounts:

                month_partial_total_accounts = int(0)

                f = month_partial_total_accounts

            else:

                f = month_partial_total_accounts

            e = g + f

            z = z + e

            results[(date_cursor.month, date_cursor.year)] = [e, z]

            date_cursor += dateutil.relativedelta.relativedelta(months=1)

        total_sale_inv = result.aggregate(the_sum=Coalesce(
            Sum('real_total'), Value(0)))['the_sum']

        total_sale_ac = result_accounts.aggregate(the_sum=Coalesce(
            Sum('real_total'), Value(0)))['the_sum']

        if not total_sale_inv:
            total_sale_inv = int(0)

        if not total_sale_ac:
            total_sale_ac = int(0)

        context['Debit'] = e
        context['data'] = results.items()

        context['total_sale'] = total_sale_inv + total_sale_ac
        context['inbox'] = Message.objects.filter(
            reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        return context


@login_required
@product_1_activation
@company_account_with_invenroty_decorator
def SalesRegisterDatewise(request, month, year, company_pk, period_selected_pk):
    """
        Sales Register View For a specific month
        """
    company = get_object_or_404(Company, pk=company_pk)
    period_selected = get_object_or_404(PeriodSelected, pk=period_selected_pk)

    result = SaleVoucher.objects.filter(company=company.pk, voucher_date__month=month, voucher_date__year=year,
                                        voucher_date__gte=period_selected.start_date, voucher_date__lt=period_selected.end_date)

    result_accounts = SaleVoucherAccounts.objects.filter(company=company.pk, voucher_date__month=month, voucher_date__year=year,
                                        voucher_date__gte=period_selected.start_date, voucher_date__lt=period_selected.end_date)


    total_sales_inv = result.aggregate(partial_total=Sum('total'))[
        'partial_total']

    total_sales_ac = result_accounts.aggregate(partial_total=Sum('total'))[
        'partial_total']

    if not total_sales_inv:
        total_sales_inv = int(0)

    if not total_sales_ac:
        total_sales_ac = int(0)

    total_sales = total_sales_inv + total_sales_ac

    inbox = Message.objects.filter(reciever=request.user)
    inbox_count = inbox.aggregate(
        the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
    send_count = Message.objects.filter(sender=request.user).aggregate(
        the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

    context = {
        'company': company,
        'period_selected': period_selected,
        'result': result,
        'result_accounts' : result_accounts,
        'total_sales': total_sales,
        'm': calendar.month_name[int(month)],
        'y': year,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count
    }

    return render(request, 'stock_keeping/sales/Sales_Register_Datewise.html', context)


class SalesListView(ProductExistsRequiredMixin, LoginRequiredMixin, ListView):
    """
    Sales List View
    """
    model = SaleVoucher
    template_name = 'stock_keeping/sales/sales_list.html'
    paginate_by = 15

    def get_queryset(self):
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        return self.model.objects.filter(company=self.kwargs['company_pk'], voucher_date__gte=period_selected.start_date, voucher_date__lte=period_selected.end_date).order_by('-voucher_date')

    def get_context_data(self, **kwargs):
        context = super(SalesListView, self).get_context_data(**kwargs)
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
    model = SaleVoucher
    template_name = 'stock_keeping/sales/sales_details.html'

    def get_object(self):
        company_pk = self.kwargs['company_pk']
        sales_pk = self.kwargs['sales_pk']
        period_selected_pk = self.kwargs['period_selected_pk']
        get_object_or_404(PeriodSelected, pk=period_selected_pk)
        get_object_or_404(Company, pk=company_pk)
        sale_voucher = get_object_or_404(SaleVoucher, pk=sales_pk)
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
        sale_voucher = get_object_or_404(SaleVoucher, pk=self.kwargs['sales_pk'])
        qsjb = SaleStock.objects.filter(sale_voucher=sale_voucher.pk).order_by('-id')
        # saving the closing stock and stocks of particular sale_voucher
        context['stock_taxable_sales'] = qsjb.filter(
            stock_item__taxability='Taxable').aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        context['stock_nongst_sales'] = qsjb.filter(
            Q(stock_item__is_non_gst='Yes') |
            Q(stock_item__taxability='Unknown')).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        context['stock_exempt_sales'] = qsjb.filter(
            Q(stock_item__taxability='Exempt') |
            Q(stock_item__taxability='Nil Rated')).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        for obj in qsjb:
            if obj.stock_item:
                obj.save()
                obj.stock_item.save()
                sale_voucher.save()

        context['stocklist'] = qsjb
        # saving the extra_charges
        extra_charge_sale = SaleTerm.objects.filter(sale_voucher=sale_voucher.pk).order_by('-id')
        for g in extra_charge_sale:
            if g.ledger != None:
                g.save()
                g.ledger.save()
                sale_voucher.save()

        context['extra_charge_sale_total'] = extra_charge_sale.aggregate(
            the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']

        context['extra_charge_sale_count'] = extra_charge_sale.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        extra_gst_sale = SaleTax.objects.filter(sale_voucher=sale_voucher.pk)
        for g in extra_gst_sale:
            if g.ledger != None:
                g.save()
                g.ledger.save()

        extra_gst_sales_central = SaleTax.objects.filter(
            sale_voucher=sale_voucher.pk, ledger__tax_type='Central Tax').count()

        extra_gst_sales_state = SaleTax.objects.filter(
            sale_voucher=sale_voucher.pk, ledger__tax_type='State Tax').count()

        extra_gst_sales_integrated = SaleTax.objects.filter(
            sale_voucher=sale_voucher.pk, ledger__tax_type='Integrated Tax').count()

        tax_invoice_total = sale_voucher.sale_voucher_tax.aggregate(
            the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']
        extra_total = sale_voucher.sale_voucher_term.aggregate(
            the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']
        stock_total = sale_voucher.sale_voucher_stock.aggregate(
            the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']

        # total_cgst_stock = sale_voucher.sale_voucher_stock.aggregate(
        # the_sum=Coalesce(Sum('cgst_total'), Value(0)))['the_sum']
        # total_sgst_stock = sale_voucher.sale_voucher_stock.aggregate(
        #     the_sum=Coalesce(Sum('sgst_total'), Value(0)))['the_sum']
        # total_igst_stock = sale_voucher.sale_voucher_stock.aggregate(
        #     the_sum=Coalesce(Sum('igst_total'), Value(0)))['the_sum']

        # total_cgst_extra = sale_voucher.sale_voucher_term.aggregate(
        #     the_sum=Coalesce(Sum('cgst_total'), Value(0)))['the_sum']
        # total_sgst_extra = sale_voucher.sale_voucher_term.aggregate(
        #     the_sum=Coalesce(Sum('sgst_total'), Value(0)))['the_sum']
        # total_igst_extra = sale_voucher.sale_voucher_term.aggregate(
        #     the_sum=Coalesce(Sum('igst_total'), Value(0)))['the_sum']

        # cgst_total = total_cgst_stock + total_cgst_extra
        # sale_voucher.cgst_total = cgst_total

        # sgst_total = total_sgst_stock + total_sgst_extra
        # sale_voucher.sgst_total = sgst_total

        # igst_total = total_igst_stock + total_igst_extra
        # sale_voucher.igst_total = igst_total


        if tax_invoice_total or extra_total or stock_total:
            total = tax_invoice_total + extra_total + stock_total

        sale_voucher.total = total  
        sale_voucher.save()

        context['extra_gst_sales_central'] = extra_gst_sales_central
        context['extra_gst_sales_state'] = extra_gst_sales_state
        context['extra_gst_sales_integrated'] = extra_gst_sales_integrated
        context['in_word'] = num2words(sale_voucher.total, lang='en_IN')
        context['extra_charge_sales'] = extra_charge_sale
        context['extra_gst_sale'] = extra_gst_sale
        context['total'] = total
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
    form_class = SaleForm
    template_name = 'stock_keeping/sales/sales_form.html'

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        sales_list = SaleVoucher.objects.filter(company=company.pk).order_by('-id')
        for sale_voucher in sales_list:
            if sale_voucher:
                return reverse('stock_keeping:salesdetail', kwargs={'company_pk': company.pk, 'sales_pk': sale_voucher.pk, 'period_selected_pk': period_selected.pk})

    def form_valid(self, form):
        form.instance.user = self.request.user
        company = Company.objects.get(pk=self.kwargs['company_pk'])
        form.instance.company = company
        counter = SaleVoucher.objects.filter(user=self.request.user, company=company).count() + 1
        form.instance.counter = counter
        context = self.get_context_data()

        stocksales = context['stocksales']
        extra_charges = context['extra_charges']

        if not stocksales.is_valid() or not extra_charges.is_valid():
            # formset for stock item is invalid; render the form with error
            print('Sales form not valid')
            return self.render_to_response(context)
            

        if company.gst_enabled == 'Yes':
            extra_gst = context['extra_gst']
            if not extra_gst.is_valid():
                return self.render_to_response(context)

        with transaction.atomic():
            self.object = form.save()
            stocksales.instance = self.object
            stocksales.save()

            self.object = form.save()
            extra_charges.instance = self.object
            extra_charges.save()

            if company.gst_enabled == 'Yes':
                self.object = form.save()
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
        company = get_object_or_404(
            Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        if self.request.POST:
            context['stocksales'] = SALE_STOCK_FORM_SET(self.request.POST, form_kwargs={'company': company.pk})
            context['extra_charges'] = SALE_TERM_FORM_SET(
                self.request.POST, form_kwargs={'company': company.pk})
            if company.gst_enabled == 'Yes':
                context['extra_gst'] = SALE_TAX_FORM_SET(
                    self.request.POST, form_kwargs={'company': company.pk})
        else:
            context['stocksales'] = SALE_STOCK_FORM_SET(form_kwargs={'company': company.pk})
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
    model = SaleVoucher
    form_class = SaleForm
    template_name = 'stock_keeping/sales/sales_form.html'

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        sale_voucher = get_object_or_404(SaleVoucher, pk=self.kwargs['sales_pk'])
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        return reverse('stock_keeping:salesdetail', kwargs={'company_pk': company.pk, 'sales_pk': sale_voucher.pk, 'period_selected_pk': period_selected.pk})

    def get_object(self):
        return get_object_or_404(SaleVoucher, pk=self.kwargs['sales_pk'])

    def test_func(self):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        sale_voucher = self.get_object()
        if self.request.user in company.accountant.all() or self.request.user in company.sale_personel.all() or self.request.user == sale_voucher.user:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super(SalesUpdateView, self).get_context_data(**kwargs)

        sale_voucher = get_object_or_404(SaleVoucher, pk=self.kwargs['sales_pk'])
        sales_particular = SaleVoucher.objects.get(pk=sale_voucher.pk)
        context['profile_details'] = Profile.objects.all()
        company = get_object_or_404(
            Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        if self.request.POST:
            #context['stocksales'] = SaleStockFormSet(self.request.POST, instance=sales_particular, form_kwargs={'company': company.pk})
            context['stocksales'] = SALE_STOCK_FORM_SET(self.request.POST, instance=sales_particular, form_kwargs={'company': company.pk})
            context['extra_charges'] = SALE_TERM_FORM_SET(
                self.request.POST, instance=sales_particular, form_kwargs={'company': company.pk})
            if company.gst_enabled == 'Yes':
                context['extra_gst'] = SALE_TAX_FORM_SET(
                    self.request.POST, instance=sales_particular, form_kwargs={'company': company.pk})
        else:
            #context['stocksales'] = SaleStockFormSet(instance=sales_particular, form_kwargs={'company': company.pk})
            context['stocksales'] = SALE_STOCK_FORM_SET(instance=sales_particular, form_kwargs={'company': company.pk})
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
        stocksales = context['stocksales']
        extra_charges = context['extra_charges']

        if not stocksales.is_valid() or not extra_charges.is_valid():
            # formset for stock item is invalid; render the form with error
            return self.render_to_response(context)

        if company.gst_enabled == 'Yes':
            extra_gst = context['extra_gst']
            if not extra_gst.is_valid():
                return self.render_to_response(context)

        with transaction.atomic():
            stocksales.save()
            extra_charges.save()
             
            if company.gst_enabled == 'Yes':
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
    model = SaleVoucher
    template_name = "stock_keeping/sales/sales_confirm_delete.html"

    def get_success_url(self, **kwargs):
        company = get_object_or_404(
            Company, pk=self.kwargs['company_pk'])
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        return reverse('stock_keeping:saleslist', kwargs={'company_pk': company.pk, 'period_selected_pk': period_selected.pk})

    def get_object(self):
        company_pk = self.kwargs['company_pk']
        sales_pk = self.kwargs['sales_pk']
        get_object_or_404(Company, pk=company_pk)
        sale_voucher = get_object_or_404(SaleVoucher, pk=sales_pk)
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
        context['profile_details'] = Profile.objects.all()
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
