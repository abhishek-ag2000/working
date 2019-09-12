"""
Views for Stock Group and Items
"""
import calendar
import collections
from itertools import zip_longest
import dateutil
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.db.models.functions import Coalesce
from django.db.models import Case, When, Value, Sum, Count, F, Subquery, OuterRef, ExpressionWrapper, FloatField
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse
from company.models import Company
from user_profile.models import Profile
from messaging.models import Message

from ecommerce_integration.decorators import product_1_activation
from accounting_entry.models import PeriodSelected
from accounting_entry.mixins import ProductExistsRequiredMixin
from .mixins import CompanyAccountsWithInventoryMixin
from .decorators import company_account_with_invenroty_decorator
from .models import StockGroup, StockItem, StockBalance
from .models_sale import SaleStock
from .models_purchase import PurchaseStock
from .models_debit_note import DebitNoteStock
from .models_credit_note import CreditNoteStock
from .forms import StockGroupForm, StockItemForm


class StockGroupListView(ProductExistsRequiredMixin,  LoginRequiredMixin, ListView):
    """
    Stock Group List View
    """
    context_object_name = 'stockgroup_list'
    model = StockGroup
    template_name = 'stock_keeping/stockgroup/stockgroup_list.html'
    paginate_by = 15

    def get_queryset(self):
        return self.model.objects.filter(company=self.kwargs['company_pk'])

    def get_context_data(self, **kwargs):
        context = super(StockGroupListView, self).get_context_data(**kwargs)

        context['profile_details'] = Profile.objects.all()
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
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


class StockGroupDetailView(ProductExistsRequiredMixin,  UserPassesTestMixin, LoginRequiredMixin, DetailView):
    """
    Stock Group Details View
    """
    context_object_name = 'stockgroup_details'
    model = StockGroup
    template_name = 'stock_keeping/stockgroup/stockgroup_details.html'

    def get_object(self):
        return get_object_or_404(StockGroup, pk=self.kwargs['stock_group_pk'])

    def test_func(self):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        stock_group = self.get_object()
        return self.request.user in company.accountant.all() or self.request.user == stock_group.user

    def get_context_data(self, **kwargs):
        context = super(StockGroupDetailView, self).get_context_data(**kwargs)

        context['profile_details'] = Profile.objects.all()
        stock_group = get_object_or_404(
            StockGroup, pk=self.kwargs['stock_group_pk'])
        context['stock_group'] = stock_group
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
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


class StockGroupCreateView(ProductExistsRequiredMixin,  LoginRequiredMixin, CreateView):
    """
    Stock Group Create View
    """
    form_class = StockGroupForm
    template_name = "stock_keeping/stockgroup/stockgroup_form.html"

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        return reverse('stock_keeping:stockgrouplist', kwargs={'company_pk': company.pk, 'period_selected_pk': period_selected.pk})

    def form_valid(self, form):
        form.instance.user = self.request.user
        company = Company.objects.get(pk=self.kwargs['company_pk'])
        form.instance.company = company
        counter = StockGroup.objects.filter(
            user=self.request.user, company=company).count() + 1
        form.instance.counter = counter
        return super(StockGroupCreateView, self).form_valid(form)

    def get_form_kwargs(self):
        data = super(StockGroupCreateView, self).get_form_kwargs()
        data.update(
            user=self.request.user,
            company=Company.objects.get(pk=self.kwargs['company_pk'])
        )
        return data

    def get_context_data(self, **kwargs):
        context = super(StockGroupCreateView, self).get_context_data(**kwargs)

        context['profile_details'] = Profile.objects.all()
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
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


class StockGroupUpdateView(ProductExistsRequiredMixin,  UserPassesTestMixin, LoginRequiredMixin, UpdateView):
    """
    Stock Group Update View
    """
    model = StockGroup
    form_class = StockGroupForm
    template_name = "stock_keeping/stockgroup/stockgroup_form.html"

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        stockgroup_details = get_object_or_404(
            StockGroup, pk=self.kwargs['stock_group_pk'])
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        return reverse('stock_keeping:stockgroupdetail', kwargs={'company_pk': company.pk, 'stock_group_pk': stockgroup_details.pk, 'period_selected_pk': period_selected.pk})

    def get_object(self):
        return get_object_or_404(StockGroup, pk=self.kwargs['stock_group_pk'])

    def test_func(self):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        stock_group = self.get_object()
        return self.request.user in company.accountant.all() or self.request.user == stock_group.user

    def get_form_kwargs(self):
        data = super(StockGroupUpdateView, self).get_form_kwargs()
        data.update(
            user=self.request.user,
            company=Company.objects.get(pk=self.kwargs['company_pk'])
        )
        return data

    def get_context_data(self, **kwargs):
        context = super(StockGroupUpdateView, self).get_context_data(**kwargs)

        context['profile_details'] = Profile.objects.all()
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
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


class StockGroupDeleteView(ProductExistsRequiredMixin,  UserPassesTestMixin, LoginRequiredMixin, DeleteView):
    """
    Stock Group Update View
    """
    model = StockGroup
    template_name = "stock_keeping/stockgroup/stockgroup_confirm_delete.html"

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        return reverse('stock_keeping:stockgrouplist', kwargs={'company_pk': company.pk, 'period_selected_pk': period_selected.pk})

    def get_object(self):
        return get_object_or_404(StockGroup, pk=self.kwargs['stock_group_pk'])

    def test_func(self):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        stock_group = self.get_object()
        return self.request.user in company.accountant.all() or self.request.user == stock_group.user

    def get_context_data(self, **kwargs):
        context = super(StockGroupDeleteView, self).get_context_data(**kwargs)

        context['profile_details'] = Profile.objects.all()
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
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

##################################### Stock Items Monthly Views #####################################


@login_required
@product_1_activation
@company_account_with_invenroty_decorator
def stock_item_month_view(request, company_pk, stock_item_pk, period_selected_pk):
    """
    Monthly Closing Stock view in respect of weighted average
    """
    company = get_object_or_404(Company, pk=company_pk)
    period_selected = get_object_or_404(PeriodSelected, pk=period_selected_pk)
    stock_item = get_object_or_404(StockItem, pk=stock_item_pk)

    opening_balance = stock_item.opening
    opening_quantity = stock_item.quantity
    results = collections.OrderedDict()

    result1 = SaleStock.objects.filter(
        sale_voucher__company=company.pk,
        stock_item=stock_item.pk,
        sale_voucher__voucher_date__gte=period_selected.start_date,
        sale_voucher__voucher_date__lt=period_selected.end_date).annotate(real_total_quantity_s=Case(When(quantity__isnull=True, then=0), default=F('quantity')))

    result2 = PurchaseStock.objects.filter(
        purchase_voucher__company=company.pk,
        stock_item=stock_item.pk,
        purchase_voucher__voucher_date__gte=period_selected.start_date,
        purchase_voucher__voucher_date__lt=period_selected.end_date).annotate(real_total_quantity_p=Case(When(quantity__isnull=True, then=0), default=F('quantity')))

    result3 = PurchaseStock.objects.filter(
        purchase_voucher__company=company.pk,
        stock_item=stock_item.pk,
        purchase_voucher__voucher_date__gte=period_selected.start_date,
        purchase_voucher__voucher_date__lt=period_selected.end_date).annotate(real_total_p=Case(When(total__isnull=True, then=0), default=F('total')))

    result4 = SaleStock.objects.filter(
        sale_voucher__company=company.pk,
        stock_item=stock_item.pk,
        sale_voucher__voucher_date__gte=period_selected.start_date,
        sale_voucher__voucher_date__lt=period_selected.end_date).annotate(real_total_s=Case(When(total__isnull=True, then=0), default=F('total')))

    result5 = DebitNoteStock.objects.filter(
        debit_note__company=company.pk,
        stock_item=stock_item.pk,
        debit_note__voucher_date__gte=period_selected.start_date,
        debit_note__voucher_date__lt=period_selected.end_date).annotate(real_total_d=Case(When(total__isnull=True, then=0), default=F('total')))

    result6 = DebitNoteStock.objects.filter(
        debit_note__company=company.pk,
        stock_item=stock_item.pk,
        debit_note__voucher_date__gte=period_selected.start_date,
        debit_note__voucher_date__lt=period_selected.end_date).annotate(real_total_quantity_d=Case(When(quantity__isnull=True, then=0), default=F('quantity')))

    result7 = CreditNoteStock.objects.filter(
        credit_note__company=company.pk,
        stock_item=stock_item.pk,
        credit_note__voucher_date__gte=period_selected.start_date,
        credit_note__voucher_date__lt=period_selected.end_date).annotate(real_total_c=Case(When(total__isnull=True, then=0), default=F('total')))

    result8 = CreditNoteStock.objects.filter(
        credit_note__company=company.pk,
        stock_item=stock_item.pk,
        credit_note__voucher_date__gte=period_selected.start_date,
        credit_note__voucher_date__lt=period_selected.end_date).annotate(real_total_quantity_c=Case(When(quantity__isnull=True, then=0), default=F('quantity')))

    date_cursor = period_selected.start_date

    w = 0
    x = 0
    y = 0
    z = 0

    while date_cursor <= period_selected.end_date:
        month_partial_purchase_quantity = result2.filter(
            purchase_voucher__voucher_date__month=date_cursor.month,
            purchase_voucher__voucher_date__year=date_cursor.year).aggregate(
                partial_total_purchase_quantity=Sum('real_total_quantity_p'))['partial_total_purchase_quantity']

        month_partial_sale_quantity = result1.filter(
            sale_voucher__voucher_date__month=date_cursor.month,
            sale_voucher__voucher_date__year=date_cursor.year).aggregate(
                partial_total_sale_quantity=Sum('real_total_quantity_s'))['partial_total_sale_quantity']

        month_partial_purchase = result3.filter(
            purchase_voucher__voucher_date__month=date_cursor.month,
            purchase_voucher__voucher_date__year=date_cursor.year).aggregate(
                partial_total_purchase=Sum('real_total_p'))['partial_total_purchase']

        month_partial_sale = result4.filter(
            sale_voucher__voucher_date__month=date_cursor.month,
            sale_voucher__voucher_date__year=date_cursor.year).aggregate(partial_total_sale=Sum('real_total_s'))['partial_total_sale']

        month_partial_debit_quantity = result6.filter(
            debit_note__voucher_date__month=date_cursor.month,
            debit_note__voucher_date__year=date_cursor.year).aggregate(
                partial_total_debit_quantity=Sum('real_total_quantity_d'))['partial_total_debit_quantity']

        month_partial_debit = result5.filter(
            debit_note__voucher_date__month=date_cursor.month,
            debit_note__voucher_date__year=date_cursor.year).aggregate(
                partial_total_debit=Sum('real_total_d'))['partial_total_debit']

        month_partial_credit = result7.filter(
            credit_note__voucher_date__month=date_cursor.month,
            credit_note__voucher_date__year=date_cursor.year).aggregate(
                partial_total_credit=Sum('real_total_c'))['partial_total_credit']

        month_partial_credit_quantity = result8.filter(
            credit_note__voucher_date__month=date_cursor.month,
            credit_note__voucher_date__year=date_cursor.year).aggregate(
                partial_total_credit_quantity=Sum('real_total_quantity_c'))['partial_total_credit_quantity']

        if not month_partial_purchase_quantity:
            month_partial_purchase_quantity = 0
            if not month_partial_debit_quantity:
                e = month_partial_purchase_quantity
            else:
                e = month_partial_purchase_quantity - month_partial_debit_quantity
        else:
            if not month_partial_debit_quantity:
                e = month_partial_purchase_quantity
            else:
                e = month_partial_purchase_quantity - month_partial_debit_quantity

        if not month_partial_sale_quantity:

            month_partial_sale_quantity = 0
            if not month_partial_credit_quantity:
                f = month_partial_sale_quantity
            else:
                f = month_partial_sale_quantity - month_partial_credit_quantity
        else:
            if not month_partial_credit_quantity:
                f = month_partial_sale_quantity
            else:
                f = month_partial_sale_quantity - month_partial_credit_quantity

        if not month_partial_purchase:
            month_partial_purchase = 0
            if not month_partial_debit:
                g = month_partial_purchase
            else:
                g = month_partial_purchase - month_partial_debit
        else:
            if not month_partial_debit:
                g = month_partial_purchase
            else:
                g = month_partial_purchase - month_partial_debit

        if not month_partial_sale:

            month_partial_sale = 0
            if not month_partial_credit:
                h = month_partial_sale
            else:
                h = month_partial_sale - month_partial_credit
        else:
            if not month_partial_credit:
                h = month_partial_sale
            else:
                h = month_partial_sale - month_partial_credit

        w = w + e - f 

        x = x + e

        y = y + g

        if x == 0:
            z = y + opening_balance
        else:
            z = ((y + opening_balance) / (x + opening_quantity)
                 * (w + opening_quantity))

        results[(date_cursor.month, date_cursor.year)] = [w, e, f, g, h, z]
        date_cursor += dateutil.relativedelta.relativedelta(months=1)

    total_purchase_quantity_sub = result2.aggregate(
        the_sum=Coalesce(Sum('real_total_quantity_p'), Value(0)))['the_sum']
    total_sale_quantity_sub = result1.aggregate(the_sum=Coalesce(
        Sum('real_total_quantity_s'), Value(0)))['the_sum']
    total_purchase_sub = result3.aggregate(
        the_sum=Coalesce(Sum('real_total_p'), Value(0)))['the_sum']
    total_sale_sub = result4.aggregate(the_sum=Coalesce(
        Sum('real_total_s'), Value(0)))['the_sum']
    total_debit_quantity = result6.aggregate(the_sum=Coalesce(
        Sum('real_total_quantity_d'), Value(0)))['the_sum']
    total_debit = result5.aggregate(the_sum=Coalesce(
        Sum('real_total_d'), Value(0)))['the_sum']
    total_credit_quantity = result8.aggregate(the_sum=Coalesce(
        Sum('real_total_quantity_c'), Value(0)))['the_sum']
    total_credit = result7.aggregate(the_sum=Coalesce(
        Sum('real_total_c'), Value(0)))['the_sum']

    total_purchase_quantity = total_purchase_quantity_sub - total_debit_quantity


    total_purchase = total_purchase_sub - total_debit


    total_sale_quantity = total_sale_quantity_sub - total_credit_quantity

    total_sale = total_sale_sub - total_credit

    Closing_balance = z

    inbox = Message.objects.filter(reciever=request.user)
    inbox_count = inbox.aggregate(
        the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
    send_count = Message.objects.filter(sender=request.user).aggregate(
        the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

    context = {
        'company': company,
        'stock_item': stock_item,
        'period_selected': period_selected,
        'total_purchase_quantity': total_purchase_quantity,
        'total_sale_quantity': total_sale_quantity,
        'total_purchase': total_purchase,
        'total_sale': total_sale,
        'data': results.items(),
        'Closing_balance': Closing_balance,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count
    }

    return render(request, 'stock_keeping/stock_item/Stock_Monthly.html', context)


@login_required
@product_1_activation
@company_account_with_invenroty_decorator
def StockSummaryDatewise(request, month, year, company_pk, stock_item_pk, period_selected_pk):
    """
    Daily Closing Stock View of a Single Month in respect of weighted Average
    """
    company = get_object_or_404(Company, pk=company_pk)
    period_selected = get_object_or_404(PeriodSelected, pk=period_selected_pk)
    stock_item = get_object_or_404(StockItem, pk=stock_item_pk)

    result1 = SaleStock.objects.filter(sale_voucher__company=company.pk, stock_item=stock_item.pk, sale_voucher__voucher_date__month=month, sale_voucher__voucher_date__year=year,
                                       sale_voucher__voucher_date__gte=period_selected.start_date, sale_voucher__voucher_date__lte=period_selected.end_date)
    result2 = PurchaseStock.objects.filter(purchase_voucher__company=company.pk, stock_item=stock_item.pk, purchase_voucher__voucher_date__month=month, purchase_voucher__voucher_date__year=year,
                                           purchase_voucher__voucher_date__gte=period_selected.start_date, purchase_voucher__voucher_date__lte=period_selected.end_date)
    result3 = PurchaseStock.objects.filter(purchase_voucher__company=company.pk, stock_item=stock_item.pk, purchase_voucher__voucher_date__month=month, purchase_voucher__voucher_date__year=year,
                                           purchase_voucher__voucher_date__gte=period_selected.start_date, purchase_voucher__voucher_date__lte=period_selected.end_date)
    result4 = SaleStock.objects.filter(sale_voucher__company=company.pk, stock_item=stock_item.pk, sale_voucher__voucher_date__month=month, sale_voucher__voucher_date__year=year,
                                       sale_voucher__voucher_date__gte=period_selected.start_date, sale_voucher__voucher_date__lte=period_selected.end_date)
    result5 = DebitNoteStock.objects.filter(debit_note__company=company.pk, stock_item=stock_item.pk, debit_note__voucher_date__month=month, debit_note__voucher_date__year=year,
                                            debit_note__voucher_date__gte=period_selected.start_date, debit_note__voucher_date__lte=period_selected.end_date)
    result6 = DebitNoteStock.objects.filter(debit_note__company=company.pk, stock_item=stock_item.pk, debit_note__voucher_date__month=month, debit_note__voucher_date__year=year,
                                            debit_note__voucher_date__gte=period_selected.start_date, debit_note__voucher_date__lte=period_selected.end_date)
    result7 = CreditNoteStock.objects.filter(credit_note__company=company.pk, stock_item=stock_item.pk, credit_note__voucher_date__month=month, credit_note__voucher_date__year=year,
                                             credit_note__voucher_date__gte=period_selected.start_date, credit_note__voucher_date__lte=period_selected.end_date)

    new = zip_longest(result1, result2, result6, result7)

    total_purchase_quantity_m = result2.aggregate(
        the_sum=Coalesce(Sum('quantity'), Value(0)))['the_sum']
    total_sale_quantity_m = result1.aggregate(
        the_sum=Coalesce(Sum('quantity'), Value(0)))['the_sum']
    total_purchase_m = result3.aggregate(
        the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']
    total_sale_m = result4.aggregate(
        the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']
    total_debit_quantity = result5.aggregate(
        the_sum=Coalesce(Sum('quantity'), Value(0)))['the_sum']
    total_debit_note = result6.aggregate(
        the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']
    total_credit_quantity = result7.aggregate(
        the_sum=Coalesce(Sum('quantity'), Value(0)))['the_sum']
    total_credit_notes = result7.aggregate(
        the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']

    total_purchase_quantity = total_purchase_quantity_m - total_debit_quantity
    total_purchase = total_purchase_m - total_debit_note
    total_sale_quantity = total_sale_quantity_m - total_credit_quantity
    total_sale = total_sale_m - total_credit_notes

    qs = SaleStock.objects.filter(sale_voucher__company=company.pk, stock_item=stock_item.pk, sale_voucher__voucher_date__month__gte=period_selected.start_date.month,
                                  sale_voucher__voucher_date__month=month, sale_voucher__voucher_date__year__gte=period_selected.start_date.year, sale_voucher__voucher_date__year__lte=year)
    qs2 = PurchaseStock.objects.filter(purchase_voucher__company=company.pk, stock_item=stock_item.pk, purchase_voucher__voucher_date__month__gte=period_selected.start_date.month,
                                       purchase_voucher__voucher_date__month=month, purchase_voucher__voucher_date__year__gte=period_selected.start_date.year, purchase_voucher__voucher_date__year__lte=year)
    qs3 = PurchaseStock.objects.filter(purchase_voucher__company=company.pk, stock_item=stock_item.pk, purchase_voucher__voucher_date__month__gte=period_selected.start_date.month,
                                       purchase_voucher__voucher_date__month=month, purchase_voucher__voucher_date__year__gte=period_selected.start_date.year, purchase_voucher__voucher_date__year__lte=year)
    qs4 = SaleStock.objects.filter(sale_voucher__company=company.pk, stock_item=stock_item.pk, sale_voucher__voucher_date__month__gte=period_selected.start_date.month,
                                   sale_voucher__voucher_date__month=month, sale_voucher__voucher_date__year__gte=period_selected.start_date.year, sale_voucher__voucher_date__year__lte=year)
    qs5 = DebitNoteStock.objects.filter(debit_note__company=company.pk, stock_item=stock_item.pk, debit_note__voucher_date__month__gte=period_selected.start_date.month,
                                        debit_note__voucher_date__month=month, debit_note__voucher_date__year__gte=period_selected.start_date.year, debit_note__voucher_date__year__lte=year)
    qs6 = DebitNoteStock.objects.filter(debit_note__company=company.pk, stock_item=stock_item.pk, debit_note__voucher_date__month__gte=period_selected.start_date.month,
                                        debit_note__voucher_date__month=month, debit_note__voucher_date__year__gte=period_selected.start_date.year, debit_note__voucher_date__year__lte=year)
    qs7 = CreditNoteStock.objects.filter(credit_note__company=company.pk, stock_item=stock_item.pk, credit_note__voucher_date__month__gte=period_selected.start_date.month,
                                         credit_note__voucher_date__month=month, credit_note__voucher_date__year__gte=period_selected.start_date.year, credit_note__voucher_date__year__lte=year)

    total_debit_sales_quantity_m = qs.aggregate(
        the_sum=Coalesce(Sum('quantity'), Value(0)))['the_sum']
    total_credit_purchase_quantity = qs2.aggregate(
        the_sum=Coalesce(Sum('quantity'), Value(0)))['the_sum']
    total_debit_purchase_total = qs3.aggregate(
        the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']
    total_creditpl_m = qs4.aggregate(
        the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']
    total_debit_note_sum = qs5.aggregate(
        the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']
    total_debit_note_qunatity_sum = qs6.aggregate(
        the_sum=Coalesce(Sum('quantity'), Value(0)))['the_sum']
    total_credit_note_sum = qs7.aggregate(
        the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']
    total_credit_note_qunatity_sum = qs7.aggregate(
        the_sum=Coalesce(Sum('quantity'), Value(0)))['the_sum']

    total_credit = total_credit_purchase_quantity - total_debit_note_qunatity_sum

    total_debitpl = total_debit_purchase_total - total_debit_note_sum

    total_debit_sales_quantity = total_debit_sales_quantity_m - \
            total_credit_note_qunatity_sum

    # if total_credit_note_sum:
    #     total_creditpl = total_creditpl_m - total_credit_note_sum

    closing_quantity = stock_item.quantity + \
        total_credit - total_debit_sales_quantity

    if total_credit != 0:
        closing_balance = (((total_debitpl + stock_item.opening) /
                            (total_credit + stock_item.quantity)) * closing_quantity)
    else:
        closing_balance = ((total_debitpl + stock_item.opening)
                           * (closing_quantity + stock_item.quantity))

    inbox = Message.objects.filter(reciever=request.user)
    inbox_count = inbox.aggregate(
        the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
    send_count = Message.objects.filter(sender=request.user).aggregate(
        the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

    context = {

        'company': company,
        'period_selected': period_selected,
        'stock_item': stock_item,
        'm': calendar.month_name[int(month)],
        'y': year,
        'new': new,
        'closing_quantity': closing_quantity,
        'closing_balance': closing_balance,
        'total_purchase_quantity': total_purchase_quantity,
        'total_sale_quantity': total_sale_quantity,
        'total_purchase': total_purchase,
        'total_sale': total_sale,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
    }

    return render(request, 'stock_keeping/stock_item/stock_daily.html', context)


##################################### Stock Items Views #####################################

class ClosingListView(ProductExistsRequiredMixin,  LoginRequiredMixin, ListView):
    """
    Stock wise Closing Stock Summary View in respect of weighted average
    """
    model = StockItem
    paginate_by = 15

    def get_template_names(self):
        return ['stock_keeping/closing_stock.html']

    def get_queryset(self):
        return self.model.objects.filter(company=self.kwargs['company_pk']).order_by('-id')

    def get_context_data(self, **kwargs):
        context = super(ClosingListView, self).get_context_data(**kwargs)
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        context['stock_journal'] = StockBalance.objects.filter(
            company=company.pk).order_by('-closing_stock')


        purchase_stock = PurchaseStock.objects.filter(purchase_voucher__company=company,stock_item=OuterRef('pk'),purchase_voucher__voucher_date__gte=period_selected.start_date, purchase_voucher__voucher_date__lte=period_selected.end_date).values('stock_item')
        purchase_stock_total = PurchaseStock.objects.filter(purchase_voucher__company=company,stock_item=OuterRef('pk'),purchase_voucher__voucher_date__gte=period_selected.start_date, purchase_voucher__voucher_date__lte=period_selected.end_date).values('stock_item')
        sales_stock = SaleStock.objects.filter(sale_voucher__company=company,stock_item=OuterRef('pk'),sale_voucher__voucher_date__gte=period_selected.start_date, sale_voucher__voucher_date__lte=period_selected.end_date).values('stock_item')
        debit_note_stock = DebitNoteStock.objects.filter(debit_note__company=company,stock_item=OuterRef('pk'),debit_note__voucher_date__gte=period_selected.start_date, debit_note__voucher_date__lte=period_selected.end_date).values('stock_item')
        credit_note_stock = CreditNoteStock.objects.filter(credit_note__company=company,stock_item=OuterRef('pk'),credit_note__voucher_date__gte=period_selected.start_date, credit_note__voucher_date__lte=period_selected.end_date).values('stock_item')

        total_purchase_quantity = purchase_stock.annotate(
        quantity_total=Coalesce(Sum('quantity'), Value(0))).values('quantity_total')

        total_purchase_value = purchase_stock_total.annotate(
        total=Coalesce(Sum('total'), Value(0))).values('total')

        total_sales_quantity = sales_stock.annotate(
        quantity_total=Coalesce(Sum('quantity'), Value(0))).values('quantity_total')

        total_debit_note_quantity = debit_note_stock.annotate(
        quantity_total=Coalesce(Sum('quantity'), Value(0))).values('quantity_total')

        total_credit_note_quantity = credit_note_stock.annotate(
        quantity_total=Coalesce(Sum('quantity'), Value(0))).values('quantity_total')

        stock_list = StockItem.objects.filter(company=company).annotate(
            purchase_quantity = Coalesce(Subquery(total_purchase_quantity,output_field=FloatField()), Value(0)),
            sales_quantity = Coalesce(Subquery(total_sales_quantity,output_field=FloatField()), Value(0)),
            debit_note_quantity = Coalesce(Subquery(total_debit_note_quantity,output_field=FloatField()), Value(0)),
            credit_note_quantity = Coalesce(Subquery(total_credit_note_quantity,output_field=FloatField()), Value(0)),
            purchase_value = Coalesce(Subquery(total_purchase_value,output_field=FloatField()), Value(0)),
        )

        stock_quantities = stock_list.annotate(
          total_purchase_quantity_final = ExpressionWrapper(F('purchase_quantity') - F('debit_note_quantity'), output_field=FloatField()),
          total_sales_quantity_final = ExpressionWrapper(F('sales_quantity') - F('credit_note_quantity'), output_field=FloatField()),
        )

        stock_closing_quantity = stock_quantities.annotate(
          closing_quantity = ExpressionWrapper(F('quantity') + F('total_purchase_quantity_final') - F('total_sales_quantity_final'), output_field=FloatField()),
          grand_total_purchase_quantity = ExpressionWrapper(F('quantity') + F('total_purchase_quantity_final'), output_field=FloatField()),
          grand_total_purchase = ExpressionWrapper(F('purchase_value') + F('opening'), output_field=FloatField()), 
        )

        closing_balance_only_purchase = stock_closing_quantity.annotate(
            purchase_closing_balance = Case(
                When(grand_total_purchase_quantity__gt=0, then=F('grand_total_purchase') / F('grand_total_purchase_quantity')),
                default=0,
                output_field=FloatField()
                )
        )

        closing_balance_final = closing_balance_only_purchase.annotate(
            closing_balance = ExpressionWrapper(F('purchase_closing_balance') * F('closing_quantity'), output_field=FloatField()),
        )

        context['closing_stock'] = closing_balance_final


        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        return context


class StockItemListview(LoginRequiredMixin, ListView):
    """
    Stock Item List View
    """
    context_object_name = 'stock_item_list'
    model = StockItem
    template_name = 'stock_keeping/stock_item/stockdata_list.html'

    def get_queryset(self):
        return self.model.objects.filter(company=self.kwargs['company_pk'])

    def get_context_data(self, **kwargs):
        context = super(StockItemListview, self).get_context_data(**kwargs)
        context['profile_details'] = Profile.objects.all()
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        context['stockdata_list'] = StockItem.objects.filter(
            company=company.pk)
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        return context


class StockItemDetailView(ProductExistsRequiredMixin,  UserPassesTestMixin, LoginRequiredMixin, DetailView):
    """
    Stock Item Details View
    """
    context_object_name = 'stock_item'
    model = StockItem
    template_name = 'stock_keeping/stock_item/stock_item.html'

    def get_object(self):
        return get_object_or_404(StockItem, pk=self.kwargs['stock_item_pk'])

    def test_func(self):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        stock_item = self.get_object()
        return self.request.user in company.auditor.all() or self.request.user in company.accountant.all() or self.request.user == stock_item.user

    def get_context_data(self, **kwargs):
        context = super(StockItemDetailView, self).get_context_data(**kwargs)

        context['profile_details'] = Profile.objects.all()
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
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


class StockItemCreateview(ProductExistsRequiredMixin,  LoginRequiredMixin, CreateView):
    """
    Stock Item Create View
    """
    form_class = StockItemForm
    template_name = "stock_keeping/stock_item/stockdata_form.html"

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        stock_list = StockItem.objects.filter(company=company.pk).order_by('-id')
        for stock in stock_list:
            if stock:
                return reverse('stock_keeping:stockdatadetail', kwargs={'company_pk': company.pk, 'stock_item_pk': stock.pk, 'period_selected_pk': period_selected.pk})

    def form_valid(self, form):
        form.instance.user = self.request.user
        company = Company.objects.get(pk=self.kwargs['company_pk'])
        form.instance.company = company
        counter = StockItem.objects.filter(
            user=self.request.user, company=company).count() + 1
        form.instance.counter = counter
        return super(StockItemCreateview, self).form_valid(form)

    def get_form_kwargs(self):
        data = super(StockItemCreateview, self).get_form_kwargs()
        data.update(
            user=self.request.user,
            company=Company.objects.get(pk=self.kwargs['company_pk'])
        )
        return data

    def get_context_data(self, **kwargs):
        context = super(StockItemCreateview, self).get_context_data(**kwargs)

        context['profile_details'] = Profile.objects.all()
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
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


class StockItemUpdateview(ProductExistsRequiredMixin,  UserPassesTestMixin, LoginRequiredMixin, UpdateView):
    """
    Stock Item Update View
    """
    model = StockItem
    form_class = StockItemForm
    template_name = "stock_keeping/stock_item/stockdata_form.html"

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        stock_item = get_object_or_404(
            StockItem, pk=self.kwargs['stock_item_pk'])
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        return reverse('stock_keeping:stockdatadetail', kwargs={'company_pk': company.pk, 'stock_item_pk': stock_item.pk, 'period_selected_pk': period_selected.pk})

    def get_object(self):
        return get_object_or_404(StockItem, pk=self.kwargs['stock_item_pk'])

    def get_form_kwargs(self):
        data = super(StockItemUpdateview, self).get_form_kwargs()
        data.update(
            user=self.request.user,
            company=Company.objects.get(pk=self.kwargs['company_pk'])
        )
        return data

    def test_func(self):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        stock_item = self.get_object()
        return self.request.user in company.auditor.all() or self.request.user in company.accountant.all() or self.request.user == stock_item.user

    def get_context_data(self, **kwargs):
        context = super(StockItemUpdateview, self).get_context_data(**kwargs)

        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
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


class StockItemDeleteview(ProductExistsRequiredMixin,  UserPassesTestMixin, LoginRequiredMixin, DeleteView):
    """
    Stock Item Delete View
    """
    model = StockItem
    template_name = "stock_keeping/stock_item/stockdataunits_confirm_delete.html"

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        return reverse('stock_keeping:stockdatalist', kwargs={'company_pk': company.pk, 'period_selected_pk': period_selected.pk})

    def get_object(self):
        return get_object_or_404(StockItem, pk=self.kwargs['stock_item_pk'])

    def test_func(self):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        stock_item = self.get_object()
        return self.request.user in company.auditor.all() or self.request.user in company.accountant.all() or self.request.user == stock_item.user

    def get_context_data(self, **kwargs):
        context = super(StockItemDeleteview, self).get_context_data(**kwargs)

        context['profile_details'] = Profile.objects.all()
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
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
