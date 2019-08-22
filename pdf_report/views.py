"""
Views
"""
import calendar
import collections
import dateutil
from django.db.models import Case, When, Value, Sum, F
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View
from django.template.loader import get_template
from company.models import Company
from accounting_entry.models import LedgerMaster, JournalVoucher, PeriodSelected
from stock_keeping.models_purchase import PurchaseVoucher, PurchaseStock
from stock_keeping.models_sale import SaleVoucher, SaleStock
from .utils import render_to_pdf


class PDFGeneratorPurchase(View):
    """
    PDF Generator Purchase
    """

    def get(self, request, *args, **kwargs):
        template = get_template('purchase_details_pdf.html')

        purchase_details = get_object_or_404(PurchaseVoucher, pk=self.kwargs['pk2'])
        stocklist = PurchaseStock.objects.filter(purchases=purchase_details.pk)

        context = {
            "company": get_object_or_404(Company, pk=self.kwargs['company_pk']),
            "period_selected": get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk']),
            "purchase_details": purchase_details,
            "stocklist": stocklist,
        }
        html = template.render(context)
        pdf = render_to_pdf('purchase_details_pdf.html', context)
        if pdf:
            return HttpResponse(pdf, content_type='application/pdf')
        return HttpResponse("PDF Not Found")


class PDFGeneratorSale(View):
    """
    PDF Generator Sale
    """

    def get(self, request, *args, **kwargs):
        template = get_template('sales_details_pdf.html')

        sales_details = get_object_or_404(SaleVoucher, pk=self.kwargs['pk2'])
        stocklist = SaleStock.objects.filter(sales=sales_details.pk)

        context = {
            "company": get_object_or_404(Company, pk=self.kwargs['company_pk']),
            "period_selected": get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk']),
            "sales_details": sales_details,
            "stocklist": stocklist,
        }
        html = template.render(context)
        pdf = render_to_pdf('sales_details_pdf.html', context)
        if pdf:
            return HttpResponse(pdf, content_type='application/pdf')
        return HttpResponse("PDF Not Found")


class PDFGeneratorPeriodicJournal(View):
    """
    PDF Generator Periodic Journal
    """

    def get(self, request, *args, **kwargs):
        template = get_template('ledger_monthly_pdf.html')

        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        ledger_master = get_object_or_404(LedgerMaster, pk=self.kwargs['ledger_master_pk'])
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])

        # opening balance
        qsob = JournalVoucher.objects.filter(user=self.request.user, company=company, By=ledger_master.pk,
                                             Date__gte=ledger_master.Creation_Date, voucher_date__lte=period_selected.start_date)
        qsob2 = JournalVoucher.objects.filter(user=self.request.user, company=company, To=ledger_master.pk,
                                              Date__gte=ledger_master.Creation_Date, voucher_date__lte=period_selected.start_date)

        total_debitob = qsob.aggregate(the_sum=Coalesce(Sum('Debit'), Value(0)))['the_sum']
        total_creditob = qsob2.aggregate(the_sum=Coalesce(Sum('Credit'), Value(0)))['the_sum']

        if(ledger_master.Creation_Date != period_selected.start_date):
            if(ledger_master.ledger_group.balance_nature == 'Debit'):
                opening_balance = abs(ledger_master.opening_balance) + abs(total_debitob) - abs(total_creditob)
            else:
                opening_balance = abs(ledger_master.opening_balance) + abs(total_creditob) - abs(total_debitob)
        else:
            opening_balance = abs(ledger_master.opening_balance)

        results = collections.OrderedDict()

        qscb = JournalVoucher.objects.filter(user=self.request.user, company=company, By=ledger_master.pk, voucher_date__gte=period_selected.start_date,
                                             voucher_date__lte=period_selected.end_date).annotate(real_total_debit=Case(When(Debit__isnull=True, then=0), default=F('Debit')))
        qscb2 = JournalVoucher.objects.filter(user=self.request.user, company=company, To=ledger_master.pk, voucher_date__gte=period_selected.start_date,
                                              voucher_date__lte=period_selected.end_date).annotate(real_total_credit=Case(When(Debit__isnull=True, then=0), default=F('Debit')))

        date_cursor = period_selected.start_date

        z = 0
        k = 0

        while date_cursor < period_selected.end_date:
            month_partial_total_debit = qscb.filter(Date__month=date_cursor.month).aggregate(partial_total_debit=Sum('real_total_debit'))['partial_total_debit']
            month_partial_total_credit = qscb2.filter(Date__month=date_cursor.month).aggregate(partial_total_credit=Sum('real_total_credit'))['partial_total_credit']

            if month_partial_total_debit == None:

                month_partial_total_debit = int(0)

                e = month_partial_total_debit

            else:

                e = month_partial_total_debit

            if month_partial_total_credit == None:

                month_partial_total_credit = int(0)

                f = month_partial_total_credit

            else:

                f = month_partial_total_credit

            if(ledger_master.ledger_group.balance_nature == 'Debit'):

                z = z + e - f

            else:
                z = z + f - e

            k = z + opening_balance

            results[calendar.month_name[date_cursor.month]] = [e, f, k]

            date_cursor += dateutil.relativedelta.relativedelta(months=1)

        total_debit = qscb.aggregate(the_sum=Coalesce(Sum('Debit'), Value(0)))['the_sum']
        total_credit = qscb2.aggregate(the_sum=Coalesce(Sum('Credit'), Value(0)))['the_sum']

        if(ledger_master.ledger_group.balance_nature == 'Debit'):

            total1 = total_debit - total_credit

        else:

            total1 = total_credit - total_debit

        total = total1 + opening_balance

        context = {

            'company': company,
            'ledger_master': ledger_master,
            'period_selected': period_selected,
            'total_debit': total_debit,
            'total_credit': total_credit,
            'total': total,
            'data': results.items(),
            'opening_balance': opening_balance,
        }

        html = template.render(context)
        pdf = render_to_pdf('ledger_monthly_pdf.html', context)
        if pdf:
            return HttpResponse(pdf, content_type='application/pdf')
        return HttpResponse("PDF Not Found")
