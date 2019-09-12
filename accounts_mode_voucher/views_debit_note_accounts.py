"""
Views for Debit Note
"""
import datetime
from num2words import num2words
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.db.models import Value, Sum, Count
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse
from company.models import Company
from user_profile.models import Profile
from messaging.models import Message

from accounting_entry.models import PeriodSelected
from accounting_entry.mixins import ProductExistsRequiredMixin
from .models_debit_note import DebitNoteAccountsVoucher, DebitNoteAccountsTerm, DebitNoteTax
from .form_debit_note import DebitNoteForm, DEBIT_NOTE_TERM_FORM_SET, DEBIT_NOTE_TAX_FORM_SET


class DebitNoteAccountsDetailsView(ProductExistsRequiredMixin,  UserPassesTestMixin, LoginRequiredMixin, DetailView):
    """
    Debit Note Accounts Only Details View
    """
    context_object_name = 'debit_details'
    model = DebitNoteAccountsVoucher
    template_name = 'debit_note/debit_note_details.html'

    def get_object(self):
        return get_object_or_404(DebitNoteAccountsVoucher, pk=self.kwargs['debit_note_pk'])

    def test_func(self):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        debits = self.get_object()
        if self.request.user in company.auditor.all() or self.request.user in company.accountant.all() or self.request.user in company.sale_personel.all() or self.request.user == debits.user:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super(DebitNoteAccountsDetailsView, self).get_context_data(**kwargs)
        context['profile_details'] = Profile.objects.all()
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        debits_details = get_object_or_404(
            DebitNoteAccountsVoucher, pk=self.kwargs['debit_note_pk'])

        # saving the extra_charges
        extra_charge_debit = DebitNoteAccountsTerm.objects.filter(
            debit_note=debits_details.pk)
        for g in extra_charge_debit:
            g.save()
            g.ledger.save()
            debits_details.save()

        context['extra_charge_debit_sum'] = extra_charge_debit.aggregate(
            the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']

        extra_gst_debit = DebitNoteTax.objects.filter(
            debit_note=debits_details.pk)
        for g in extra_gst_debit:
            if g.ledger != None:
                g.save()
                g.ledger.save()

        gst_total = debits_details.debit_note_gst_accounts.aggregate(
            the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']
        extra_total = debits_details.debit_note_extra_accounts.aggregate(
            the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']
        if gst_total or extra_total:
            total = gst_total + extra_total

        debits_details.total = total
        debits_details.save()

        extra_gst_debit_central = DebitNoteTax.objects.filter(
            debit_note=debits_details.pk, ledger__tax_type='Central Tax').count()

        extra_gst_debit_state = DebitNoteTax.objects.filter(
            debit_note=debits_details.pk, ledger__tax_type='State Tax').count()

        extra_gst_debit_integrated = DebitNoteTax.objects.filter(
            debit_note=debits_details.pk, ledger__tax_type='Integrated Tax').count()

        context['extra_gst_debit_central'] = extra_gst_debit_central
        context['extra_gst_debit_state'] = extra_gst_debit_state
        context['extra_gst_debit_integrated'] = extra_gst_debit_integrated
        context['in_word'] = num2words(debits_details.total, lang='en_IN')
        context['debits_details'] = debits_details
        context['total'] = total
        context['extra_charge_debit'] = extra_charge_debit
        context['extra_gst_debit'] = extra_gst_debit
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        return context


class DebitNoteCreateview(ProductExistsRequiredMixin,  LoginRequiredMixin, CreateView):
    """
    Debit Note Create View
    """
    form_class = DebitNoteForm
    template_name = 'debit_note/debit_note_form.html'

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        debit_list = DebitNoteAccountsVoucher.objects.filter(
            company=company.pk).order_by('-id')
        for debit_note in debit_list:
            if debit_note:
                return reverse('accounts_mode_voucher:debitdetail', kwargs={'company_pk': company.pk, 'debit_note_pk': debit_note.pk, 'period_selected_pk': period_selected.pk})

    def form_valid(self, form):
        form.instance.user = self.request.user
        company = Company.objects.get(pk=self.kwargs['company_pk'])
        form.instance.company = company
        counter = DebitNoteAccountsVoucher.objects.filter(company=company).count() + 1
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
        return super(DebitNoteCreateview, self).form_valid(form)

    def get_form_kwargs(self):
        data = super(DebitNoteCreateview, self).get_form_kwargs()
        data.update(
            company=Company.objects.get(pk=self.kwargs['company_pk']),
        )
        return data

    def get_context_data(self, **kwargs):
        context = super(DebitNoteCreateview, self).get_context_data(**kwargs)
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        if self.request.POST:
            context['extra_charges'] = DEBIT_NOTE_TERM_FORM_SET(
                self.request.POST, form_kwargs={'company': company.pk})
            if company.gst_enabled == 'Yes':
                context['extra_gst'] = DEBIT_NOTE_TAX_FORM_SET(
                    self.request.POST, form_kwargs={'company': company.pk})
        else:
            context['extra_charges'] = DEBIT_NOTE_TERM_FORM_SET(
                form_kwargs={'company': company.pk})
            if company.gst_enabled == 'Yes':
                context['extra_gst'] = DEBIT_NOTE_TAX_FORM_SET(
                    form_kwargs={'company': company.pk})
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        return context


class DebitNoteUpdateView(ProductExistsRequiredMixin,  UserPassesTestMixin, LoginRequiredMixin, UpdateView):
    """
    Debit Note Update View
    """
    model = DebitNoteAccountsVoucher
    form_class = DebitNoteForm
    template_name = 'debit_note/debit_note_form.html'

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        debit_details = get_object_or_404(
            DebitNoteAccountsVoucher, pk=self.kwargs['debit_note_pk'])
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        return reverse('accounts_mode_voucher:debitdetail', kwargs={'company_pk': company.pk, 'debit_note_pk': debit_details.pk, 'period_selected_pk': period_selected.pk})

    def get_object(self):
        return get_object_or_404(DebitNoteAccountsVoucher, pk=self.kwargs['debit_note_pk'])

    def test_func(self):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        sales = self.get_object()
        if self.request.user in company.accountant.all() or self.request.user in company.sale_personel.all() or self.request.user == sales.user:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super(DebitNoteUpdateView, self).get_context_data(**kwargs)
        debit_details = get_object_or_404(
            DebitNoteAccountsVoucher, pk=self.kwargs['debit_note_pk'])
        sales_particular = DebitNoteAccountsVoucher.objects.get(pk=debit_details.pk)
        context['profile_details'] = Profile.objects.all()
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        if self.request.POST:
            context['extra_charges'] = DEBIT_NOTE_TERM_FORM_SET(
                self.request.POST, instance=sales_particular, form_kwargs={'company': company.pk})
            if company.gst_enabled == 'Yes':
                context['extra_gst'] = DEBIT_NOTE_TAX_FORM_SET(
                    self.request.POST, instance=sales_particular, form_kwargs={'company': company.pk})
        else:
            context['extra_charges'] = DEBIT_NOTE_TERM_FORM_SET(
                instance=sales_particular, form_kwargs={'company': company.pk})
            if company.gst_enabled == 'Yes':
                context['extra_gst'] = DEBIT_NOTE_TAX_FORM_SET(
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
        return super(DebitNoteUpdateView, self).form_valid(form)

    def get_form_kwargs(self):
        data = super(DebitNoteUpdateView, self).get_form_kwargs()
        data.update(
            company=Company.objects.get(pk=self.kwargs['company_pk'])
        )
        return data


class DebitNoteDeleteView(ProductExistsRequiredMixin,  UserPassesTestMixin, LoginRequiredMixin, DeleteView):
    """
    Debit Note Delete View
    """
    model = DebitNoteAccountsVoucher
    template_name = "debit_note/debit_note_delete.html"

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        return reverse('accounts_mode_voucher:debitlist', kwargs={'company_pk': company.pk, 'period_selected_pk': period_selected.pk})

    def get_object(self):
        return get_object_or_404(DebitNoteAccountsVoucher, pk=self.kwargs['debit_note_pk'])

    def test_func(self):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        sales = self.get_object()
        if self.request.user in company.accountant.all() or self.request.user in company.sale_personel.all() or self.request.user == sales.user:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super(DebitNoteDeleteView, self).get_context_data(**kwargs)
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
