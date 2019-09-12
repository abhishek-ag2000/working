"""
Views for Credit Note
"""
from num2words import num2words
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.db.models import Value, Sum, Count, Q
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse
from company.models import Company
from user_profile.models import Profile
from messaging.models import Message

from accounting_entry.models import PeriodSelected
from accounting_entry.mixins import ProductExistsRequiredMixin
from .model_credit_note_accounts import CreditNoteAccountsVoucher, CreditNoteAccountsTerm, CreditNoteAccountTax
from .form_credit_note_accounts import CreditNoteForm, CREDIT_NOTE_TERM_FORM_SET, CREDIT_NOTE_TAX_FORM_SET


class CreditNoteDetailsView(ProductExistsRequiredMixin,  UserPassesTestMixin, LoginRequiredMixin, DetailView):
    """
    Credit Note Details View
    """
    context_object_name = 'debit_details'
    model = CreditNoteAccountsVoucher
    template_name = 'credit_note/credit_note_details.html'

    def get_object(self):
        return get_object_or_404(CreditNoteAccountsVoucher, pk=self.kwargs['credit_note_pk'])

    def test_func(self):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        credit_note = self.get_object()
        if self.request.user in company.auditor.all() or self.request.user in company.accountant.all() or self.request.user in company.sale_personel.all() or self.request.user == credit_note.user:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super(CreditNoteDetailsView, self).get_context_data(**kwargs)

        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        credit_details = get_object_or_404(
            CreditNoteAccountsVoucher, pk=self.kwargs['credit_note_pk'])

        extra_charge_credit = CreditNoteAccountsTerm.objects.filter(
            credit_note=credit_details.pk)

        for g in extra_charge_credit:
            if g.ledger != None:
                g.save()
                g.ledger.save()
                credit_details.save()

        context['extra_charge_credit_sum'] = extra_charge_credit.aggregate(
            the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']

        context['extra_charge_credit_count'] = extra_charge_credit.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        extra_gst_credit = CreditNoteAccountTax.objects.filter(
            credit_note=credit_details.pk)

        for g in extra_gst_credit:
            g.save()
            g.ledger.save()

        extra_gst_credit_central = CreditNoteAccountTax.objects.filter(
            credit_note=credit_details.pk, ledger__tax_type='Central Tax').count()
        # print(extra_gst_credit_central)

        extra_gst_credit_state = CreditNoteAccountTax.objects.filter(
            credit_note=credit_details.pk, ledger__tax_type='State Tax').count()
        # print(extra_gst_credit_state)

        extra_gst_credit_integrated = CreditNoteAccountTax.objects.filter(
            credit_note=credit_details.pk, ledger__tax_type='Integrated Tax').count()
        # print(extra_gst_credit_integrated)

        tax_total = credit_details.credit_note_gst_accounts.aggregate(
        the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']
        extra_total = credit_details.credit_note_term_accounts.aggregate(
            the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']

        if tax_total or extra_total:
            total = tax_total + extra_total

        credit_details.total = total
        credit_details.save()

        context['extra_gst_credit_central'] = extra_gst_credit_central
        context['extra_gst_credit_state'] = extra_gst_credit_state
        context['extra_gst_credit_integrated'] = extra_gst_credit_integrated
        context['in_word'] = num2words(credit_details.total, lang='en_IN')
        context['credit_details'] = credit_details
        context['extra_charge_credit'] = extra_charge_credit
        context['total'] = total
        context['extra_gst_credit'] = extra_gst_credit
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        return context


class CreditNoteCreateView(ProductExistsRequiredMixin,  LoginRequiredMixin, CreateView):
    """
    Credit Note Create View
    """
    form_class = CreditNoteForm
    template_name = 'credit_note/credit_note_form.html'

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        credit_list = CreditNoteAccountsVoucher.objects.filter(
            company=company.pk)
        for s in credit_list:
            if s:
                return reverse('accounts_mode_voucher:creditdetail', kwargs={'company_pk': company.pk, 'credit_note_pk': s.pk, 'period_selected_pk': period_selected.pk})

    def form_valid(self, form):
        form.instance.user = self.request.user
        company = Company.objects.get(pk=self.kwargs['company_pk'])
        form.instance.company = company
        counter = CreditNoteAccountsVoucher.objects.filter(company=company).count() + 1
        form.instance.counter = counter
        context = self.get_context_data()
        extra_charges = context['extra_charges']

        if not extra_charges.is_valid():
            # formset for stock item is invalid; render the form with error
            return self.render_to_response(context)

        with transaction.atomic():
            self.object = form.save()
            extra_charges.instance = self.object
            extra_charges.save()

            if c.gst_enabled == 'Yes':
                extra_gst = context['extra_gst']
                self.object = form.save()
                if extra_gst.is_valid():
                    extra_gst.instance = self.object
                    extra_gst.save()
        return super(CreditNoteCreateView, self).form_valid(form)

    def get_form_kwargs(self):
        data = super(CreditNoteCreateView, self).get_form_kwargs()
        data.update(
            company=Company.objects.get(pk=self.kwargs['company_pk']),
        )
        return data

    def get_context_data(self, **kwargs):
        context = super(CreditNoteCreateView, self).get_context_data(**kwargs)

        company = get_object_or_404(
            Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        if self.request.POST:
            context['extra_charges'] = CREDIT_NOTE_TERM_FORM_SET(
                self.request.POST, form_kwargs={'company': company.pk})
            if company.gst_enabled == 'Yes':
                context['extra_gst'] = CREDIT_NOTE_TAX_FORM_SET(
                    self.request.POST, form_kwargs={'company': company.pk})
        else:
            context['extra_charges'] = CREDIT_NOTE_TERM_FORM_SET(
                form_kwargs={'company': company.pk})
            if company.gst_enabled == 'Yes':
                context['extra_gst'] = CREDIT_NOTE_TAX_FORM_SET(
                    form_kwargs={'company': company.pk})
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        return context


class CreditNoteUpdateView(ProductExistsRequiredMixin,  UserPassesTestMixin, LoginRequiredMixin, UpdateView):
    """
    Credit Note Update View
    """
    model = CreditNoteAccountsVoucher
    form_class = CreditNoteForm
    template_name = 'credit_note/credit_note_form.html'

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        credit_details = get_object_or_404(
            CreditNoteAccountsVoucher, pk=self.kwargs['credit_note_pk'])
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        return reverse('accounts_mode_voucher:creditdetail', kwargs={'company_pk': company.pk, 'credit_note_pk': credit_details.pk, 'period_selected_pk': period_selected.pk})

    def get_object(self):
        return get_object_or_404(CreditNoteAccountsVoucher, pk=self.kwargs['credit_note_pk'])

    def test_func(self):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        sales_return = self.get_object()
        if self.request.user in company.accountant.all() or self.request.user in company.sale_personel.all() or self.request.user == sales_return.user:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super(CreditNoteUpdateView, self).get_context_data(**kwargs)
        credit_details = get_object_or_404(
            CreditNoteAccountsVoucher, pk=self.kwargs['credit_note_pk'])
        sales_return_particular = CreditNoteAccountsVoucher.objects.get(
            pk=credit_details.pk)
        context['profile_details'] = Profile.objects.all()
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        if self.request.POST:
            context['extra_charges'] = CREDIT_NOTE_TERM_FORM_SET(
                self.request.POST, instance=sales_return_particular, form_kwargs={'company': company.pk})
            if company.gst_enabled == 'Yes':
                context['extra_gst'] = CREDIT_NOTE_TAX_FORM_SET(
                    self.request.POST, instance=sales_return_particular, form_kwargs={'company': company.pk})
        else:
            context['extra_charges'] = CREDIT_NOTE_TERM_FORM_SET(
                instance=sales_return_particular, form_kwargs={'company': company.pk})
            if company.gst_enabled == 'Yes':
                context['extra_gst'] = CREDIT_NOTE_TAX_FORM_SET(
                    instance=sales_return_particular, form_kwargs={'company': company.pk})
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

        extra_charges = context['extra_charges']
        
        if not extra_charges.is_valid():
            # formset for stock item is invalid; render the form with error
            return self.render_to_response(context)

        with transaction.atomic():
            extra_charges.save()
            if c.gst_enabled == 'Yes':
                extra_gst = context['extra_gst']
                if extra_gst.is_valid():
                    extra_gst.save()
        return super(CreditNoteUpdateView, self).form_valid(form)

    def get_form_kwargs(self):
        data = super(CreditNoteUpdateView, self).get_form_kwargs()
        data.update(
            company=Company.objects.get(pk=self.kwargs['company_pk'])
        )
        return data


class CreditNoteDeleteView(ProductExistsRequiredMixin,  UserPassesTestMixin, LoginRequiredMixin, DeleteView):
    """
    Credit Note Delete View
    """
    model = CreditNoteAccountsVoucher
    template_name = 'credit_note/credit_note_delete.html'

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        return reverse('stock_keeping:creditlist', kwargs={'company_pk': company.pk, 'period_selected_pk': period_selected.pk})

    def get_object(self):
        return get_object_or_404(CreditNoteAccountsVoucher, pk=self.kwargs['credit_note_pk'])

    def test_func(self):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        sales_return = self.get_object()
        if self.request.user in company.accountant.all() or self.request.user in company.sale_personel.all() or self.request.user == sales_return.user:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super(CreditNoteDeleteView, self).get_context_data(**kwargs)
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
