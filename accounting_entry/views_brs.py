"""
Views for Bank Reconciliation
"""
from itertools import zip_longest
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.db.models.functions import Coalesce
from django.db.models import Count, Value, Sum, Q
from django.contrib.auth.decorators import login_required
from ecommerce_integration.decorators import product_1_activation
from company.models import Company
from messaging.models import Message
from user_profile.models import Profile
from .mixins import ProductExistsRequiredMixin
from .models import PeriodSelected, LedgerMaster, BankReconciliation


class BankLedgerListView(ProductExistsRequiredMixin, LoginRequiredMixin, ListView):
    """
    Bank Ledger List View
    """
    model = LedgerMaster
    template_name = 'Bank/bank_ledger_list.html'

    def get_queryset(self):
        return LedgerMaster.objects.filter(
            Q(company=self.kwargs['company_pk']),
            Q(ledger_group__group_base__name__exact='Bank Accounts') | Q(ledger_group__group_base__name__exact='Bank OD A/c'))

    def get_context_data(self, **kwargs):
        context = super(BankLedgerListView, self).get_context_data(**kwargs)

        context['company'] = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['period_selected'] = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['profile_details'] = Profile.objects.all()
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        return context


@login_required
@product_1_activation
def bank_ledger_details_view(request, company_pk, ledger_master_pk, period_selected_pk):
    company = get_object_or_404(Company, pk=company_pk)
    ledger_master = get_object_or_404(LedgerMaster, pk=ledger_master_pk)
    period_selected = get_object_or_404(PeriodSelected, pk=period_selected_pk)

    # opening balance
    opening_total_dr = BankReconciliation.objects.filter(
        company=company,
        dr_ledger=ledger_master,
        voucher_date__lt=period_selected.start_date).aggregate(the_sum=Coalesce(Sum('amount'), Value(0)))['the_sum']

    opening_total_cr = BankReconciliation.objects.filter(
        company=company,
        cr_ledger=ledger_master,
        voucher_date__lt=period_selected.start_date).aggregate(the_sum=Coalesce(Sum('amount'), Value(0)))['the_sum']

    if ledger_master.ledger_group.group_base.is_debit == 'Yes':
        opening_balance = ledger_master.opening_balance + \
            opening_total_dr - opening_total_cr
    else:
        opening_balance = ledger_master.opening_balance + \
            opening_total_cr - opening_total_dr

    # brs for opening balance calculation
    opeing_unreconciled_total_dr = BankReconciliation.objects.filter(
        company=company,
        dr_ledger=ledger_master,
        bank_date=None,
        voucher_date__lt=period_selected.start_date).order_by('voucher_date').aggregate(the_sum=Coalesce(Sum('amount'), Value(0)))['the_sum']

    opeing_unreconciled_total_cr = BankReconciliation.objects.filter(
        company=company,
        cr_ledger=ledger_master,
        bank_date=None,
        voucher_date__lt=period_selected.start_date).order_by('voucher_date').aggregate(the_sum=Coalesce(Sum('amount'), Value(0)))['the_sum']

    per_bank_balance_1 = opening_balance - \
        opeing_unreconciled_total_cr - opeing_unreconciled_total_dr

    # closing balance
    closing_period_total_cr = BankReconciliation.objects.filter(
        company=company,
        cr_ledger=ledger_master,
        voucher_date__gte=period_selected.start_date,
        voucher_date__lt=period_selected.end_date).order_by('voucher_date')

    closing_period_total_dr = BankReconciliation.objects.filter(
        company=company,
        dr_ledger=ledger_master,
        voucher_date__gte=period_selected.start_date,
        voucher_date__lt=period_selected.end_date).order_by('voucher_date')

    ziped_open_close = zip_longest(closing_period_total_cr, closing_period_total_dr)

    total_debitcb = closing_period_total_cr.aggregate(the_sum=Coalesce(Sum('amount'), Value(0)))['the_sum']
    total_creditcb = closing_period_total_dr.aggregate(the_sum=Coalesce(Sum('amount'), Value(0)))['the_sum']

    if ledger_master.ledger_group.group_base.is_debit == 'Yes':
        closing_balance = opening_balance + total_creditcb - total_debitcb
    else:
        closing_balance = opening_balance + total_debitcb - total_creditcb

    # per bank balance

    # per_bank_balance = closing_balance - (total_creditcb - total_debitcb)

    qscb_bank_not_reconciled = BankReconciliation.objects.filter(
        company=company,
        dr_ledger=ledger_master,
        bank_date=None,
        voucher_date__gte=period_selected.start_date,
        voucher_date__lt=period_selected.end_date).order_by('voucher_date')

    qscb2_bank_not_reconciled = BankReconciliation.objects.filter(
        company=company,
        cr_ledger=ledger_master,
        bank_date=None,
        voucher_date__gte=period_selected.start_date,
        voucher_date__lt=period_selected.end_date).order_by('voucher_date')

    total_debit_not_reconciled = qscb_bank_not_reconciled.aggregate(the_sum=Coalesce(Sum('amount'), Value(0)))['the_sum']

    total_credit_not_reconciled = qscb2_bank_not_reconciled.aggregate(the_sum=Coalesce(Sum('amount'), Value(0)))['the_sum']

    qscb_bank = BankReconciliation.objects.filter(
        company=company,
        dr_ledger=ledger_master,
        voucher_date__gte=period_selected.start_date,
        voucher_date__lt=period_selected.end_date).exclude(bank_date=None).order_by('voucher_date')

    qscb2_bank = BankReconciliation.objects.filter(
        company=company,
        cr_ledger=ledger_master,
        voucher_date__gte=period_selected.start_date,
        voucher_date__lt=period_selected.end_date).exclude(bank_date=None).order_by('voucher_date')

    total_debit = qscb_bank.aggregate(the_sum=Coalesce(Sum('amount'), Value(0)))['the_sum']
    total_credit = qscb2_bank.aggregate(the_sum=Coalesce(Sum('amount'), Value(0)))['the_sum']

    per_bank_balance = opening_balance - (total_credit - total_debit)

    # LedgerMaster_detail = LedgerMaster.objects.get(pk=ledger_master)
    # LedgerMaster_detail.Closing_balance = closing_balance
    # LedgerMaster_detail.Balance_opening = opening_balance
    # LedgerMaster_detail.save(update_fields=['Closing_balance', 'Balance_opening'])

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
        'total_debit_opening': opeing_unreconciled_total_dr,
        'total_credit_opening': opeing_unreconciled_total_cr,
        'per_bank_balance_opening': per_bank_balance_1,
        'per_bank_balance': per_bank_balance,
        'journal_debit': closing_period_total_cr,
        'journal_credit': closing_period_total_dr,
        'total_debit_not_reconciled': total_debit_not_reconciled,
        'total_credit_not_reconciled': total_credit_not_reconciled,
        'n': ziped_open_close,
        'closing_balance': closing_balance,
        'opening_balance': opening_balance,
        'company_list': Company.objects.all(),
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
        'selectdate': PeriodSelected.objects.filter(user=request.user)
    }

    return render(request, 'Bank/bank_ledger_details.html', context)


@login_required
@product_1_activation
def bank_journal_detail(request, company_pk, bank_reconciliation_pk, period_selected_pk):
    company = get_object_or_404(Company, pk=company_pk)
    journal_details = get_object_or_404(BankReconciliation, pk=bank_reconciliation_pk)
    period_selected = get_object_or_404(PeriodSelected, pk=period_selected_pk)

    inbox = Message.objects.filter(reciever=request.user)
    inbox_count = inbox.aggregate(
        the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
    send_count = Message.objects.filter(sender=request.user).aggregate(
        the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

    context = {
        'journal_details': journal_details,
        'company': company,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
        'period_selected': period_selected,
    }

    return render(request, 'Bank/bank_details.html', context)
