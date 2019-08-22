"""
Views for Contra Voucher
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
from .models import PeriodSelected, ContraVoucher, ContraVoucherRows
from .forms import ContraVoucherForm, CONTRA_FORM_SET


class ContraVoucherListView(ProductExistsRequiredMixin, LoginRequiredMixin, ListView):
    """
    Contra Voucher List View
    """
    model = ContraVoucher
    template_name = 'Contra/contra_list.html'
    paginate_by = 15

    def get_queryset(self):
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        
        return self.model.objects.filter(
            company=self.kwargs['company_pk'],
            voucher_date__gte=period_selected.start_date,
            voucher_date__lte=period_selected.end_date).order_by('-id')

    def get_context_data(self, **kwargs):
        context = super(ContraVoucherListView, self).get_context_data(**kwargs)

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


class ContraVoucherDetailView(ProductExistsRequiredMixin, UserPassesTestMixin, LoginRequiredMixin, DetailView):
    """
    Contra Voucher Detail View
    """
    context_object_name = 'contra_voucher'
    model = ContraVoucher
    template_name = 'Contra/contra_details.html'

    def get_object(self):
        return get_object_or_404(ContraVoucher, pk=self.kwargs['contra_voucher_pk'])

    def test_func(self):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        receipts = self.get_object()
        return self.request.user in company.auditor.all() or \
            self.request.user in company.accountant.all() or \
            self.request.user in company.cb_personal.all() or \
            self.request.user == receipts.user

    def get_context_data(self, **kwargs):
        context = super(ContraVoucherDetailView, self).get_context_data(**kwargs)

        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        # contra_voucher = get_object_or_404(ContraVoucher, pk=self.kwargs['contra_voucher_pk'])
        # context['contra_voucher'] = contra_voucher
        # contra_voucher.account.save()
        # contra_ac = ContraVoucherRows.objects.filter(contra=contra_voucher)
        # for obj in contra_ac:
        #     obj.save()
        #     obj.particular.save()
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        return context


class ContraVoucherCreateView(ProductExistsRequiredMixin, LoginRequiredMixin, CreateView):
    """
    Contra Voucher Create View
    """
    form_class = ContraVoucherForm
    success_message = "%(account)s is submitted successfully"
    template_name = 'Contra/contra_form.html'

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        contra = ContraVoucher.objects.filter(
            company=company,
            voucher_date__gte=period_selected.start_date,
            voucher_date__lte=period_selected.end_date).order_by('-id')
        for voucher in contra:
            return reverse('accounting_entry:contradetail', kwargs={'company_pk': company.pk, 'contra_voucher_pk': voucher.pk, 'period_selected_pk': period_selected.pk})

    def get_context_data(self, **kwargs):
        context = super(ContraVoucherCreateView, self).get_context_data(**kwargs)

        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected

        if self.request.POST:
            context['contra_voucher'] = CONTRA_FORM_SET(self.request.POST, form_kwargs={'company': company})
        else:
            context['contra_voucher'] = CONTRA_FORM_SET(form_kwargs={'company': company})

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
        counter = ContraVoucher.objects.filter(
            user=self.request.user, company=company).count() + 1
        form.instance.counter = counter
        context = self.get_context_data()
        contra = context['contra_voucher']

        if form.is_valid() and contra.is_valid():
            with transaction.atomic():
                self.object = form.save()
                contra.instance = self.object
                contra.save()

        return super(ContraVoucherCreateView, self).form_valid(form)

    def get_form_kwargs(self):
        data = super(ContraVoucherCreateView, self).get_form_kwargs()
        data.update(
            user=self.request.user,
            company=Company.objects.get(pk=self.kwargs['company_pk'])
        )

        return data


class ContraVoucherUpdateView(ProductExistsRequiredMixin, UserPassesTestMixin, LoginRequiredMixin, UpdateView):
    """
    Contra Voucher Update View
    """
    model = ContraVoucher
    form_class = ContraVoucherForm
    template_name = 'Contra/contra_form.html'

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        contra_voucher = get_object_or_404(ContraVoucher, pk=self.kwargs['contra_voucher_pk'])
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        
        return reverse('accounting_entry:contradetail', kwargs={'company_pk': company.pk, 'contra_voucher_pk': contra_voucher.pk, 'period_selected_pk': period_selected.pk})

    def get_object(self):
        return get_object_or_404(ContraVoucher, pk=self.kwargs['contra_voucher_pk'])

    def test_func(self):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        contra_voucher = self.get_object()
        return self.request.user in company.accountant.all() or \
               self.request.user in company.cb_personal.all() or \
               self.request.user == contra_voucher.user

    def get_context_data(self, **kwargs):
        context = super(ContraVoucherUpdateView, self).get_context_data(**kwargs)

        contra_voucher = get_object_or_404(ContraVoucher, pk=self.kwargs['contra_voucher_pk'])
        context['profile_details'] = Profile.objects.all()
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        if self.request.POST:
            context['contra_voucher'] = CONTRA_FORM_SET(
                self.request.POST, instance=contra_voucher, form_kwargs={'company': company})
        else:
            context['contra_voucher'] = CONTRA_FORM_SET(instance=contra_voucher, form_kwargs={'company': company})
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
        contra_voucher = context['contra_voucher']

        if contra_voucher.is_valid():
            contra_voucher.save()

        return super(ContraVoucherUpdateView, self).form_valid(form)

    def get_form_kwargs(self):
        data = super(ContraVoucherUpdateView, self).get_form_kwargs()
        data.update(
            user=self.request.user,
            company=Company.objects.get(pk=self.kwargs['company_pk'])
        )
        return data


class ContraVoucherDeleteView(ProductExistsRequiredMixin, UserPassesTestMixin, LoginRequiredMixin, DeleteView):
    """
    Contra Voucher Delete View
    """
    model = ContraVoucher
    template_name = "Contra/contra_confirm_delete.html"

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        return reverse('accounting_entry:contralist', kwargs={'company_pk': company.pk, 'period_selected_pk': period_selected.pk})

    def get_object(self):
        get_object_or_404(Company, pk=self.kwargs['company_pk'])
        contra_voucher = get_object_or_404(ContraVoucher, pk=self.kwargs['contra_voucher_pk'])
        return contra_voucher

    def test_func(self):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        contra_voucher = self.get_object()
        return self.request.user in company.cb_personal.all() or \
               self.request.user == contra_voucher.user

    def get_context_data(self, **kwargs):
        context = super(ContraVoucherDeleteView, self).get_context_data(**kwargs)

        context['profile_details'] = Profile.objects.all()
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        #context['contra_voucher'] = get_object_or_404(ContraVoucher, pk=self.kwargs['pk2'])
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        return context
