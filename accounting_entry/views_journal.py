"""
Accounting Double Entry (Views for Journal Voucher and Journal related operations)
"""
from decimal import Decimal
import collections
import calendar
import dateutil
import pandas as pd
import numpy as np
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.db.models.functions import Coalesce
from django.db.models import Count, Value, F, Sum
from django.db import transaction
from django.contrib.auth.decorators import login_required
from ecommerce_integration.decorators import product_1_activation
from company.models import Company
from messaging.models import Message
from user_profile.models import Profile
from .mixins import ProductExistsRequiredMixin
from .models import PeriodSelected, LedgerMaster, JournalVoucher, MultiJournalVoucher, MultiJournalVoucherDrRows
from .forms import JournalVoucherForm, MultiJournalVoucherForm, MULTI_JOURNAL_DR_FORM_SET
from .resources import JournalResource


class JournalVoucherListView(ProductExistsRequiredMixin, LoginRequiredMixin, ListView):
    """
    Journal Voucher List View
    """
    model = JournalVoucher
    template_name = "accounting_entry/journal_list.html"
    paginate_by = 15

    def get_queryset(self):
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])

        return JournalVoucher.objects.filter(
            company=self.kwargs['company_pk'],
            voucher_date__gte=period_selected.start_date,
            voucher_date__lte=period_selected.end_date).order_by('-id')

    def get_context_data(self, **kwargs):
        context = super(JournalVoucherListView, self).get_context_data(**kwargs)

        context['profile_details'] = Profile.objects.all()
        context['company'] = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['period_selected'] = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        return context


class JournalVoucherCreateView(ProductExistsRequiredMixin, LoginRequiredMixin, CreateView):
    """
    Journal Create View
    """
    model = JournalVoucher
    form_class = JournalVoucherForm
    template_name = "accounting_entry/journal_form.html"

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        journal_list = JournalVoucher.objects.filter(company=company).order_by('-id')
        for j in journal_list:
            return reverse('accounting_entry:detail', kwargs={'company_pk': company.pk, 'journal_voucher_pk': j.pk, 'period_selected_pk': period_selected.pk})

    def form_valid(self, form):
        form.instance.user = self.request.user
        company = Company.objects.get(pk=self.kwargs['company_pk'])
        form.instance.company = company
        counter = JournalVoucher.objects.filter(
            user=self.request.user, company=company).count() + 1
        form.instance.counter = counter

        return super(JournalVoucherCreateView, self).form_valid(form)

    def get_form_kwargs(self):
        data = super(JournalVoucherCreateView, self).get_form_kwargs()
        data.update(
            user=self.request.user,
            company=Company.objects.get(pk=self.kwargs['company_pk'])
        )
        return data

    def get_context_data(self, **kwargs):
        context = super(JournalVoucherCreateView, self).get_context_data(**kwargs)

        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        return context


class JournalVoucherUpdateView(ProductExistsRequiredMixin, UserPassesTestMixin, LoginRequiredMixin, UpdateView):
    """
    Journal Update View
    """
    model = JournalVoucher
    form_class = JournalVoucherForm
    template_name = "accounting_entry/journal_form.html"

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        journal_voucher = get_object_or_404(JournalVoucher, pk=self.kwargs['journal_voucher_pk'])
        
        return reverse(
            'accounting_entry:detail',
            kwargs={'company_pk': company.pk,
                    'journal_voucher_pk': journal_voucher.pk,
                    'period_selected_pk': period_selected.pk})

    def get_object(self):
        journal_voucher = self.kwargs['journal_voucher_pk']
        return get_object_or_404(JournalVoucher, pk=journal_voucher)

    def get_form_kwargs(self):
        data = super(JournalVoucherUpdateView, self).get_form_kwargs()
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
        context = super(JournalVoucherUpdateView, self).get_context_data(**kwargs)

        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        return context


class JournalRegisterView(ProductExistsRequiredMixin, LoginRequiredMixin, ListView):
    """
    Journal Register List View
    """
    model = JournalVoucher
    template_name = 'accounting_entry/Journal_register.html'

    def get_context_data(self, **kwargs):
        context = super(JournalRegisterView, self).get_context_data(**kwargs)

        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['company'] = company
        context['period_selected'] = period_selected

        results = collections.OrderedDict()
        result = JournalVoucher.objects.filter(
            company=company,
            voucher_type='Journal',
            voucher_date__gte=period_selected.start_date,
            voucher_date__lt=period_selected.end_date).annotate(
                real_total=F('amount'))

        date_cursor = period_selected.start_date

        while date_cursor <= period_selected.end_date:
            month_partial_total = result.filter(voucher_date__month=date_cursor.month, voucher_date__year=date_cursor.year).aggregate(
                partial_total=Count('real_total'))['partial_total']

            if month_partial_total is None:
                month_partial_total = 0

            results[(date_cursor.month, date_cursor.year)] = month_partial_total
            date_cursor += dateutil.relativedelta.relativedelta(months=1)

        total_voucher = result.aggregate(the_sum=Coalesce(Count('real_total'), Value(0)))['the_sum']

        total = total_voucher

        context['data'] = results.items()
        context['total'] = total
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        return context


class MultiJournalListView(ProductExistsRequiredMixin, UserPassesTestMixin, LoginRequiredMixin, ListView):
    """
    Multi Journal List View
    """
    model = MultiJournalVoucher
    template_name = 'MultiJournalVoucherRows/multi_journal_list.html'
    paginate_by = 15

    def get_queryset(self):
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        return self.model.objects.filter(
            company=self.kwargs['company_pk'],
            voucher_date__gte=period_selected.start_date,
            voucher_date__lte=period_selected.end_date).order_by('-id')

    def test_func(self):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        multi_journals = MultiJournalVoucher.objects.filter(
            company=self.kwargs['company_pk'], voucher_date__gte=period_selected.start_date, voucher_date__lte=period_selected.end_date)
        for obj in multi_journals:
            return self.request.user in company.auditor.all() or \
                self.request.user in company.accountant.all() or \
                self.request.user == obj.user
        return False

    def get_context_data(self, **kwargs):
        context = super(MultiJournalListView, self).get_context_data(**kwargs)

        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        return context


class MultiJournalCreateView(ProductExistsRequiredMixin, LoginRequiredMixin, CreateView):
    """
    Multi Journal Create View
    """
    form_class = MultiJournalVoucherForm
    template_name = 'MultiJournalVoucherRows/multi_journal_form.html'

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])

        return reverse('accounting_entry:multijournallist', kwargs={'company_pk': company.pk, 'period_selected_pk': period_selected.pk})

    def get_context_data(self, **kwargs):
        context = super(MultiJournalCreateView, self).get_context_data(**kwargs)
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected

        if self.request.POST:
            context['multi_journal_dr_formset'] = MULTI_JOURNAL_DR_FORM_SET(
                self.request.POST, form_kwargs={'company_pk': company.pk})
        else:
            context['multi_journal_dr_formset'] = MULTI_JOURNAL_DR_FORM_SET(
                form_kwargs={'company_pk': company.pk})

        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        company = Company.objects.get(pk=self.kwargs['company_pk'])
        form.instance.company = company
        context = self.get_context_data()
        multi_journal_dr_formset = context['multi_journal_dr_formset']
        with transaction.atomic():
            self.object = form.save()
            if multi_journal_dr_formset.is_valid():
                multi_journal_dr_formset.instance = self.object
                multi_journal_dr_formset.save()
        return super(MultiJournalCreateView, self).form_valid(form)

    def get_form_kwargs(self):
        data = super(MultiJournalCreateView, self).get_form_kwargs()
        data.update(
            company=Company.objects.get(pk=self.kwargs['company_pk'])
        )
        return data


class MultiJournalUpdateView(ProductExistsRequiredMixin, UserPassesTestMixin, LoginRequiredMixin, UpdateView):
    """
    Multi Journal Update View
    """
    model = MultiJournalVoucher
    form_class = MultiJournalVoucherForm
    template_name = 'MultiJournalVoucherRows/multi_journal_form.html'

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        multi_journal = get_object_or_404(MultiJournalVoucher, pk=kwargs['multi_journal_voucher_pk'])
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        return reverse('accounting_entry:multijournaldetail',
                       kwargs={'company_pk': company.pk, 'multi_journal_voucher_pk': multi_journal.pk, 'period_selected_pk': period_selected.pk})

    def get_object(self):
        journal_voucher = self.kwargs['multi_journal_voucher_pk']
        multijournaltotal = get_object_or_404(MultiJournalVoucher, pk=journal_voucher)
        return multijournaltotal

    def test_func(self):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        multi_journal = self.get_object()
        return self.request.user in company.accountant.all() or self.request.user == multi_journal.User

    def get_context_data(self, **kwargs):
        context = super(MultiJournalUpdateView, self).get_context_data(**kwargs)
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        multi_journal = get_object_or_404(
            MultiJournalVoucher, pk=self.kwargs['multi_journal_voucher_pk'])
        total = MultiJournalVoucher.objects.get(pk=multi_journal.pk)
        if self.request.POST:
            context['multi_journal_dr_formset'] = MULTI_JOURNAL_DR_FORM_SET(
                self.request.POST, instance=total, form_kwargs={'company_pk': company.pk})
        else:
            context['multi_journal_dr_formset'] = MULTI_JOURNAL_DR_FORM_SET(
                instance=total, form_kwargs={'company_pk': company.pk})

        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        comapny = Company.objects.get(pk=self.kwargs['company_pk'])
        form.instance.company = comapny
        context = self.get_context_data()
        multi_journal_dr_formset = context['multi_journal_dr_formset']
        with transaction.atomic():
            self.object = form.save()
            if multi_journal_dr_formset.is_valid():
                multi_journal_dr_formset.instance = self.object
                multi_journal_dr_formset.save()
        return super(MultiJournalUpdateView, self).form_valid(form)


class MultiJournalDeleteView(ProductExistsRequiredMixin, UserPassesTestMixin, LoginRequiredMixin, DeleteView):
    """
    Multi Journal Delete View
    """
    model = MultiJournalVoucher
    template_name = 'MultiJournalVoucherRows/multijournal_delete.html'

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        return reverse('accounting_entry:multijournallist',
                       kwargs={'company_pk': company.pk, 'period_selected_pk': period_selected.pk})

    def get_object(self):
        company_pk = self.kwargs['company_pk']
        journal_voucher = self.kwargs['journal_voucher_pk']
        get_object_or_404(Company, pk=company_pk)
        multijournal = get_object_or_404(MultiJournalVoucher, pk=journal_voucher)
        return multijournal

    def test_func(self):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        groups = self.get_object()
        if self.request.user in company.accountant.all() or self.request.user == groups.User:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super(MultiJournalDeleteView,
                        self).get_context_data(**kwargs)
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        multi_journal = get_object_or_404(
            MultiJournalVoucher, pk=self.kwargs['journal_voucher_pk'])
        context['multi_journal'] = multi_journal
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        return context


class MultiJournalRowCreateView(ProductExistsRequiredMixin, LoginRequiredMixin, CreateView):
    """
    Multi Journal Create View
    """
    form_class = MultiJournalVoucherDrRows
    template_name = 'MultiJournalVoucherRows/multi_journal_form.html'

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        return reverse('accounting_entry:multijournallist', kwargs={'company_pk': company.pk, 'period_selected_pk': period_selected.pk})

    def get_form_kwargs(self):
        data = super(MultiJournalRowCreateView, self).get_form_kwargs()
        data.update(
            user=self.request.user,
            company=Company.objects.get(pk=self.kwargs['company_pk'])
        )
        return data

    def get_context_data(self, **kwargs):
        context = super(MultiJournalRowCreateView, self).get_context_data(**kwargs)
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
def journal_voucher_detail_view(request, company_pk, journal_voucher_pk, period_selected_pk):
    """
    Journal Details View
    """
    company = get_object_or_404(Company, pk=company_pk)
    journal_voucher = get_object_or_404(JournalVoucher, pk=journal_voucher_pk)
    period_selected = get_object_or_404(PeriodSelected, pk=period_selected_pk)

    journal_voucher.dr_ledger.save()
    journal_voucher.cr_ledger.save()

    inbox = Message.objects.filter(reciever=request.user)
    inbox_count = inbox.aggregate(
        the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
    send_count = Message.objects.filter(sender=request.user).aggregate(
        the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

    context = {
        'journal_voucher': journal_voucher,
        'company': company,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
        'period_selected': period_selected,
    }
    return render(request, 'accounting_entry/journal_details.html', context)


@login_required
@product_1_activation
def journal_register_view(request, month, company_pk, period_selected_pk):
    """
    Journal Register Datewise
    """
    company = get_object_or_404(Company, pk=company_pk)
    period_selected = get_object_or_404(PeriodSelected, pk=period_selected_pk)

    result = JournalVoucher.objects.filter(
        company=company,
        voucher_type='Journal',
        voucher_date__month=month,
        voucher_date__gte=period_selected.start_date,
        voucher_date__lt=period_selected.end_date)

    total = result.aggregate(partial_total=Sum('amount'))['partial_total']

    inbox = Message.objects.filter(reciever=request.user)
    inbox_count = inbox.aggregate(
        the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
    send_count = Message.objects.filter(sender=request.user).aggregate(
        the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

    context = {
        'company': company,
        'period_selected': period_selected,
        'result': result,
        'm': calendar.month_name[int(month)],
        'total': total,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
    }

    return render(request, 'accounting_entry/journal_datewise.html', context)


@product_1_activation
def multi_journal_deail_view(request, company_pk, multi_journal_voucher_pk, period_selected_pk):
    """
    Multi Journal Detail View
    """
    company = get_object_or_404(Company, pk=company_pk)
    multi_journal = get_object_or_404(MultiJournalVoucher, pk=multi_journal_voucher_pk)
    period_selected = get_object_or_404(PeriodSelected, pk=period_selected_pk)
    multi_journal_dr_rows = MultiJournalVoucherDrRows.objects.filter(multi_journal=multi_journal)
    multi_journal_cr_rows = MultiJournalVoucherDrRows.objects.filter(multi_journal=multi_journal)

    inbox = Message.objects.filter(reciever=request.user)
    inbox_count = inbox.aggregate(
        the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
    send_count = Message.objects.filter(sender=request.user).aggregate(
        the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

    context = {
        'multi_journal': multi_journal,
        'multi_journal_dr_rows': multi_journal_dr_rows,
        'multi_journal_cr_rows': multi_journal_cr_rows,
        'company': company,
        'period_selected': period_selected,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
    }
    return render(request, 'MultiJournalVoucherRows/multi_journal_details.html', context)


def journal_export_view(request, company_pk, period_selected_pk):
    """
    Journal Export
    """
    company = get_object_or_404(Company, pk=company_pk)
    period_selected = get_object_or_404(PeriodSelected, pk=period_selected_pk)
    journal_resource = JournalResource()
    queryset = JournalVoucher.objects.filter(
        company=company,
        voucher_date__gte=period_selected.start_date,
        voucher_date__lt=period_selected.end_date)
    dataset = journal_resource.export(queryset)
    # modification to find name of ledger and its group name in dataset final
    response = HttpResponse(
        dataset.xls, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="JournalVoucher.xls"'
    return response


def journal_import_view(request, company_pk, period_selected_pk):
    """
    Journal Upload
    """
    company = get_object_or_404(Company, pk=company_pk)
    period_selected = get_object_or_404(PeriodSelected, pk=period_selected_pk)
    error_message = "Some of the ledgers and Groups does not match with the ledgers of your Company"
    form_error = False

    if request.method == 'POST':
        #journal_resource = JournalResource()
        #dataset = Dataset()
        new_journal = request.FILES['myfile']
        data = pd.ExcelFile(new_journal)
        dfex = pd.read_excel(data, 'Tablib Dataset')
        dfnew = dfex[['Date', 'By', 'By__LedgerGroup_Name__group_Name',
                      'To', 'To__LedgerGroup_Name__group_Name', 'Debit', 'Credit']]

        for i in range(0, len(dfnew)):
            debit = Decimal(np.sum(dfnew.iloc[i]['Debit']).item())
            credit = Decimal(np.sum(dfnew.iloc[i]['Credit']).item())

            if LedgerMaster.objects.filter(
                company=company,
                name__iexact=dfnew.iloc[i]['By'],
                LedgerGroup_Name__group_Name__iexact=dfnew.iloc[i]['By__LedgerGroup_Name__group_Name']).exists() and LedgerMaster.objects.filter(
                    company=company,
                    name__iexact=dfnew.iloc[i]['To'],
                    LedgerGroup_Name__group_Name__iexact=dfnew.iloc[i]['To__LedgerGroup_Name__group_Name']).exists():
                JournalVoucher.objects.create(
                    User=request.user,
                    company=company,
                    Date=dfnew.iloc[i]['Date'],
                    By=LedgerMaster.objects.filter(
                        name__iexact=dfnew.iloc[i]['By']).first(),
                    To=LedgerMaster.objects.filter(
                            name__iexact=dfnew.iloc[i]['To']).first(),
                    Debit=debit,
                    Credit=credit)
            else:
                form_error = True

    inbox = Message.objects.filter(reciever=request.user)
    inbox_count = inbox.aggregate(
        the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
    send_count = Message.objects.filter(sender=request.user).aggregate(
        the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

    context = {
        'company': company,
        'period_selected': period_selected,
        'error_message': error_message,
        'inbox': inbox,
        'form_error': form_error,
        'inbox_count': inbox_count,
        'send_count': send_count,
    }

    return render(request, 'accounting_entry/import_journal.html', context)
