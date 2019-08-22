import qrcode

from django.shortcuts import get_object_or_404, redirect
from django.views.generic import (ListView, DetailView,
                                  CreateView, UpdateView)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.functions import Coalesce
from django.db.models import Count, Value
from django.http import HttpResponse
from django.urls import reverse

from company.models import Organisation
from accounting_entry.models import PeriodSelected
from messaging.models import Message
from .mixins import QRProductExistsRequiredMixin
from .models import StockMasterQR
from .forms import StockItemsQRForm


# Create your views here.

class StocksForQRListView(QRProductExistsRequiredMixin, LoginRequiredMixin, ListView):
    """
    Stock Item List View For QR Code Creation
    """
    context_object_name = 'StockMasterQR_list'
    model = StockMasterQR
    template_name = 'qr_code/stock_list.html'

    def get_queryset(self):
        return StockMasterQR.objects.filter(company=self.kwargs['organisation_pk']).order_by('id')

    def get_context_data(self, **kwargs):
        context = super(StocksForQRListView, self).get_context_data(**kwargs)

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


class StockitemDetailsQRView(QRProductExistsRequiredMixin, LoginRequiredMixin, DetailView):
    """
    Stock Data Details View For QR Code
    """
    context_object_name = 'StockMasterQR_details'
    model = StockMasterQR
    template_name = 'qr_code/stockdata_details.html'

    def get_object(self):
        organisation_pk = self.kwargs['organisation_pk']
        qr_code_pk = self.kwargs['qr_code_pk']
        period_selected_pk = self.kwargs['period_selected_pk']
        get_object_or_404(PeriodSelected, pk=period_selected_pk)
        get_object_or_404(Organisation, pk=organisation_pk)
        StockMasterQR_details = get_object_or_404(StockMasterQR, pk=qr_code_pk)
        return StockMasterQR_details

    def get_context_data(self, **kwargs):
        context = super(StockitemDetailsQRView,
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


class StockMasterQRCreateview(QRProductExistsRequiredMixin, LoginRequiredMixin, CreateView):
    """
    Stock Master QR Create View
    """
    form_class = StockItemsQRForm
    template_name = "qr_code/stockdata_create.html"

    def get_success_url(self, **kwargs):
        organisation = get_object_or_404(
            Organisation, pk=self.kwargs['organisation_pk'])
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        stocksqr = StockMasterQR.objects.filter(
            company=organisation.pk).order_by('-id')
        for p in stocksqr:
            if p:
                return reverse('qr_code:stock_items_details_qr', kwargs={'organisation_pk': organisation.pk, 'qr_code_pk': p.pk, 'period_selected_pk': period_selected.pk})

    def form_valid(self, form):
        form.instance.user = self.request.user
        c = Organisation.objects.get(pk=self.kwargs['organisation_pk'])
        form.instance.company = c
        counter = StockMasterQR.objects.filter(
            company=c).count() + 1
        print(counter)
        form.instance.counter = counter
        return super(StockMasterQRCreateview, self).form_valid(form)

    def get_form_kwargs(self):
        data = super(StockMasterQRCreateview, self).get_form_kwargs()
        data.update(
            company=Organisation.objects.get(pk=self.kwargs['organisation_pk'])
        )
        return data

    def get_context_data(self, **kwargs):
        context = super(StockMasterQRCreateview,
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


class StockMasterQRUpdateView(QRProductExistsRequiredMixin, LoginRequiredMixin, UpdateView):
    """
    Stock Master QR Update View
    """
    model = StockMasterQR
    form_class = StockItemsQRForm
    template_name = "qr_code/stockdata_create.html"

    def get_success_url(self):
        organisation = get_object_or_404(
            Organisation, pk=self.kwargs['organisation_pk'])
        stockdata_details = get_object_or_404(
            StockMasterQR, pk=self.kwargs['qr_code_pk'])
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        return reverse('qr_code:stock_items_details_qr', kwargs={'pk': organisation.pk, 'qr_code_pk': stockdata_details.pk, 'period_selected_pk': period_selected.pk})

    def get_object(self):
        pk = self.kwargs['organisation_pk']
        qr_code_pk = self.kwargs['qr_code_pk']
        get_object_or_404(Organisation, pk=pk)
        stockdata = get_object_or_404(StockMasterQR, pk=qr_code_pk)
        return stockdata

    def get_form_kwargs(self):
        data = super(StockMasterQRUpdateView, self).get_form_kwargs()
        data.update(
            company=Organisation.objects.get(pk=self.kwargs['organisation_pk'])
        )
        return data

    def get_context_data(self, **kwargs):
        context = super(StockMasterQRUpdateView,
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


def generate_qr_code(request, organisation_pk, qr_code_pk, period_selected_pk):
    """
    Function Based View For Generating QR Code
    """
    Stock_items = get_object_or_404(StockMasterQR, pk=qr_code_pk)
    company = get_object_or_404(Organisation, pk=organisation_pk)
    period_selected = get_object_or_404(
        PeriodSelected, pk=period_selected_pk)

    qr_image = qrcode.make(Stock_items)
    path = 'media/qr_images/' + Stock_items.stock_name + '.png'
    qr_image.save(path)
    Stock_items.qr_code = 'qr_images/' + Stock_items.stock_name + '.png'
    Stock_items.is_qr = True
    Stock_items.save()

    return redirect(reverse('qr_code:stock_items_details_qr', kwargs={"organisation_pk": company.pk, "qr_code_pk": Stock_items.pk, "period_selected_pk": period_selected.pk}))


def download_qr_code(request, organisation_pk, qr_code_pk, period_selected_pk):
    """
    Function Based View For Downloading QR Code
    """
    Stock_items = get_object_or_404(StockMasterQR, pk=qr_code_pk)
    company = get_object_or_404(Organisation, pk=organisation_pk)
    period_selected = get_object_or_404(
        PeriodSelected, pk=period_selected_pk)

    response = HttpResponse(Stock_items.qr_code, content_type='image/png')
    response['Content-Disposition'] = 'attachment; filename={}.png'.format(
        Stock_items.stock_name)
    return response
