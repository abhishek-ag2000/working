"""
Views for Daybook / Cash/Bank Statements
"""
from django.shortcuts import get_object_or_404, render
from django.db.models.functions import Coalesce
from django.db.models import Count, Value, Sum
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from company.models import Company
from messaging.models import Message
from ecommerce_integration.decorators import product_1_activation
from user_profile.models import Profile
from .mixins import ProductExistsRequiredMixin
from .models import PeriodSelected, LedgerGroup, JournalVoucher


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

        context['profile_details'] = Profile.objects.all()
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

    # Cash Account
    cash_group = LedgerGroup.objects.filter(
        company=company, group_base__name__exact='Cash-in-Hand')

    cash_group_closing = cash_group.annotate(
        closing=Coalesce(Sum('group_ledger__closing_balance'), 0),  # reverse lookup
    )

    groups_ca_pos = cash_group.annotate(
        closing=Coalesce(Sum('group_ledger__closing_balance'), 0)
    ).filter(closing__gt=0)

    groups_ca_neg = cash_group.annotate(
        closing=Coalesce(Sum('group_ledger__closing_balance'), 0)
    ).filter(closing__lte=0)

    groups_ca_positive = groups_ca_pos.aggregate(
        the_sum=Coalesce(Sum('closing'), Value(0)))['the_sum']

    groups_ca_negative = groups_ca_neg.aggregate(
        the_sum=Coalesce(Sum('closing'), Value(0)))['the_sum']

    # Bank Account
    bank_group = LedgerGroup.objects.filter(
        company=company, group_base__name__exact='Bank Accounts')
    bank_group_closing = bank_group.annotate(
        closing=Coalesce(Sum('group_ledger__closing_balance'), 0),
    )

    groups_ba_pos = bank_group.annotate(
        closing=Coalesce(Sum('group_ledger__closing_balance'), 0),
    ).filter(closing__gt=0)

    groups_ba_positive = groups_ba_pos.aggregate(
        the_sum=Coalesce(Sum('closing'), Value(0)))['the_sum']

    positive = groups_ca_positive + groups_ba_positive
    negative = groups_ca_negative

    inbox = Message.objects.filter(reciever=request.user)
    inbox_count = inbox.aggregate(
        the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
    send_count = Message.objects.filter(sender=request.user).aggregate(
        the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

    context = {
        'company': company,
        'period_selected': period_selected,

        'cash_group': cash_group_closing,

        'bank_group': bank_group_closing,

        'positive': positive,
        'negative': negative,

        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count
    }

    return render(request, 'Cash_Bank/cash_and_bank.html', context)
