"""
Views for Daybook / Cash/Bank Statements
"""
from django.shortcuts import get_object_or_404, render
from django.db.models.functions import Coalesce
from django.db.models import Count, Value, Sum, OuterRef, Subquery, FloatField, Case, When, F
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from company.models import Company
from messaging.models import Message
from ecommerce_integration.decorators import product_1_activation
from .mixins import ProductExistsRequiredMixin
from .models import PeriodSelected, LedgerGroup, LedgerMaster, JournalVoucher


class DayBookListView(ProductExistsRequiredMixin, LoginRequiredMixin, ListView):
    """
    Day Book List View
    """
    context_object_name = 'journal_list'
    model = JournalVoucher
    paginate_by = 15

    def get_template_names(self):
        return ['Daybook/daybook.html']

    def get_queryset(self):
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])

        return JournalVoucher.objects.filter(
            company=self.kwargs['company_pk'],
            voucher_date__gte=period_selected.start_date,
            voucher_date__lte=period_selected.end_date).order_by('-id')

    def get_context_data(self, **kwargs):
        context = super(DayBookListView, self).get_context_data(**kwargs)
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


@login_required
@product_1_activation
def cash_and_bank_view(request, company_pk, period_selected_pk):
    company = get_object_or_404(Company, pk=company_pk)
    period_selected = get_object_or_404(PeriodSelected, pk=period_selected_pk)

    # Journal queries to get the debit and credit balances of all ledgers
    Journal_debit = JournalVoucher.objects.filter(company=company, dr_ledger=OuterRef(
    'pk'), voucher_date__gte=period_selected.start_date, voucher_date__lte=period_selected.end_date).values('dr_ledger')

    Journal_credit = JournalVoucher.objects.filter(company=company, cr_ledger=OuterRef(
    'pk'), voucher_date__gte=period_selected.start_date, voucher_date__lte=period_selected.end_date).values('cr_ledger')

    Journal_debit_opening = JournalVoucher.objects.filter(company=company, dr_ledger=OuterRef(
    'pk'), voucher_date__lt=period_selected.start_date).values('dr_ledger')

    Journal_credit_opening = JournalVoucher.objects.filter(company=company, cr_ledger=OuterRef(
    'pk'), voucher_date__lt=period_selected.start_date).values('cr_ledger')

    
    total_debit = Journal_debit.annotate(
    total=Coalesce(Sum('amount'), Value(0))).values('total')

    total_credit = Journal_credit.annotate(
    total=Coalesce(Sum('amount'), Value(0))).values('total')

    total_debit_opening = Journal_debit_opening.annotate(
    total=Coalesce(Sum('amount'), Value(0))).values('total')

    total_credit_opening = Journal_credit_opening.annotate(
    total=Coalesce(Sum('amount'), Value(0))).values('total')

    ledgers = LedgerMaster.objects.filter(company=company).annotate(
        debit_balance_opening = Coalesce(Subquery(total_debit_opening,output_field=FloatField()), Value(0)),
        credit_balance_opening = Coalesce(Subquery(total_credit_opening,output_field=FloatField()), Value(0)),
        debit_balance = Coalesce(Subquery(total_debit,output_field=FloatField()), Value(0)),
        credit_balance = Coalesce(Subquery(total_credit,output_field=FloatField()), Value(0))
    )

    ledger_list = ledgers.annotate(
        opening_balance_generated = Case(
            When(ledger_group__group_base__is_debit='Yes', then=F('opening_balance') + F('debit_balance_opening') - F('credit_balance_opening')),
            When(ledger_group__group_base__is_debit='No', then=F('opening_balance') + F('credit_balance_opening') - F('debit_balance_opening')),
            default=None,
            output_field=FloatField()
            ),
    )

    
    ledger_final_list = ledger_list.annotate(
        closing_balance_generated = Case(
            When(ledger_group__group_base__is_debit='Yes', then=F('opening_balance_generated') + F('debit_balance') - F('credit_balance')),
            When(ledger_group__group_base__is_debit='No', then=F('opening_balance_generated') + F('credit_balance') - F('debit_balance')),
            default=None,
            output_field=FloatField()
            ),
    )

    total_cash_positive = ledger_final_list.filter(ledger_group__group_base__name__contains='Cash-in-Hand',closing_balance_generated__gte=0).aggregate(
            the_sum=Coalesce(Sum('closing_balance_generated'), Value(0)))['the_sum']

    total_cash_negative = ledger_final_list.filter(ledger_group__group_base__name__contains='Cash-in-Hand',closing_balance_generated__lt=0).aggregate(
            the_sum=Coalesce(Sum('closing_balance_generated'), Value(0)))['the_sum']


    total_bank_positive = ledger_final_list.filter(ledger_group__group_base__name__contains='Bank Accounts',closing_balance_generated__gte=0).aggregate(
            the_sum=Coalesce(Sum('closing_balance_generated'), Value(0)))['the_sum']

    total_bank_negative = ledger_final_list.filter(ledger_group__group_base__name__contains='Bank Accounts',closing_balance_generated__lt=0).aggregate(
            the_sum=Coalesce(Sum('closing_balance_generated'), Value(0)))['the_sum']

    total_positive = total_cash_positive + total_bank_positive

    total_negative = abs(total_cash_negative) + abs(total_bank_negative)


    inbox = Message.objects.filter(reciever=request.user)
    inbox_count = inbox.aggregate(
        the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
    send_count = Message.objects.filter(sender=request.user).aggregate(
        the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

    context = {
        'company': company,
        'period_selected': period_selected,

        'total_cash_positive' : total_cash_positive,
        'total_cash_negative' : total_cash_negative,
        'total_bank_positive' : total_bank_positive,
        'total_bank_negative' : total_bank_negative,

        'total_positive' : round(total_positive, 2),
        'total_negative' : round(total_negative, 2),

        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count
    }

    return render(request, 'Cash_Bank/cash_and_bank.html', context)
