"""
Views for PaymentVoucher Voucher
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
from .models import PeriodSelected, PaymentVoucher #, PaymentVoucherRows
from .forms import PaymentVoucherForm, PAYMENT_FORM_SET


class PaymentVoucherListView(ProductExistsRequiredMixin, LoginRequiredMixin, ListView):
    """
    Payment Voucher List View
    """
    model = PaymentVoucher
    template_name = 'Payments/payment_list.html'
    paginate_by = 15

    def get_queryset(self):
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])

        return self.model.objects.filter(
            company=self.kwargs['company_pk'],
            voucher_date__gte=period_selected.start_date,
            voucher_date__lte=period_selected.end_date).order_by('-id')

    def get_context_data(self, **kwargs):
        context = super(PaymentVoucherListView, self).get_context_data(**kwargs)

        context['profile_details'] = Profile.objects.all()
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        # context['payment_list'] = PaymentVoucher.objects.filter(
        #     company=self.kwargs['company_pk'],
        #     voucher_date__gte=period_selected.start_date,
        #     voucher_date__lte=period_selected.end_date).order_by('-id')
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        return context


class PaymentVoucherDetailView(ProductExistsRequiredMixin, LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    Payment Voucher Detail View
    """
    context_object_name = 'payment_voucher'
    model = PaymentVoucher
    template_name = 'Payments/payment_details.html'

    def get_object(self):
        return get_object_or_404(PaymentVoucher, pk=self.kwargs['payment_voucher_pk'])

    def test_func(self):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        payments = self.get_object()
        return self.request.user in company.auditor.all() or \
            self.request.user in company.accountant.all() or \
            self.request.user in company.cb_personal.all() or \
            self.request.user == payments.user

    def get_context_data(self, **kwargs):
        context = super(PaymentVoucherDetailView, self).get_context_data(**kwargs)

        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        # payment_voucher = get_object_or_404(PaymentVoucher, pk=kwargs['payment_voucher_pk'])
        # context['payment_voucher'] = payment_voucher
        # payment_voucher.account.save()
        # payment_voucher_row = PaymentVoucherRows.objects.filter(payment=payment_voucher)
        # for obj in payment_voucher_row:
        #     obj.save()
        #     obj.particular.save()
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        return context


class PaymentVoucherCreateView(ProductExistsRequiredMixin, LoginRequiredMixin, CreateView):
    """
    Payment Voucher Create View
    """
    form_class = PaymentVoucherForm
    success_message = "%(account)s is submitted successfully"
    template_name = 'Payments/payment_form.html'

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        payment = PaymentVoucher.objects.filter(
            company=company,
            voucher_date__gte=period_selected.start_date,
            voucher_date__lte=period_selected.end_date).order_by('-id')
        for voucher in payment:
            return reverse('accounting_entry:paymentdetail', kwargs={'company_pk': company.pk, 'payment_voucher_pk': voucher.pk, 'period_selected_pk': period_selected.pk})

    def get_context_data(self, **kwargs):
        context = super(PaymentVoucherCreateView, self).get_context_data(**kwargs)

        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        if self.request.POST:
            context['payments'] = PAYMENT_FORM_SET(self.request.POST, form_kwargs={'company': company})
        else:
            context['payments'] = PAYMENT_FORM_SET(form_kwargs={'company': company})

        context['successful_submit'] = True

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
        counter = PaymentVoucher.objects.filter(
            user=self.request.user, company=company).count() + 1
        form.instance.counter = counter
        context = self.get_context_data()
        payments = context['payments']

        if form.is_valid() and payments.is_valid():
            with transaction.atomic():
                self.object = form.save()
                payments.instance = self.object
                payments.save()

        return super(PaymentVoucherCreateView, self).form_valid(form)

    def get_form_kwargs(self):
        data = super(PaymentVoucherCreateView, self).get_form_kwargs()
        data.update(
            user=self.request.user,
            company=Company.objects.get(pk=self.kwargs['company_pk'])
        )
        return data


class PaymentVoucherUpdateView(ProductExistsRequiredMixin, UserPassesTestMixin, LoginRequiredMixin, UpdateView):
    """
    Payment Voucher Update View
    """
    model = PaymentVoucher
    form_class = PaymentVoucherForm
    template_name = 'Payments/payment_form.html'

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        payment_voucher = get_object_or_404(PaymentVoucher, pk=self.kwargs['payment_voucher_pk'])
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])

        return reverse('accounting_entry:paymentdetail', kwargs={'company_pk': company.pk, 'payment_voucher_pk': payment_voucher.pk, 'period_selected_pk': period_selected.pk})

    def get_object(self):
        return get_object_or_404(PaymentVoucher, pk=self.kwargs['payment_voucher_pk'])

    def test_func(self):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        payments = self.get_object()
        return self.request.user in company.accountant.all() or \
            self.request.user in company.cb_personal.all() or \
            self.request.user == payments.user

    def get_context_data(self, **kwargs):
        context = super(PaymentVoucherUpdateView, self).get_context_data(**kwargs)

        payment_voucher = get_object_or_404(PaymentVoucher, pk=self.kwargs['payment_voucher_pk'])
        payments = PaymentVoucher.objects.get(pk=payment_voucher.pk)
        context['profile_details'] = Profile.objects.all()
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        if self.request.POST:
            context['payments'] = PAYMENT_FORM_SET(
                self.request.POST, instance=payments, form_kwargs={'company': company})
        else:
            context['payments'] = PAYMENT_FORM_SET(instance=payments, form_kwargs={'company': company})
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
        payments = context['payments']
        
        if payments.is_valid():
            payments.save()

        return super(PaymentVoucherUpdateView, self).form_valid(form)

    def get_form_kwargs(self):
        data = super(PaymentVoucherUpdateView, self).get_form_kwargs()
        data.update(
            user=self.request.user,
            company=Company.objects.get(pk=self.kwargs['company_pk'])
        )
        return data


class PaymentVoucherDeleteView(ProductExistsRequiredMixin, UserPassesTestMixin, LoginRequiredMixin, DeleteView):
    """
    Payment Voucher Delete View
    """
    model = PaymentVoucher
    template_name = "Payments/payment_confirm_delete.html"

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])

        return reverse('accounting_entry:paymentlist', kwargs={'company_pk': company.pk, 'period_selected_pk': period_selected.pk})

    def get_object(self):
        return get_object_or_404(PaymentVoucher, pk=self.kwargs['payment_voucher_pk'])

    def test_func(self):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        payments = self.get_object()
        return self.request.user in company.accountant.all() or \
            self.request.user in company.cb_personal.all() or \
            self.request.user == payments.user

    def get_context_data(self, **kwargs):
        context = super(PaymentVoucherDeleteView, self).get_context_data(**kwargs)

        context['profile_details'] = Profile.objects.all()
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        #context['payment'] = get_object_or_404(PaymentVoucher, pk=self.kwargs['payment_voucher_pk'])
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        return context
