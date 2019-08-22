"""
Views for Ledger Master
"""
import collections
import calendar
from itertools import zip_longest
import dateutil
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.db.models.functions import Coalesce
from django.db.models import Count, Value, Sum, F
from django.contrib.auth.decorators import login_required
from user_profile.models import Profile
from ecommerce_integration.decorators import product_1_activation
from company.models import Company
from messaging.models import Message
from .resources import LedgerResource
from .mixins import ProductExistsRequiredMixin
from .models import PeriodSelected, Company, LedgerMaster, JournalVoucher
from .forms import LedgerMasterForm, LedgerMasterFormAdmin


class LedgerMasterListView(ProductExistsRequiredMixin, LoginRequiredMixin, ListView):
    """
    Ledger List View
    """
    model = LedgerMaster

    def get_queryset(self):
        return LedgerMaster.objects.filter(company=self.kwargs['company_pk'])#.order_by('ledger_name')

    def get_context_data(self, **kwargs):
        context = super(LedgerMasterListView, self).get_context_data(**kwargs)

        context['profile_details'] = Profile.objects.all()
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        # context['LedgerMasters'] = LedgerMaster.objects.filter(
        #     company=company).order_by('id')
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected

        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        return context


@login_required
@product_1_activation
def ledger_master_detail_view(request, company_pk, ledger_master_pk, period_selected_pk):
    company = get_object_or_404(Company, pk=company_pk)
    ledger_master = get_object_or_404(LedgerMaster, pk=ledger_master_pk)
    period_selected = get_object_or_404(PeriodSelected, pk=period_selected_pk)

    # opening balance for the period
    qs_opening_dr = JournalVoucher.objects.filter(
        company=company,
        dr_ledger=ledger_master,
        voucher_date__lt=period_selected.start_date).order_by('voucher_date')

    qs_opening_cr = JournalVoucher.objects.filter(
        company=company,
        cr_ledger=ledger_master,
        voucher_date__lt=period_selected.start_date).order_by('voucher_date')

    dr_opening_total = qs_opening_dr.aggregate(the_sum=Coalesce(Sum('amount'), Value(0)))['the_sum']
    cr_opening_total = qs_opening_cr.aggregate(the_sum=Coalesce(Sum('amount'), Value(0)))['the_sum']

    if ledger_master.ledger_group.group_base.is_debit == 'Yes':
        opening_balance = ledger_master.opening_balance + \
            dr_opening_total - cr_opening_total
    else:
        opening_balance = ledger_master.opening_balance + \
            cr_opening_total - dr_opening_total

    qs_period_dr = JournalVoucher.objects.filter(
        company=company,
        dr_ledger=ledger_master,
        voucher_date__gte=period_selected.start_date,
        voucher_date__lte=period_selected.end_date).order_by('voucher_date')

    qs_period_cr = JournalVoucher.objects.filter(
        company=company,
        cr_ledger=ledger_master,
        voucher_date__gte=period_selected.start_date,
        voucher_date__lte=period_selected.end_date).order_by('voucher_date')

    journal_list = zip_longest(qs_period_dr, qs_period_cr)

    dr_period_total = qs_period_dr.aggregate(the_sum=Coalesce(Sum('amount'), Value(0)))['the_sum']
    cr_period_total = qs_period_cr.aggregate(the_sum=Coalesce(Sum('amount'), Value(0)))['the_sum']

    if ledger_master.ledger_group.group_base.is_debit == 'Yes':
        closing_balance = opening_balance + dr_period_total - cr_period_total
    else:
        closing_balance = opening_balance + cr_period_total - dr_period_total

    ledger_master = LedgerMaster.objects.get(pk=ledger_master.pk)
    ledger_master.closing_balance = closing_balance
    ledger_master.balance_opening = opening_balance
    ledger_master.save(update_fields=['closing_balance', 'balance_opening'])

    inbox = Message.objects.filter(reciever=request.user)
    inbox_count = inbox.aggregate(
        the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
    send_count = Message.objects.filter(sender=request.user).aggregate(
        the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

    context = {
        'company': company,
        'ledger_master': ledger_master,
        'period_selected': period_selected,
        'total_debit': abs(dr_period_total),
        'total_credit': abs(cr_period_total),
        'journal_debit': qs_period_dr,
        'journal_credit': qs_period_cr,
        'n': journal_list,
        'closing_balance': closing_balance,
        'opening_balance': opening_balance,
        'company_list': Company.objects.all(),
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
        'selectdate': PeriodSelected.objects.filter(user=request.user),
    }

    return render(request, 'accounting_entry/ledger_master.html', context)


class LedgerMasterCreateView(ProductExistsRequiredMixin, LoginRequiredMixin, CreateView):
    """
    Ledger Master Create View
    """
    form_class = LedgerMasterForm
    template_name = "accounting_entry/ledger1_form.html"

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        ledger_list = LedgerMaster.objects.filter(
            company=company).order_by('-id')
        for l in ledger_list:
            return reverse('accounting_entry:ledgerdetail',
                           kwargs={'company_pk': company.pk, 'ledger_master_pk': l.pk, 'period_selected_pk': period_selected.pk})

    def form_valid(self, form):
        form.instance.user = self.request.user
        company = Company.objects.get(pk=self.kwargs['company_pk'])
        form.instance.company = company
        counter = LedgerMaster.objects.filter(
            user=self.request.user, company=company).count() + 1
        form.instance.counter = counter
        return super(LedgerMasterCreateView, self).form_valid(form)

    def get_form_kwargs(self):
        data = super(LedgerMasterCreateView, self).get_form_kwargs()
        data.update(
            user=self.request.user,
            company=Company.objects.get(pk=self.kwargs['company_pk'])
        )
        return data

    def get_context_data(self, **kwargs):
        context = super(LedgerMasterCreateView, self).get_context_data(**kwargs)
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


class LedgerMasterUpdateView(ProductExistsRequiredMixin, UserPassesTestMixin, LoginRequiredMixin, UpdateView):
    '''
    Ledger Master Update View
    '''
    model = LedgerMaster
    form_class = LedgerMasterFormAdmin
    template_name = "accounting_entry/ledger1_form.html"

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        ledger_master = get_object_or_404(LedgerMaster, pk=kwargs['ledger_master_pk'])
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        return reverse('accounting_entry:ledgerdetail',
                       kwargs={'company_pk': company.pk, 'ledger_master_pk': ledger_master.pk, 'period_selected_pk': period_selected.pk})

    def get_object(self):
        return get_object_or_404(LedgerMaster, pk=self.kwargs['ledger_master_pk'])

    def get_form_kwargs(self):
        data = super(LedgerMasterUpdateView, self).get_form_kwargs()
        data.update(
            user=self.request.user,
            company=Company.objects.get(pk=self.kwargs['company_pk'])
        )
        return data

    def test_func(self):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        groups = self.get_object()
        return self.request.user in company.accountant.all() or self.request.user == groups.user

    def get_context_data(self, **kwargs):
        context = super(LedgerMasterUpdateView, self).get_context_data(**kwargs)
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


@login_required
@product_1_activation
def get_ledger_master_excel(request, company_pk):
    """
    Download excel with Ledger Master
    """
    company = get_object_or_404(Company, pk=company_pk)
    ledger_resource = LedgerResource()
    queryset = LedgerMaster.objects.filter(company=company)
    dataset = ledger_resource.export(queryset)
    dataset.title = 'Ledgers'
    response = HttpResponse(
        dataset.xls, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="ledger.xls"'
    return response


@login_required
@product_1_activation
def ledger_monthly_detail_view(request, company_pk, ledger_master_pk, period_selected_pk):
    """
    Monthly Detail View
    """
    company = get_object_or_404(Company, pk=company_pk)
    ledger_master = get_object_or_404(LedgerMaster, pk=ledger_master_pk)
    period_selected = get_object_or_404(PeriodSelected, pk=period_selected_pk)

    # opening balance for the period
    qs_opening_dr = JournalVoucher.objects.filter(
        company=company,
        dr_ledger=ledger_master,
        voucher_date__lt=period_selected.start_date).order_by('voucher_date')

    qs_opening_cr = JournalVoucher.objects.filter(
        company=company,
        cr_ledger=ledger_master,
        voucher_date__lt=period_selected.start_date).order_by('voucher_date')

    dr_opening_total = qs_opening_dr.aggregate(the_sum=Coalesce(Sum('amount'), Value(0)))['the_sum']
    cr_opening_total = qs_opening_cr.aggregate(the_sum=Coalesce(Sum('amount'), Value(0)))['the_sum']

    if ledger_master.ledger_group.group_base.is_debit == 'Yes':
        opening_balance = ledger_master.opening_balance + dr_opening_total - cr_opening_total
    else:
        opening_balance = ledger_master.opening_balance + cr_opening_total - dr_opening_total

    results = collections.OrderedDict()

    qs_period_dr = JournalVoucher.objects.filter(
        company=company,
        dr_ledger=ledger_master,
        voucher_date__gte=period_selected.start_date,
        voucher_date__lte=period_selected.end_date).annotate(
            real_total_debit=F('amount'))

    qs_period_cr = JournalVoucher.objects.filter(
        company=company,
        cr_ledger=ledger_master,
        voucher_date__gte=period_selected.start_date,
        voucher_date__lte=period_selected.end_date).annotate(
            real_total_credit=F('amount'))

    date_cursor = period_selected.start_date

    z = 0
    k = 0

    while date_cursor <= period_selected.end_date:
        month_partial_total_debit = qs_period_dr.filter(
            voucher_date__month=date_cursor.month,
            voucher_date__year=date_cursor.year).aggregate(
                partial_total_debit=Sum('real_total_debit'))['partial_total_debit']

        month_partial_total_credit = qs_period_cr.filter(
            voucher_date__month=date_cursor.month,
            voucher_date__year=date_cursor.year).aggregate(
                partial_total_credit=Sum('real_total_credit'))['partial_total_credit']

        if month_partial_total_debit is None:
            month_partial_total_debit = 0
            e = month_partial_total_debit
        else:
            e = month_partial_total_debit
        if month_partial_total_credit is None:
            month_partial_total_credit = 0
            f = month_partial_total_credit
        else:
            f = month_partial_total_credit

        if ledger_master.ledger_name != 'Profit & Loss A/c':
            if ledger_master.ledger_group.group_base.is_debit == 'Yes':
                z = z + e - f
            else:
                z = z + f - e
        else:
            if ledger_master.ledger_group.group_base.is_debit == 'Yes':
                z = z + e - f
            else:
                z = z + f - e

        k = z + opening_balance

        results[(date_cursor.month, date_cursor.year)] = [e, f, k]

        date_cursor += dateutil.relativedelta.relativedelta(months=1)

    total_debit = qs_period_dr.aggregate(the_sum=Coalesce(Sum('amount'), Value(0)))['the_sum']

    total_credit = qs_period_cr.aggregate(the_sum=Coalesce(Sum('amount'), Value(0)))['the_sum']

    if ledger_master.ledger_group.group_base.is_debit == 'Yes':
        total1 = total_debit - total_credit
    else:
        total1 = total_credit - total_debit

    total = total1 + opening_balance

    inbox = Message.objects.filter(reciever=request.user)
    inbox_count = inbox.aggregate(
        the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
    send_count = Message.objects.filter(sender=request.user).aggregate(
        the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

    context = {
        'company': company,
        'ledger_master': ledger_master,
        'period_selected': period_selected,
        'total_debit': total_debit,
        'total_credit': total_credit,
        'total': total,
        'data': results.items(),
        'opening_balance': opening_balance,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
    }

    return render(request, 'accounting_entry/ledger_monthly.html', context)


def ledger_register_datewise(request, month, year, company_pk, ledger_master_pk, period_selected_pk):
    """
    Ledger Register
    """
    company = get_object_or_404(Company, pk=company_pk)
    period_selected = get_object_or_404(PeriodSelected, pk=period_selected_pk)
    ledger_master = get_object_or_404(LedgerMaster, pk=ledger_master_pk)

    # opening balance
    qs_opening_dr = JournalVoucher.objects.filter(
        company=company,
        dr_ledger=ledger_master,
        voucher_date__lt=period_selected.start_date)

    qs_opening_cr = JournalVoucher.objects.filter(
        company=company,
        cr_ledger=ledger_master,
        voucher_date__lt=period_selected.start_date)

    dr_total = qs_opening_dr.aggregate(
        the_sum=Coalesce(Sum('amount'), Value(0)))['the_sum']

    cr_total = qs_opening_cr.aggregate(
        the_sum=Coalesce(Sum('amount'), Value(0)))['the_sum']

    if ledger_master.ledger_group.group_base.is_debit == 'Yes':
        opening_balance = ledger_master.opening_balance + \
            dr_total - cr_total
    else:
        opening_balance = ledger_master.opening_balance + \
            cr_total - dr_total

    qs_period_dr = JournalVoucher.objects.filter(
        company=company,
        dr_ledger=ledger_master,
        voucher_date__month=month,
        voucher_date__year=year,
        voucher_date__gte=period_selected.start_date,
        voucher_date__lte=period_selected.end_date)

    qs_period_cr = JournalVoucher.objects.filter(
        company=company,
        cr_ledger=ledger_master,
        voucher_date__month=month,
        voucher_date__year=year,
        voucher_date__gte=period_selected.start_date,
        voucher_date__lte=period_selected.end_date)

    journal_list = zip_longest(qs_period_dr, qs_period_cr)

    dr_period_total = qs_period_dr.aggregate(
        the_sum=Coalesce(Sum('amount'), Value(0)))['the_sum']

    cr_period_total = qs_period_cr.aggregate(
        the_sum=Coalesce(Sum('amount'), Value(0)))['the_sum']

    qs = JournalVoucher.objects.filter(
        company=company,
        dr_ledger=ledger_master,
        voucher_date__month__gte=period_selected.start_date.month,
        voucher_date__month__lte=month,
        voucher_date__year__gte=period_selected.start_date.year,
        voucher_date__year__lte=year)

    qs2 = JournalVoucher.objects.filter(
        company=company,
        cr_ledger=ledger_master,
        voucher_date__month__gte=period_selected.start_date.month,
        voucher_date__month__lte=month,
        voucher_date__year__gte=period_selected.start_date.year,
        voucher_date__year__lte=year)

    total_debit = qs.aggregate(the_sum=Coalesce(
        Sum('amount'), Value(0)))['the_sum']

    total_credit = qs2.aggregate(the_sum=Coalesce(
        Sum('amount'), Value(0)))['the_sum']

    if ledger_master.ledger_group.group_base.is_debit == 'Yes':
        closing_balance = opening_balance + total_debit - total_credit
    else:
        closing_balance = opening_balance + total_credit - total_debit

    if ledger_master.ledger_group.group_base.is_debit == 'Yes':
        opening_balancerev = closing_balance - dr_period_total + cr_period_total
    else:
        opening_balancerev = closing_balance - cr_period_total + dr_period_total

    inbox = Message.objects.filter(reciever=request.user)
    inbox_count = inbox.aggregate(
        the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

    send_count = Message.objects.filter(sender=request.user).aggregate(
        the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

    context = {
        'company': company,
        'period_selected': period_selected,
        'ledger_master': ledger_master,
        'journal_list': journal_list,
        'dr_period_total': dr_period_total,
        'cr_period_total': cr_period_total,
        'closing_balance': closing_balance,
        'opening_balance': opening_balancerev,
        'm': calendar.month_name[int(month)],
        'y': year,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
    }

    return render(request, 'accounting_entry/ledger_daily.html', context)


@login_required
@product_1_activation
def ledger_monthly_detail_view_2(request, pk, ledger_master_pk, period_selected_pk):
    """
    Ledger Monthly Detail View
    """
    company = get_object_or_404(Company, pk=pk)
    ledger_master = get_object_or_404(LedgerMaster, pk=ledger_master_pk)
    period_selected = get_object_or_404(PeriodSelected, pk=period_selected_pk)

    # opening balance
    qs_opening_dr = JournalVoucher.objects.filter(
        company=company,
        dr_ledger=ledger_master,
        voucher_date__lt=period_selected.start_date).order_by('voucher_date')
    qs_opening_cr = JournalVoucher.objects.filter(
        company=company,
        cr_ledger=ledger_master,
        voucher_date__lt=period_selected.start_date).order_by('voucher_date')

    dr_total = qs_opening_dr.aggregate(
        the_sum=Coalesce(Sum('amount'), Value(0)))['the_sum']
    cr_total = qs_opening_cr.aggregate(
        the_sum=Coalesce(Sum('amount'), Value(0)))['the_sum']

    if ledger_master.ledger_group.group_base.is_debit == 'Yes':
        opening_balance = ledger_master.opening_balance + dr_total - cr_total
    else:
        opening_balance = ledger_master.opening_balance + cr_total - dr_total

    results = collections.OrderedDict()

    qs_period_dr = JournalVoucher.objects.filter(
        company=company,
        dr_ledger=ledger_master,
        voucher_date__gte=period_selected.start_date,
        voucher_date__lte=period_selected.end_date).annotate(
            real_total_debit=F('amount'))
    qs_period_cr = JournalVoucher.objects.filter(
        company=company,
        cr_ledger=ledger_master,
        voucher_date__gte=period_selected.start_date,
        voucher_date__lte=period_selected.end_date).annotate(
            real_total_credit=F('amount'))

    date_cursor = period_selected.start_date

    z = 0
    k = 0

    while date_cursor <= period_selected.end_date:
        month_partial_total_debit = qs_period_dr.filter(
            voucher_date__month=date_cursor.month,
            voucher_date__year=date_cursor.year).aggregate(
                partial_total_debit=Sum('real_total_debit'))['partial_total_debit']

        month_partial_total_credit = qs_period_cr.filter(
            voucher_date__month=date_cursor.month,
            voucher_date__year=date_cursor.year).aggregate(
                partial_total_credit=Sum('real_total_credit'))['partial_total_credit']

        if month_partial_total_debit is None:
            month_partial_total_debit = 0
            e = month_partial_total_debit
        else:
            e = month_partial_total_debit
        if month_partial_total_credit is None:
            month_partial_total_credit = 0
            f = month_partial_total_credit
        else:
            f = month_partial_total_credit

        if (ledger_master.ledger_name != 'Profit & Loss A/c'):
            if ledger_master.ledger_group.group_base.is_debit == 'Yes':
                z = z + e - f
            else:
                z = z + f - e
        else:
            if ledger_master.ledger_group.group_base.is_debit == 'Yes':
                z = z + e - f
            else:
                z = z + f - e

        k = z + opening_balance

        results[(date_cursor.month, date_cursor.year)] = [e, f, k]

        date_cursor += dateutil.relativedelta.relativedelta(months=1)

    total_debit = qs_period_dr.aggregate(the_sum=Coalesce(Sum('amount'), Value(0)))['the_sum']

    total_credit = qs_period_cr.aggregate(the_sum=Coalesce(Sum('amount'), Value(0)))['the_sum']

    if ledger_master.ledger_group.group_base.is_debit == 'Yes':
        total1 = total_debit - total_credit
    else:
        total1 = total_credit - total_debit

    total = total1 + opening_balance

    inbox = Message.objects.filter(reciever=request.user)
    inbox_count = inbox.aggregate(
        the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
    send_count = Message.objects.filter(sender=request.user).aggregate(
        the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

    context = {
        'company': company,
        'ledger_master': ledger_master,
        'period_selected': period_selected,
        'total_debit': total_debit,
        'total_credit': total_credit,
        'total': total,
        'data': results.items(),
        'opening_balance': opening_balance,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
    }

    return render(request, 'accounting_entry/ledger_monthly_2.html', context)


def ledger_register_datewise_2(request, month, year, comapany_pk, ledger_master_pk, period_selected_pk):
    """
    Ledgr Register Datewise
    """
    company = get_object_or_404(Company, pk=comapany_pk)
    period_selected = get_object_or_404(PeriodSelected, pk=period_selected_pk)
    ledger_master = get_object_or_404(LedgerMaster, pk=ledger_master_pk)

    # opening balance
    qs_opening_dr = JournalVoucher.objects.filter(
        company=company,
        dr_ledger=ledger_master,
        voucher_date__lt=period_selected.start_date)

    qs_opening_cr = JournalVoucher.objects.filter(
        company=company,
        cr_ledger=ledger_master,
        voucher_date__lt=period_selected.start_date)

    dr_total = qs_opening_dr.aggregate(the_sum=Coalesce(Sum('amount'), Value(0)))['the_sum']
    cr_total = qs_opening_cr.aggregate(the_sum=Coalesce(Sum('amount'), Value(0)))['the_sum']

    if ledger_master.ledger_group.group_base.is_debit == 'Yes':
        opening_balance = ledger_master.opening_balance + dr_total - cr_total
    else:
        opening_balance = ledger_master.opening_balance + cr_total - dr_total

    qs_period_dr = JournalVoucher.objects.filter(
        company=company,
        dr_ledger=ledger_master,
        voucher_date__month=month,
        voucher_date__year=year,
        voucher_date__gte=period_selected.start_date,
        voucher_date__lte=period_selected.end_date)

    qs_period_cr = JournalVoucher.objects.filter(
        company=company,
        cr_ledger=ledger_master,
        voucher_date__month=month,
        voucher_date__year=year,
        voucher_date__gte=period_selected.start_date,
        voucher_date__lte=period_selected.end_date)

    journal_list = zip_longest(qs_period_dr, qs_period_cr)

    dr_period_total = qs_period_dr.aggregate(the_sum=Coalesce(Sum('amount'), Value(0)))['the_sum']

    cr_period_total = qs_period_cr.aggregate(the_sum=Coalesce(Sum('amount'), Value(0)))['the_sum']

    qs = JournalVoucher.objects.filter(
        company=company,
        dr_ledger=ledger_master,
        voucher_date__month__gte=period_selected.start_date.month,
        voucher_date__month__lte=month,
        voucher_date__year__gte=period_selected.start_date.year,
        voucher_date__year__lte=year)

    qs2 = JournalVoucher.objects.filter(
        company=company,
        cr_ledger=ledger_master,
        voucher_date__month__gte=period_selected.start_date.month,
        voucher_date__month__lte=month,
        voucher_date__year__gte=period_selected.start_date.year,
        voucher_date__year__lte=year)

    total_debit = qs.aggregate(the_sum=Coalesce(Sum('amount'), Value(0)))['the_sum']
    total_credit = qs2.aggregate(the_sum=Coalesce(Sum('amount'), Value(0)))['the_sum']

    if ledger_master.ledger_group.group_base.is_debit == 'Yes':
        closing_balance = opening_balance + total_debit - total_credit
    else:
        closing_balance = opening_balance + total_credit - total_debit

    if ledger_master.ledger_group.group_base.is_debit == 'Yes':
        opening_balancerev = closing_balance - dr_period_total + cr_period_total
    else:
        opening_balancerev = closing_balance - cr_period_total + dr_period_total

    inbox = Message.objects.filter(reciever=request.user)
    inbox_count = inbox.aggregate(
        the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
    send_count = Message.objects.filter(sender=request.user).aggregate(
        the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

    context = {
        'company': company,
        'period_selected': period_selected,
        'ledger_master': ledger_master,
        'journal_list': journal_list,
        'dr_period_total': dr_period_total,
        'cr_period_total': cr_period_total,
        'closing_balance': closing_balance,
        'opening_balance': opening_balancerev,
        'm': calendar.month_name[int(month)],
        'y': year,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
    }

    return render(request, 'accounting_entry/ledger_daily_2.html', context)
