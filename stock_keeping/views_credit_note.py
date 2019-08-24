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
from .mixins import CompanyAccountsWithInventoryMixin
from .models_credit_note import CreditNoteVoucher, CreditNoteStock, CreditNoteTerm, CreditNoteTax
from .forms_credit_note import CreditNoteForm, CREDIT_NOTE_STOCK_FORM_SET, CREDIT_NOTE_TERM_FORM_SET, CREDIT_NOTE_TAX_FORM_SET


class CreditNoteListview(ProductExistsRequiredMixin,  LoginRequiredMixin, ListView):
    """
    Credit Note List View
    """
    context_object_name = 'credit_list'
    model = CreditNoteVoucher
    template_name = 'stock_keeping/credit_note/credit_note_list.html'
    paginate_by = 15

    def get_queryset(self):
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        return self.model.objects.filter(company=self.kwargs['company_pk'], voucher_date__gte=period_selected.start_date, voucher_date__lte=period_selected.end_date).order_by('-voucher_date')

    def get_context_data(self, **kwargs):
        context = super(CreditNoteListview, self).get_context_data(**kwargs)
        context['profile_details'] = Profile.objects.all()
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        context['credit_list'] = CreditNoteVoucher.objects.filter(
            company=self.kwargs['company_pk']).order_by('-id')
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        return context


class CreditNoteDetailsView(ProductExistsRequiredMixin,  UserPassesTestMixin, LoginRequiredMixin, DetailView):
    """
    Credit Note Details View
    """
    context_object_name = 'debit_details'
    model = CreditNoteVoucher
    template_name = 'stock_keeping/credit_note/credit_note_details.html'

    def get_object(self):
        return get_object_or_404(CreditNoteVoucher, pk=self.kwargs['credit_note_pk'])

    def test_func(self):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        credit_note = self.get_object()
        if self.request.user in company.auditor.all() or self.request.user in company.accountant.all() or self.request.user in company.sale_personel.all() or self.request.user == credit_note.user:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super(CreditNoteDetailsView, self).get_context_data(**kwargs)

        context['profile_details'] = Profile.objects.all()
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        credit_details = get_object_or_404(
            CreditNoteVoucher, pk=self.kwargs['credit_note_pk'])
        qsjb = CreditNoteStock.objects.filter(credit_note=credit_details.pk)
        # saving the closing stock and stocks of particular sales
        for obj in qsjb:
            if obj.stock_item:
                obj.stock_item.save()
        context['stocklist'] = qsjb
        # saving the extra_charges

        context['stock_taxable_credit'] = qsjb.filter(stock_item__taxability='Taxable').aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        context['stock_nongst_credit'] = qsjb.filter(
            Q(stock_item__is_non_gst='Yes') |
            Q(stock_item__taxability='Unknown')).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        context['stock_exempt_credit'] = qsjb.filter(
            Q(stock_item__taxability='Exempt') |
            Q(stock_item__taxability='Nil Rated')).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        extra_charge_credit = CreditNoteTerm.objects.filter(
            credit_note=credit_details.pk)

        for g in extra_charge_credit:
            if g.ledger != None:
                g.save()
                g.ledger.save()

        context['extra_charge_credit_sum'] = extra_charge_credit.aggregate(
            the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']

        context['extra_charge_credit_count'] = extra_charge_credit.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        extra_gst_credit = CreditNoteTax.objects.filter(
            credit_note=credit_details.pk)

        for g in extra_gst_credit:
            g.save()
            g.ledger.save()

        # saving the sales ledger
        credit_details.doc_ledger.save()
        # saving the sales ledger group
        credit_details.doc_ledger.ledger_group.save()
        # saving the party ledger
        credit_details.party_ac.save()
        # saving the party ledger group
        credit_details.party_ac.ledger_group.save()

        extra_gst_credit_central = CreditNoteTax.objects.filter(
            credit_note=credit_details.pk, ledger__tax_type='Central Tax').count()
        # print(extra_gst_credit_central)

        extra_gst_credit_state = CreditNoteTax.objects.filter(
            credit_note=credit_details.pk, ledger__tax_type='State Tax').count()
        # print(extra_gst_credit_state)

        extra_gst_credit_integrated = CreditNoteTax.objects.filter(
            credit_note=credit_details.pk, ledger__tax_type='Integrated Tax').count()
        # print(extra_gst_credit_integrated)

        context['extra_gst_credit_central'] = extra_gst_credit_central
        context['extra_gst_credit_state'] = extra_gst_credit_state
        context['extra_gst_credit_integrated'] = extra_gst_credit_integrated
        context['in_word'] = num2words(credit_details.total, lang='en_IN')
        context['credit_details'] = credit_details
        context['extra_charge_credit'] = extra_charge_credit
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
    template_name = 'stock_keeping/credit_note/credit_note_form.html'

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        credit_list = CreditNoteVoucher.objects.filter(
            company=company.pk)
        for s in credit_list:
            if s:
                return reverse('stock_keeping:creditdetail', kwargs={'company_pk': company.pk, 'credit_note_pk': s.pk, 'period_selected_pk': period_selected.pk})

    def form_valid(self, form):
        form.instance.user = self.request.user
        company = Company.objects.get(pk=self.kwargs['company_pk'])
        form.instance.company = company
        counter = CreditNoteVoucher.objects.filter(company=company).count() + 1
        form.instance.counter = counter
        context = self.get_context_data()
        stockcredit = context['stockcredit']
        with transaction.atomic():
            self.object = form.save()
            if stockcredit.is_valid():
                stockcredit.instance = self.object
                stockcredit.save()
        extra_charges = context['extra_charges']
        with transaction.atomic():
            self.object = form.save()
            if extra_charges.is_valid():
                extra_charges.instance = self.object
                extra_charges.save()
        extra_gst = context['extra_gst']
        with transaction.atomic():
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

        context['profile_details'] = Profile.objects.all()
        company = get_object_or_404(
            Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        if self.request.POST:
            context['stockcredit'] = CREDIT_NOTE_STOCK_FORM_SET(self.request.POST, form_kwargs={
                'company': company.pk})
            context['extra_charges'] = CREDIT_NOTE_TERM_FORM_SET(
                self.request.POST, form_kwargs={'company': company.pk})
            context['extra_gst'] = CREDIT_NOTE_TAX_FORM_SET(
                self.request.POST, form_kwargs={'company': company.pk})
        else:
            context['stockcredit'] = CREDIT_NOTE_STOCK_FORM_SET(
                form_kwargs={'company': company.pk})
            context['extra_charges'] = CREDIT_NOTE_TERM_FORM_SET(
                form_kwargs={'company': company.pk})
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
    model = CreditNoteVoucher
    form_class = CreditNoteForm
    template_name = 'stock_keeping/credit_note/credit_note_form.html'

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        credit_details = get_object_or_404(
            CreditNoteVoucher, pk=self.kwargs['credit_note_pk'])
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        return reverse('stock_keeping:creditdetail', kwargs={'company_pk': company.pk, 'credit_note_pk': credit_details.pk, 'period_selected_pk': period_selected.pk})

    def get_object(self):
        return get_object_or_404(CreditNoteVoucher, pk=self.kwargs['credit_note_pk'])

    def test_func(self):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        sales_return = self.get_object()
        if self.request.user in company.accountant.all() or self.request.user in company.sale_personel.all() or self.request.user == sales_return.user:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super(CreditNoteUpdateView, self).get_context_data(**kwargs)
        credit_details = get_object_or_404(
            CreditNoteVoucher, pk=self.kwargs['credit_note_pk'])
        sales_return_particular = CreditNoteVoucher.objects.get(
            pk=credit_details.pk)
        context['profile_details'] = Profile.objects.all()
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        if self.request.POST:
            context['stockcredit'] = CREDIT_NOTE_STOCK_FORM_SET(
                self.request.POST, instance=sales_return_particular, form_kwargs={'company': company.pk})
            context['extra_charges'] = CREDIT_NOTE_TERM_FORM_SET(
                self.request.POST, instance=sales_return_particular, form_kwargs={'company': company.pk})
            context['extra_gst'] = CREDIT_NOTE_TAX_FORM_SET(
                self.request.POST, instance=sales_return_particular, form_kwargs={'company': company.pk})
        else:
            context['stockcredit'] = CREDIT_NOTE_STOCK_FORM_SET(
                instance=sales_return_particular, form_kwargs={'company': company.pk})
            context['extra_charges'] = CREDIT_NOTE_TERM_FORM_SET(
                instance=sales_return_particular, form_kwargs={'company': company.pk})
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
        stockcredit = context['stockcredit']
        if stockcredit.is_valid():
            stockcredit.save()
        extra_charges = context['extra_charges']
        if extra_charges.is_valid():
            extra_charges.save()
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
    model = CreditNoteVoucher
    template_name = 'stock_keeping/credit_note/credit_note_delete.html'

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        return reverse('stock_keeping:creditlist', kwargs={'company_pk': company.pk, 'period_selected_pk': period_selected.pk})

    def get_object(self):
        return get_object_or_404(CreditNoteVoucher, pk=self.kwargs['credit_note_pk'])

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
