from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.db.models.functions import Coalesce
from django.db.models import Count, Value

from company.models import Organisation
from accounting_entry.models import PeriodSelected
from messaging.models import Message
from .mixins import QRProductExistsRequiredMixin


class QRDashboard(QRProductExistsRequiredMixin, LoginRequiredMixin, TemplateView):
    """
    Bracket QR Dashboard View
    """
    template_name = 'qr_code/qr_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(QRDashboard, self).get_context_data(**kwargs)

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
