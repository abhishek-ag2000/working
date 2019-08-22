"""
Views for Ledger Group
"""
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse
from django.shortcuts import get_object_or_404, render
from django.db.models.functions import Coalesce
from django.db.models import Count, Value, Sum
from django.contrib.auth.decorators import login_required
from ecommerce_integration.decorators import product_1_activation
from company.models import Company
from messaging.models import Message
from .mixins import ProductExistsRequiredMixin
from .models import PeriodSelected, Company, LedgerGroup
from .forms import LedgerGroupForm


class LedgerGroupSummaryListView(ProductExistsRequiredMixin, UserPassesTestMixin, LoginRequiredMixin, ListView):
    """
    Ledger Group Summary List View
    """
    model = LedgerGroup
    paginate_by = 15

    def get_template_names(self):
        return ['Group_Summary/group_summary.html']

    def get_queryset(self):
        return self.model.objects.filter(company=self.kwargs['company_pk'])

    def test_func(self):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        ledger_group = LedgerGroup.objects.filter(company=company)

        for obj in ledger_group:
            return self.request.user in company.auditor.all() or \
                self.request.user in company.accountant.all() or \
                self.request.user == obj.user
        return False

    def get_context_data(self, **kwargs):
        context = super(LedgerGroupSummaryListView, self).get_context_data(**kwargs)

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


class LedgerGroupListView(ProductExistsRequiredMixin, UserPassesTestMixin, LoginRequiredMixin, ListView):
    """
    Ledger Group List View
    """
    model = LedgerGroup
    template_name = "accounting_entry/group1_list.html"
    paginate_by = 15

    def get_queryset(self):
        return self.model.objects.filter(company=self.kwargs['company_pk']).order_by('group_name')

    def test_func(self):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        ledger_group = LedgerGroup.objects.filter(company=company)
        for obj in ledger_group:
            return self.request.user in company.auditor.all() or \
                self.request.user in company.accountant.all() or \
                self.request.user == obj.user
        return False

    def get_context_data(self, **kwargs):
        context = super(LedgerGroupListView, self).get_context_data(**kwargs)

        context['company'] = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['period_selected'] = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        return context


class LedgerGroupDetailView(ProductExistsRequiredMixin, UserPassesTestMixin, LoginRequiredMixin, DetailView):
    """
    Ledger Group Detail View
    """
    context_object_name = 'ledger_group'
    model = LedgerGroup
    template_name = 'accounting_entry/ledger_group.html'

    def get_object(self):
        get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        get_object_or_404(Company, pk=self.kwargs['company_pk'])
        ledger_group = get_object_or_404(LedgerGroup, pk=self.kwargs['ledger_group_pk'])
        return ledger_group

    def test_func(self):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        ledger_group = self.get_object()
        return self.request.user in company.auditor.all() or \
            self.request.user in company.accountant.all() or \
            self.request.user == ledger_group.user

    def get_context_data(self, **kwargs):
        context = super(LedgerGroupDetailView, self).get_context_data(**kwargs)

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


class LedgerGroupCreateView(ProductExistsRequiredMixin, LoginRequiredMixin, CreateView):
    """
    Ledger Group Create View
    """
    form_class = LedgerGroupForm
    template_name = "accounting_entry/group1_form.html"

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        return reverse('accounting_entry:grouplist', kwargs={'company_pk': company.pk, 'period_selected_pk': period_selected.pk})

    def form_valid(self, form):
        form.instance.user = self.request.user
        company = Company.objects.get(pk=self.kwargs['company_pk'])
        form.instance.company = company
        counter = LedgerGroup.objects.filter(user=self.request.user, company=company).count() + 1
        form.instance.counter = counter
        return super(LedgerGroupCreateView, self).form_valid(form)

    def get_form_kwargs(self):
        data = super(LedgerGroupCreateView, self).get_form_kwargs()
        data.update(
            user=self.request.user,
            company=Company.objects.get(pk=self.kwargs['company_pk'])
        )
        return data

    def get_context_data(self, **kwargs):
        context = super(LedgerGroupCreateView, self).get_context_data(**kwargs)

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


class LedgerGroupUpdateView(ProductExistsRequiredMixin, UserPassesTestMixin, LoginRequiredMixin, UpdateView):
    """
    Ledger Group Update View
    """
    model = LedgerGroup
    form_class = LedgerGroupForm
    template_name = "accounting_entry/group1_form.html"

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        ledger_group = get_object_or_404(LedgerGroup, pk=self.kwargs['ledger_group_pk'])
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        return reverse('accounting_entry:groupdetail', kwargs={'company_pk': company.pk, 'ledger_group_pk': ledger_group.pk, 'period_selected_pk': period_selected.pk})

    def get_object(self):
        return get_object_or_404(LedgerGroup, pk=self.kwargs['ledger_group_pk'])

    def get_form_kwargs(self):
        data = super(LedgerGroupUpdateView, self).get_form_kwargs()

        data.update(
            user=self.request.user,
            company=Company.objects.get(pk=self.kwargs['company_pk'])
        )
        return data

    def test_func(self):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        ledger_group = self.get_object()
        return self.request.user in company.accountant.all() or self.request.user == ledger_group.user

    def get_context_data(self, **kwargs):
        context = super(LedgerGroupUpdateView, self).get_context_data(**kwargs)

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
def ledger_group_detail_view(request, company_pk, ledger_group_pk, period_selected_pk):
    """
    Group Details View
    """
    company = get_object_or_404(Company, pk=company_pk)
    ledger_group = get_object_or_404(LedgerGroup, pk=ledger_group_pk)
    period_selected = get_object_or_404(PeriodSelected, pk=period_selected_pk)

    # purchases
    gs_purchase = LedgerGroup.objects.filter(
        company=company, group_base__name__exact="Purchase Accounts")
    gs_purchase_total = gs_purchase.aggregate(the_sum=Coalesce(
        Sum('group_ledger__closing_balance'), Value(0)))['the_sum']

    # sales
    gs_sales = LedgerGroup.objects.filter(
        company=company, group_base__name__exact="Sales Accounts")
    gs_sales_total = gs_sales.aggregate(the_sum=Coalesce(
        Sum('group_ledger__closing_balance'), Value(0)))['the_sum']

    # Direct Expense
    gs_directexp = LedgerGroup.objects.filter(
        company=company, group_base__name__exact="Direct Expenses")
    gs_directexp_total = gs_directexp.aggregate(the_sum=Coalesce(
        Sum('group_ledger__closing_balance'), Value(0)))['the_sum']

    # Direct Income
    gs_directinc = LedgerGroup.objects.filter(
        company=company, group_base__name__exact="Direct Incomes")
    gs_directinc_total = gs_directinc.aggregate(the_sum=Coalesce(
        Sum('group_ledger__closing_balance'), Value(0)))['the_sum']

    # Indirect Expense
    gs_indirectexp = LedgerGroup.objects.filter(
        company=company, group_base__name__exact="Indirect Expenses")
    gs_indirectexp_total = gs_indirectexp.aggregate(the_sum=Coalesce(
        Sum('group_ledger__closing_balance'), Value(0)))['the_sum']

    # Indirect Income
    gs_indirectinc = LedgerGroup.objects.filter(
        company=company, group_base__name__exact="Indirect Incomes")
    gs_indirectinc_total = gs_indirectinc.aggregate(the_sum=Coalesce(
        Sum('group_ledger__closing_balance'), Value(0)))['the_sum']

    inbox = Message.objects.filter(reciever=request.user)
    inbox_count = inbox.aggregate(
        the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
    send_count = Message.objects.filter(sender=request.user).aggregate(
        the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

    context = {
        'company': company,
        'ledger_group': ledger_group,
        'period_selected': period_selected,
        'gs_purchase': gs_purchase,
        'gs_purchase_total': gs_purchase_total,
        'gs_sales': gs_sales,
        'gs_sales_total': gs_sales_total,
        'gs_directexp': gs_directexp,
        'gs_directexp_total': gs_directexp_total,
        'gs_directinc': gs_directinc,
        'gs_directinc_total': gs_directinc_total,
        'gs_indirectinc': gs_indirectinc,
        'gs_indirectinc_total': gs_indirectinc_total,
        'gs_indirectexp': gs_indirectexp,
        'gs_indirectexp_total': gs_indirectexp_total,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count
    }

    return render(request, 'Group_Summary/group_summary_details.html', context)
