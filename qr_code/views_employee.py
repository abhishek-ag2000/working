import qrcode

from django.shortcuts import get_object_or_404, redirect
from django.views.generic import (ListView, DetailView,
                                  CreateView, UpdateView)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.functions import Coalesce
from django.db.models import Count, Value
from django.urls import reverse

from company.models import Organisation
from accounting_entry.models import PeriodSelected
from messaging.models import Message
from .mixins import QRProductExistsRequiredMixin
from .models import EmployeeMasterQR
from .forms import EmployeeMasterQRForm


class EmployeeQrListView(QRProductExistsRequiredMixin, LoginRequiredMixin, ListView):
    """
    Employee List View For Bracket-QR
    """
    context_object_name = 'employee_list'
    model = EmployeeMasterQR
    template_name = 'employee_qr_code/employee_list.html'

    def get_queryset(self):
        return EmployeeMasterQR.objects.filter(company=self.kwargs['organisation_pk']).order_by('id')

    def get_context_data(self, **kwargs):
        context = super(EmployeeQrListView, self).get_context_data(**kwargs)

        organisation = get_object_or_404(
            Organisation, pk=self.kwargs['organisation_pk'])
        context['organisation'] = organisation
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected

        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        return context


class EmployeeQrDetailsQRView(QRProductExistsRequiredMixin, LoginRequiredMixin, DetailView):
    """
    Employee Qr Details View
    """
    context_object_name = 'EmployeeQr_details'
    model = EmployeeMasterQR
    template_name = 'employee_qr_code/employee_details.html'

    def get_object(self):
        organisation_pk = self.kwargs['organisation_pk']
        qr_code_pk = self.kwargs['qr_code_pk']
        period_selected_pk = self.kwargs['period_selected_pk']
        get_object_or_404(PeriodSelected, pk=period_selected_pk)
        get_object_or_404(Organisation, pk=organisation_pk)
        EmployeeQr_details = get_object_or_404(EmployeeMasterQR, pk=qr_code_pk)
        return EmployeeQr_details

    def get_context_data(self, **kwargs):
        context = super(EmployeeQrDetailsQRView,
                        self).get_context_data(**kwargs)
        organisation = get_object_or_404(
            Organisation, pk=self.kwargs['organisation_pk'])
        context['organisation'] = organisation
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        return context


class EmployeeMasterQRCreateview(QRProductExistsRequiredMixin, LoginRequiredMixin, CreateView):
    """
    Employee Master QR Create View
    """
    form_class = EmployeeMasterQRForm
    template_name = "employee_qr_code/employee_create.html"

    def get_success_url(self, **kwargs):
        organisation = get_object_or_404(
            Organisation, pk=self.kwargs['organisation_pk'])
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        stocksqr = EmployeeMasterQR.objects.filter(
            company=organisation.pk).order_by('-id')
        for p in stocksqr:
            if p:
                return reverse('qr_code:stock_items_details_qr', kwargs={'organisation_pk': organisation.pk, 'qr_code_pk': p.pk, 'period_selected_pk': period_selected.pk})

    def form_valid(self, form):
        form.instance.user = self.request.user
        c = Organisation.objects.get(pk=self.kwargs['organisation_pk'])
        form.instance.company = c
        counter = EmployeeMasterQR.objects.filter(
            company=c).count() + 1
        print(counter)
        form.instance.counter = counter
        return super(EmployeeMasterQRCreateview, self).form_valid(form)

    def get_form_kwargs(self):
        data = super(EmployeeMasterQRCreateview, self).get_form_kwargs()
        data.update(
            organisation=Organisation.objects.get(pk=self.kwargs['organisation_pk'])
        )
        return data

    def get_context_data(self, **kwargs):
        context = super(EmployeeMasterQRCreateview,
                        self).get_context_data(**kwargs)
        organisation = get_object_or_404(
            Organisation, pk=self.kwargs['organisation_pk'])
        context['organisation'] = organisation
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        return context


class EmployeeMasterQRRUpdateView(QRProductExistsRequiredMixin, LoginRequiredMixin, UpdateView):
    """
    Employe Master QR Update View
    """
    model = EmployeeMasterQR
    form_class = EmployeeMasterQRForm
    template_name = "employee_qr_code/employee_create.html"

    def get_success_url(self):
        organisation = get_object_or_404(
            Organisation, pk=self.kwargs['organisation_pk'])
        employee_details = get_object_or_404(
            EmployeeMasterQR, pk=self.kwargs['qr_code_pk'])
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        return reverse('qr_code:employee_details_qr', kwargs={'organisation_pk': organisation.pk, 'qr_code_pk': employee_details.pk, 'period_selected_pk': period_selected.pk})

    def get_object(self):
        pk = self.kwargs['organisation_pk']
        qr_code_pk = self.kwargs['qr_code_pk']
        get_object_or_404(Company, pk=pk)
        employee_data = get_object_or_404(EmployeeMasterQR, pk=qr_code_pk)
        return employee_data

    def get_form_kwargs(self):
        data = super(EmployeeMasterQRCreateview, self).get_form_kwargs()
        data.update(
            organisation=Organisation.objects.get(pk=self.kwargs['organisation_pk'])
        )
        return data


    def get_context_data(self, **kwargs):
        context = super(EmployeeMasterQRRUpdateView,
                        self).get_context_data(**kwargs)
        organisation = get_object_or_404(
            Organisation, pk=self.kwargs['organisation_pk'])
        context['organisation'] = organisation
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        return context


def generate_employee_qr_code(request, organisation_pk, qr_code_pk, period_selected_pk):
    """
    Function Based View For Generating QR Code
    """
    employee_details = get_object_or_404(EmployeeMasterQR, pk=qr_code_pk)
    company = get_object_or_404(Organisation, pk=organisation_pk)
    period_selected = get_object_or_404(PeriodSelected, pk=period_selected_pk)

    qr_image = qrcode.make(employee_details)
    path = 'media/qr_images/' + employee_details.employee_name + '.png'
    qr_image.save(path)
    employee_details.qr_code = 'qr_images/' + \
        employee_details.employee_name + '.png'
    employee_details.is_qr = True
    employee_details.save()

    return redirect(reverse('qr_code:employee_details_qr', kwargs={"organisation_pk": company.pk, "qr_code_pk": employee_details.pk, "period_selected_pk": period_selected.pk}))
