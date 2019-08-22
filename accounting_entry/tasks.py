"""
Tasks
"""
from __future__ import absolute_import, unicode_literals
from celery.decorators import task
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from company.models import Company
from .models import LedgerMaster, JournalVoucher, PeriodSelected


@task()
def update_ledger_balances_task(company_id, ledger_id, period_selected_id):
    """
     Update ledger master opening and closing balance
    """
    company = get_object_or_404(Company, pk=company_id)
    ledger = get_object_or_404(LedgerMaster, pk=ledger_id)
    period_selected = get_object_or_404(PeriodSelected, pk=period_selected_id)

    # opening balance
    if company.gst_enabled:
        dr_total_opening = JournalVoucher.objects.filter(
            company=company,
            dr_ledger=ledger,
            voucher_date__lt=period_selected.start_date
        ).order_by('voucher_date').aggregate(the_sum=Coalesce(Sum('amount'), Value(0)))['the_sum']

        cr_total_opening = JournalVoucher.objects.filter(
            company=company,
            cr_ledger=ledger,
            voucher_date__lt=period_selected.start_date
        ).order_by('voucher_date').aggregate(the_sum=Coalesce(Sum('amount'), Value(0)))['the_sum']
    else:
        dr_total_opening = JournalVoucher.objects.filter(
            company=company,
            dr_ledger=ledger,
            voucher_date__lt=period_selected.start_date
        ).order_by('voucher_date').aggregate(the_sum=Coalesce(Sum('amount'), Value(0)))['the_sum']

        cr_total_opening = JournalVoucher.objects.filter(
            company=company,
            cr_ledger=ledger,
            voucher_date__lt=period_selected.start_date
        ).order_by('voucher_date').aggregate(the_sum=Coalesce(Sum('amount'), Value(0)))['the_sum']

    if ledger.ledger_group.group_base.is_debit == 'Yes':
        opening_balance = ledger.opening_balance + dr_total_opening - cr_total_opening
    else:
        opening_balance = ledger.opening_balance + cr_total_opening - dr_total_opening

    # closing balance
    if company.gst_enabled:
        dr_total_closing = JournalVoucher.objects.filter(
            company=company,
            dr_ledger=ledger,
            voucher_date__gte=period_selected.start_date,
            voucher_date__lte=period_selected.end_date
        ).order_by('voucher_date').aggregate(the_sum=Coalesce(Sum('amount'), Value(0)))['the_sum']

        cr_total_closing = JournalVoucher.objects.filter(
            company=company,
            cr_ledger=ledger,
            voucher_date__gte=period_selected.start_date,
            voucher_date__lte=period_selected.end_date
        ).order_by('voucher_date').aggregate(the_sum=Coalesce(Sum('amount'), Value(0)))['the_sum']

    else:
        dr_total_closing = JournalVoucher.objects.filter(
            company=company,
            dr_ledger=ledger,
            voucher_date__gte=period_selected.start_date,
            voucher_date__lte=period_selected.end_date
        ).order_by('voucher_date').aggregate(the_sum=Coalesce(Sum('amount'), Value(0)))['the_sum']

        cr_total_closing = JournalVoucher.objects.filter(
            company=company,
            cr_ledger=ledger,
            voucher_date__gte=period_selected.start_date,
            voucher_date__lte=period_selected.end_date
        ).order_by('voucher_date').aggregate(the_sum=Coalesce(Sum('amount'), Value(0)))['the_sum']

    if ledger.ledger_group.group_base.is_debit == 'Yes':
        closing_balance = opening_balance + dr_total_closing - cr_total_closing
    else:
        closing_balance = opening_balance + cr_total_closing - dr_total_closing

    LedgerMaster.objects.filter(
        company=company,
        id=ledger.id).update(
            balance_opening=opening_balance,
            closing_balance=closing_balance)

    # ledger.balance_opening = opening_balance
    # ledger.closing_balance = closing_balance
    # ledger.save() #causes recursive signal call
