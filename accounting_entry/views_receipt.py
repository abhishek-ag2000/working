"""
Views for ReceiptVoucher Voucher
"""
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.db.models.functions import Coalesce
from django.db.models import Count, Value
from django.db import transaction

from company.models import Company
from messaging.models import Message
from user_profile.models import Profile
from .mixins import ProductExistsRequiredMixin
from .models import PeriodSelected, ReceiptVoucher, ReceiptVoucherRows
from .forms import ReceiptVoucherForm, RECEIPT_FORM_SET


class ReceiptVoucherListView(ProductExistsRequiredMixin, LoginRequiredMixin, ListView):
    """
    Receipt Voucher List View
    """
    model = ReceiptVoucher
    template_name = 'Receipt/receipt_list.html'
    paginate_by = 15

    def get_queryset(self):
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])

        return self.model.objects.filter(
            company=self.kwargs['company_pk'],
            voucher_date__gte=period_selected.start_date,
            voucher_date__lte=period_selected.end_date).order_by('-id')

    def get_context_data(self, **kwargs):
        context = super(ReceiptVoucherListView, self).get_context_data(**kwargs)

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


class ReceiptVoucherDetailView(ProductExistsRequiredMixin, UserPassesTestMixin, LoginRequiredMixin, DetailView):
    """
    Receipt Voucher Detail View
    """
    context_object_name = 'receipt_voucher'
    model = ReceiptVoucher
    template_name = 'Receipt/receipt_details.html'

    def get_object(self):
        return get_object_or_404(ReceiptVoucher, pk=self.kwargs['receipt_voucher_pk'])

    def test_func(self):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        receipt_voucher = self.get_object()
        return self.request.user in company.auditor.all() or \
            self.request.user in company.accountant.all() or \
            self.request.user in company.cb_personal.all() or \
            self.request.user == receipt_voucher.user

    def get_context_data(self, **kwargs):
        context = super(ReceiptVoucherDetailView, self).get_context_data(**kwargs)

        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        # receipt_voucher = get_object_or_404(ReceiptVoucher, pk=self.kwargs['receipt_voucher_pk'])
        # context['receipt_voucher'] = receipt_voucher
        # receipt_voucher.account.save()
        # receipt_ac = ReceiptVoucherRows.objects.filter(receipt=receipt_voucher)
        # for obj in receipt_ac:
        #     obj.save()
        #     obj.particular.save()
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        return context

class ReceiptVoucherCreateView(ProductExistsRequiredMixin, LoginRequiredMixin, CreateView):
    """
    Receipt Voucher Create View
    """
    form_class = ReceiptVoucherForm
    success_message = "%(account)s is submitted successfully"
    template_name = 'Receipt/receipt_form.html'

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        receipt = ReceiptVoucher.objects.filter(
            company=company,
            voucher_date__gte=period_selected.start_date,
            voucher_date__lte=period_selected.end_date).order_by('-id')
        for voucher in receipt:
            return reverse('accounting_entry:receiptdetail', kwargs={'company_pk': company.pk, 'receipt_voucher_pk': voucher.pk, 'period_selected_pk': period_selected.pk})

    def get_context_data(self, **kwargs):
        context = super(ReceiptVoucherCreateView, self).get_context_data(**kwargs)

        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        if self.request.POST:
            context['receipts'] = RECEIPT_FORM_SET(self.request.POST, form_kwargs={'company': company})
        else:
            context['receipts'] = RECEIPT_FORM_SET(form_kwargs={'company': company})

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
        counter = ReceiptVoucher.objects.filter(
            user=self.request.user, company=company).count() + 1
        form.instance.counter = counter
        context = self.get_context_data()
        receipts = context['receipts']
        
        if form.is_valid() and receipts.is_valid():
            with transaction.atomic():
                self.object = form.save()
                receipts.instance = self.object
                receipts.save()

        return super(ReceiptVoucherCreateView, self).form_valid(form)

    def get_form_kwargs(self):
        data = super(ReceiptVoucherCreateView, self).get_form_kwargs()
        data.update(
            user=self.request.user,
            company=Company.objects.get(pk=self.kwargs['company_pk'])
        )
        return data


class ReceiptVoucherUpdateView(ProductExistsRequiredMixin, UserPassesTestMixin, LoginRequiredMixin, UpdateView):
    """
    Receipt Voucher Update View
    """
    model = ReceiptVoucher
    form_class = ReceiptVoucherForm
    template_name = 'Receipt/receipt_form.html'

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        receipt_voucher = get_object_or_404(ReceiptVoucher, pk=self.kwargs['receipt_voucher_pk'])
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        
        return reverse('accounting_entry:receiptdetail', kwargs={'company_pk': company.pk, 'receipt_voucher_pk': receipt_voucher.pk, 'period_selected_pk': period_selected.pk})

    def get_object(self):
        return get_object_or_404(ReceiptVoucher, pk=self.kwargs['receipt_voucher_pk'])

    def test_func(self):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        receipt_voucher = self.get_object()
        return self.request.user in company.accountant.all() or \
            self.request.user in company.cb_personal.all() or \
            self.request.user == receipt_voucher.user

    def get_context_data(self, **kwargs):
        context = super(ReceiptVoucherUpdateView, self).get_context_data(**kwargs)

        receipt_voucher = get_object_or_404(ReceiptVoucher, pk=self.kwargs['receipt_voucher_pk'])
        receipt_voucher = ReceiptVoucher.objects.get(pk=receipt_voucher.pk)
        context['profile_details'] = Profile.objects.all()
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        if self.request.POST:
            context['receipts'] = RECEIPT_FORM_SET(self.request.POST, instance=receipt_voucher, form_kwargs={'company': company})
        else:
            context['receipts'] = RECEIPT_FORM_SET(instance=receipt_voucher, form_kwargs={'company': company})
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
        receipt_voucher = context['receipts']
        if receipt_voucher.is_valid():
            receipt_voucher.save()
        return super(ReceiptVoucherUpdateView, self).form_valid(form)

    def get_form_kwargs(self):
        data = super(ReceiptVoucherUpdateView, self).get_form_kwargs()
        data.update(
            user=self.request.user,
            company=Company.objects.get(pk=self.kwargs['company_pk'])
        )
        return data


class ReceiptVoucherDeleteView(ProductExistsRequiredMixin, UserPassesTestMixin, LoginRequiredMixin, DeleteView):
    """
    Receipt Voucher Delete View
    """
    model = ReceiptVoucher
    template_name = "Receipt/receipt_confirm_delete.html"

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        return reverse('accounting_entry:receiptlist', kwargs={'company_pk': company.pk, 'period_selected_pk': period_selected.pk})

    def get_object(self):
        return get_object_or_404(ReceiptVoucher, pk=self.kwargs['receipt_voucher_pk'])

    def test_func(self):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        receipt_voucher = self.get_object()
        return self.request.user in company.accountant.all() or \
            self.request.user in company.cb_personal.all() or \
            self.request.user == receipt_voucher.user

    def get_context_data(self, **kwargs):
        context = super(ReceiptVoucherDeleteView, self).get_context_data(**kwargs)

        context['profile_details'] = Profile.objects.all()
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        context['receipt'] = get_object_or_404(ReceiptVoucher, pk=self.kwargs['receipt_voucher_pk'])
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        return context
