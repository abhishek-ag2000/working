"""
GSTR-1
"""
import itertools
from decimal import Decimal
from django.shortcuts import get_object_or_404, Http404
from django.db.models.functions import Coalesce
from django.db.models import Count, Value, Sum, Q, F, Case, When
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from messaging.models import Message

from company.models import Company
from accounting_entry.models import PeriodSelected
from accounting_entry.mixins import ProductExistsRequiredMixin
from stock_keeping.models_sale import SaleVoucher, SaleStock
from stock_keeping.models_credit_note import CreditNoteVoucher, CreditNoteStock


class GSTRQueryProvider():
    """
    GSTR Query Provider provides various filtered queryset without evaluating data
    """
    unregisted_party_types = [
        "Unknown",
        "Consumer",
        "Unregistered"
    ]

    b2b_tran_nature = [
        "Deemed Exports Exempt",
        "Deemed Exports Nil Rated",
        "Deemed Exports Taxable",
        "Interstate Sales - Taxable",
        "Interstate Sales to Embassy / UN Body Taxable",
        "Intrastate Deemed Exports Exempt",
        "Intrastate Deemed Exports Nil Rated",
        "Intrastate Deemed Exports Taxable",
        "Intrastate Sales Taxable",
        "Sales to SEZ - Exempt",
        "Sales to SEZ - LUT/Bond",
        "Sales to SEZ - Nil Rated",
        "Sales to SEZ - Taxable"
    ]

    b2cs_same_state_tran_nature = [
        "Intrastate Sales Taxable",
        "sales to Consumer - Exempt",
        "sales to Consumer - Nil Rated",
        "sales to Consumer - Taxable"
    ]

    other_state_sales_taxable_nature = "Interstate Sales - Taxable"

    notes_reg_tran_nature = [
        "Deemed Exports Exempt",
        "Deemed Exports Nil Rated",
        "Deemed Exports Taxable",
        "Interstate Sales - Taxable",
        "Interstate Sales to Embassy / UN Body Taxable",
        "Intrastate Deemed Exports Exempt",
        "Intrastate Deemed Exports Nil Rated",
        "Intrastate Deemed Exports Taxable",
        "Intrastate Sales Taxable",
        "Sales to SEZ - Exempt",
        "Sales to SEZ - LUT/Bond",
        "Sales to SEZ - Nil Rated",
        "Sales to SEZ - Taxable"
    ]

    notes_ureg_export_tran_nature = [
        "Exports Exempt",
        "Exports LUT/Bond",
        "Exports Nil Rated",
        "Exports Taxable"
    ]

    export_tran_nature = [
        "Exports Exempt",
        "Exports LUT/Bond",
        "Exports Nil Rated",
        "Exports Taxable"
    ]

    nil_rated_tran_nature = [
        "Interstate Sales Nil Rated"
        "Interstate Sales Exempt"
        "Interstate Sales to Embassy / UN Body Nil Rated"
        "Interstate Sales to Embassy / UN Body Exempt"
        "Sales Exempt"
        "Sales Nil Rated"
        "Not Applicable"
    ]

    @staticmethod
    def get_b2b_query_set(company, period_selected):
        """
        Returns a query set for B2B
        """
        # B2B
        # Details of invoices of Taxable supplies made to other registered taxpayers
        # Conditions:
        # 1. Nature of transaction in list of B2B transaction nature
        # 2. GSTIN present in voucher
        return SaleVoucher.objects.filter(
            Q(party_ac__registration_type__exact='Regular') | Q(
                party_ac__registration_type__exact='Composition'),
            company=company,
            voucher_date__gte=period_selected.start_date,
            voucher_date__lt=period_selected.end_date,
            nature_transactions_sales__in=GSTRQueryProvider.b2b_tran_nature,
        ).exclude(
            party_ac__gst_no__exact='')

    @staticmethod
    def get_b2cl_query_set(company, period_selected):
        """
        Returns a query set for B2CL
        """
        # B2CL
        # Invoices for Taxable outward supplies to consumers where
        # a)The place of supply is outside the state where the supplier is registered and
        # b)The total invoice value is more that Rs 2,50,000
        # Conditions:
        # 1. GSTIN not present
        # 2. Nature of transaction is "Interstate Sales Taxable"
        # 3. Invoice value > 2,50,000.00
        # 4. Company's state is not same as party's state
        return SaleVoucher.objects.filter(
            company=company,
            voucher_date__gte=period_selected.start_date,
            voucher_date__lt=period_selected.end_date,
            nature_transactions_sales__exact=GSTRQueryProvider.other_state_sales_taxable_nature,
            party_ac__gst_no__exact='',
            total__gt=250000.0,
            party_ac__registration_type__in=GSTRQueryProvider.unregisted_party_types
        ).exclude(party_ac__state__state_name__exact=company.organisation.state.state_name)

    @staticmethod
    def get_b2cs_summary_query_set(company, period_selected):
        """
        Returns a query set for B2CS in summary (due to limitation on union operation data has been early fetched and aggrigation performed)
        """
       # B2CS
        # Supplies made to consumers and unregistered persons of the following nature
        # a) Intra-state__state_name: any value
        # b) Inter-State: Invoice value Rs 2.5 lakh or less
        # Conditions:
        # 1. GSTIN not present
        # 2. [Inter-State] Nature of transaction is "Interstate Sales Taxable" and Invoice value <= 2,50,000.00 and
        #    Company's state is not same as party's state
        # 3. [Intra-State] Nature of transaction in list of b2cs transaction nature
        rec_filter1 = SaleStock.objects.filter(
            Q(
                Q(sale_voucher__nature_transactions_sales__exact=GSTRQueryProvider.other_state_sales_taxable_nature) &
                ~Q(sale_voucher__party_ac__state__state_name__exact=company.organisation.state.state_name) &
                Q(sale_voucher__total__lte=250000.0)
            ) |
            Q(
                Q(sale_voucher__nature_transactions_sales__in=GSTRQueryProvider.b2cs_same_state_tran_nature) &
                Q(sale_voucher__party_ac__state__state_name__exact=company.organisation.state.state_name)
            ),
            sale_voucher__company=company,
            sale_voucher__voucher_date__gte=period_selected.start_date,
            sale_voucher__voucher_date__lt=period_selected.end_date,
            sale_voucher__party_ac__gst_no__exact='',
            sale_voucher__party_ac__registration_type__in=GSTRQueryProvider.unregisted_party_types
        ).annotate(
            state_name_out=F('sale_voucher__party_ac__state__state_name'),
            taxable_amount_out=F('total'),
            tax_rate_out=Case(When(cgst__gt=0, then=F(
                'cgst') + F('sgst')), default=(F('igst'))),
            sgst_amount_out=F('sgst_total'),
            cgst_amount_out=F('cgst_total'),
            igst_amount_out=F('igst_total'),
            tax_total_amount_out=(
                F('sgst_total')+F('cgst_total')+F('igst_total'))
        ).values(
            'state_name_out',
            'taxable_amount_out',
            'tax_rate_out',
            'sgst_amount_out',
            'cgst_amount_out',
            'igst_amount_out',
            'tax_total_amount_out')

        rec_filter2 = CreditNoteStock.objects.filter(
            Q(
                Q(credit_note__nature_transactions_sales__exact=GSTRQueryProvider.other_state_sales_taxable_nature) &
                ~Q(credit_note__party_ac__state__state_name__exact=company.organisation.state.state_name) &
                Q(
                    Q(credit_note__sale_voucher__total__lte=250000.0) |
                    Q(
                        Q(credit_note__sales_invno__isnull=False) &
                        ~Q(credit_note__sales_invno__exact='') &
                        Q(credit_note__sales_amount__lte=250000.0)
                    )
                )
            ) |
            Q(
                Q(credit_note__nature_transactions_sales__in=GSTRQueryProvider.b2cs_same_state_tran_nature) &
                Q(credit_note__party_ac__state__state_name__exact=company.organisation.state.state_name)
            ),
            credit_note__company=company,
            credit_note__voucher_date__gte=period_selected.start_date,
            credit_note__voucher_date__lt=period_selected.end_date,
            credit_note__party_ac__gst_no__exact='',
            credit_note__party_ac__registration_type__in=GSTRQueryProvider.unregisted_party_types
        ).annotate(
            state_name_out=F('credit_note__party_ac__state__state_name'),
            taxable_amount_out=F('total') * -1,
            tax_rate_out=Case(When(cgst__gt=0, then=F(
                'cgst') + F('sgst')), default=(F('igst'))),
            sgst_amount_out=F('sgst_total') * -1,
            cgst_amount_out=F('cgst_total') * -1,
            igst_amount_out=F('igst_total') * -1,
            tax_total_amount_out=(
                F('sgst_total')+F('cgst_total')+F('igst_total')) * -1
        ).values(
            'state_name_out',
            'taxable_amount_out',
            'tax_rate_out',
            'sgst_amount_out',
            'cgst_amount_out',
            'igst_amount_out',
            'tax_total_amount_out')

        rec_filter = rec_filter1.union(rec_filter2, all=True).order_by(
            'state_name_out', 'tax_rate_out')
        # Aggrigate/Annotatation not supported on union set in Django
        # .values(
        #     'state_name_out',
        #     'tax_rate_out'
        # ).annotate(
        #     taxable_amount_result=Sum('taxable_amount_out'),
        #     sgst_amount_result=Sum('sgst_amount_out'),
        #     cgst_amount_result=Sum('cgst_amount_out'),
        #     igst_amount_result=Sum('igst_amount_out'),
        #     tax_total_amount_result=Sum('tax_total_amount_out'))

        # print(rec_filter.query)
        grouped_state_rate = itertools.groupby(
            rec_filter, key=lambda x: (x['state_name_out'], x['tax_rate_out']))
        result = []
        for group_key, group_values in grouped_state_rate:
            taxable_amount_grouped = Decimal(0.0)
            sgst_amount_grouped = Decimal(0.0)
            cgst_amount_grouped = Decimal(0.0)
            igst_amount_grouped = Decimal(0.0)
            tax_total_amount_grouped = Decimal(0.0)

            for each_group in group_values:
                taxable_amount_grouped += each_group['taxable_amount_out']
                sgst_amount_grouped += each_group['sgst_amount_out']
                cgst_amount_grouped += each_group['cgst_amount_out']
                igst_amount_grouped += each_group['igst_amount_out']
                tax_total_amount_grouped += each_group['tax_total_amount_out']

            result.append({
                'state_name_out': group_key[0],
                'tax_rate_out': group_key[1],
                'taxable_amount_out': taxable_amount_grouped,
                'sgst_amount_out': sgst_amount_grouped,
                'cgst_amount_out': cgst_amount_grouped,
                'igst_amount_out': igst_amount_grouped,
                'tax_total_amount_out': tax_total_amount_grouped
            })

        return result

    @staticmethod
    def get_b2cs_sale_query_set(company, period_selected):
        """
        Returns a query set for B2CS Sales
        """
       # B2CS
        # Supplies made to consumers and unregistered persons of the following nature
        # a) Intra-State: any value
        # b) Inter-State: Invoice value Rs 2.5 lakh or less
        # Conditions:
        # 1. GSTIN not present
        # 2. [Inter-State] Nature of transaction is "Interstate Sales Taxable" and Invoice value <= 2,50,000.00 and
        #    Company's state is not same as party's state
        # 3. [Intra-State] Nature of transaction in list of b2cs transaction nature
        return SaleVoucher.objects.filter(
            Q(
                Q(nature_transactions_sales__exact=GSTRQueryProvider.other_state_sales_taxable_nature) &
                ~Q(party_ac__state__state_name__exact=company.organisation.state.state_name) &
                Q(total__lte=250000.0)
            ) |
            Q(
                Q(nature_transactions_sales__in=GSTRQueryProvider.b2cs_same_state_tran_nature) &
                Q(party_ac__state__state_name__exact=company.organisation.state.state_name)
            ),
            company=company,
            voucher_date__gte=period_selected.start_date,
            voucher_date__lt=period_selected.end_date,
            party_ac__gst_no__exact='',
            party_ac__registration_type__in=GSTRQueryProvider.unregisted_party_types
        )

    @staticmethod
    def get_b2cs_return_query_set(company, period_selected):
        """
        Returns a query set for B2CS Returns
        """
        # B2CS
        # Supplies made to consumers and unregistered persons of the following nature
        # a) Intra-state.state_name: any value
        # b) Inter-State: Invoice value Rs 2.5 lakh or less
        # Conditions:
        # 1. GSTIN not present
        # 2. [Inter-State] Nature of transaction is "Interstate Sales Taxable" and Invoice value <= 2,50,000.00 and
        #    Company's state is not same as party's state
        # 3. [Intra-State] Nature of transaction in list of b2cs transaction nature
        return CreditNoteVoucher.objects.filter(
            Q(
                Q(nature_transactions_sales__exact=GSTRQueryProvider.other_state_sales_taxable_nature) &
                ~Q(party_ac__state__state_name__exact=company.organisation.state.state_name) &
                Q(
                    Q(sale_voucher__total__lte=250000.0) |
                    Q(
                        Q(sales_invno__isnull=False) &
                        ~Q(sales_invno__exact='') &
                        Q(sales_amount__lte=250000.0)
                    )
                )
            ) |
            Q(
                Q(nature_transactions_sales__in=GSTRQueryProvider.b2cs_same_state_tran_nature) &
                Q(party_ac__state__state_name__exact=company.organisation.state.state_name)
            ),
            company=company,
            voucher_date__gte=period_selected.start_date,
            voucher_date__lt=period_selected.end_date,
            party_ac__gst_no__exact='',
            party_ac__registration_type__in=GSTRQueryProvider.unregisted_party_types
        )

    @staticmethod
    def get_notes_reg_query_set(company, period_selected):
        """
        Returns a query set for Note to Registered (Sales Return)
        """
        # Credit Note Registered
        # Supplies return from registered persons of the following nature
        # Conditions:
        # 1. Nature of transaction in list of GSTRQueryProvider.notes_reg_tran_nature.
        # 2. GSTIN present in voucher
        return CreditNoteVoucher.objects.filter(
            Q(party_ac__registration_type__exact='Regular') | Q(
                party_ac__registration_type__exact='Composition'),
            company=company,
            voucher_date__gte=period_selected.start_date,
            voucher_date__lt=period_selected.end_date,
            nature_transactions_sales__in=GSTRQueryProvider.notes_reg_tran_nature,
        ).exclude(party_ac__gst_no__exact='')

    @staticmethod
    def get_notes_ureg_query_set(company, period_selected):
        """
        Returns a query set for Note to Unregistered (Sales Return)
        """
        # Credit Note Unregistered
        # Supplies return from consumers and unegistered persons of the following nature
        # Conditions:
        # a)The place of supply is outside the state where the supplier is registered and
        # b)The total invoice value is more that Rs 2,50,000 for Interstate transaction excluding export transactions
        # Conditions:
        # 1. GSTIN not present
        # 2. Nature of transaction is "Interstate Sales Taxable" or list of export transaction types
        # 3. Invoice value > 2,50,000.00 for inter state
        # 4. Company's state is not same as party's state
        return CreditNoteVoucher.objects.filter(
            Q(Q(nature_transactions_sales__exact=GSTRQueryProvider.other_state_sales_taxable_nature) & Q(total__gt=250000.0)) |
            Q(nature_transactions_sales__in=GSTRQueryProvider.notes_ureg_export_tran_nature),
            company=company,
            voucher_date__gte=period_selected.start_date,
            voucher_date__lt=period_selected.end_date,
            party_ac__gst_no__exact='',
            party_ac__registration_type__in=GSTRQueryProvider.unregisted_party_types
        ).exclude(party_ac__state__state_name__exact=company.organisation.state.state_name)

    @staticmethod
    def get_export_query_set(company, period_selected):
        """
        Returns a query set for Export
        """
        # Export
        # Exports supplies including supplies to SEZ/SEZ Developer or deemed exports
        # Conditions:
        # 1. Nature of transaction in list of export transaction nature
        # 2. GSTIN not present in voucher
        # 4. Party's state is "Other Territory"
        return SaleVoucher.objects.filter(
            company=company,
            voucher_date__gte=period_selected.start_date,
            voucher_date__lt=period_selected.end_date,
            nature_transactions_sales__in=GSTRQueryProvider.export_tran_nature,
            party_ac__gst_no__exact='',
            party_ac__registration_type__in=GSTRQueryProvider.unregisted_party_types,
            party_ac__state__state_name__exact='Other Territory'
        )

    @staticmethod
    def get_exempted_query_set(company, period_selected):
        """
        Returns a query set for Exempted / Nil Rated / Non-GST
        """
        # Nil Rated / Exempt / Non-GST
        # Details of Nil Rated, Exempted and Non GST Supplies made during the tax period
        # Conditions:
        # 1. Nature of transaction in list of nil_rated transaction nature
        return SaleVoucher.objects.filter(
            company=company,
            voucher_date__gte=period_selected.start_date,
            voucher_date__lt=period_selected.end_date,
            nature_transactions_sales__in=GSTRQueryProvider.nil_rated_tran_nature,
        )


class GSTR1View(ProductExistsRequiredMixin, TemplateView):
    """
    GSTR1View View
    """
    template_name = "gst_reports/gstr1.html"

    def get_context_data(self, **kwargs):
        context = super(GSTR1View, self).get_context_data(**kwargs)
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

        context['invoice_count'] = SaleVoucher.objects.filter(
            company=company,
            voucher_date__gte=period_selected.start_date,
            voucher_date__lt=period_selected.end_date).aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        GSTR1View.init_context_b2b(
            context=context,
            company=company,
            period_selected=period_selected)

        GSTR1View.init_context_b2cl(
            context=context,
            company=company,
            period_selected=period_selected)

        GSTR1View.init_context_b2cs(
            context=context,
            company=company,
            period_selected=period_selected)

        GSTR1View.init_context_note_registered(
            context=context,
            company=company,
            period_selected=period_selected)

        GSTR1View.init_context_note_unregistered(
            context=context,
            company=company,
            period_selected=period_selected)

        GSTR1View.init_context_export(
            context=context,
            company=company,
            period_selected=period_selected)

        GSTR1View.init_context_exempted(
            context=context,
            company=company,
            period_selected=period_selected)

        context['taxable_total'] = context['b2b_taxable'] + context['b2cl_taxable'] + context['b2cs_taxable'] + \
            context['notes_reg_taxable'] + context['notes_ureg_taxable'] + \
            context['export_taxable'] + context['nil_rated_taxable']
        context['cgst_total'] = context['b2b_cgst_total'] + \
            context['b2cs_cgst_total'] + context['notes_reg_cgst_total']
        context['sgst_total'] = context['b2b_sgst_total'] + \
            context['b2cs_sgst_total'] + context['notes_reg_sgst_total']
        context['igst_total'] = context['b2b_igst_total'] + context['b2cl_igst_total'] + context['b2cs_igst_total'] + \
            context['notes_reg_igst_total'] + \
            context['notes_ureg_igst_total'] + context['export_igst_total']
        context['tax_total'] = context['b2b_tax_total'] + context['b2cl_tax_total'] + context['b2cs_tax_total'] + \
            context['notes_reg_tax_total'] + \
            context['notes_ureg_tax_total'] + context['export_tax_total']
        context['invoice_total'] = context['b2b_invoice_total'] + context['b2cl_invoice_total'] + context['b2cs_invoice_total'] + \
            context['notes_reg_invoice_total'] + context['notes_ureg_invoice_total'] + \
            context['export_invoice_total'] + \
            context['exempted_invoice_total']

        return context

    @staticmethod
    def init_context_b2b(context, company, period_selected):
        """
        Initializes B2B Summary in the context parameter
        """
        b2b_filter = GSTRQueryProvider.get_b2b_query_set(
            company=company, period_selected=period_selected)

        context['b2b_count'] = b2b_filter.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['b2b_taxable'] = b2b_filter.aggregate(
            the_sum=Coalesce(Sum('sub_total'), Value(0)))['the_sum']
        context['b2b_cgst_total'] = b2b_filter.aggregate(
            the_sum=Coalesce(Sum('cgst_total'), Value(0)))['the_sum']
        context['b2b_sgst_total'] = b2b_filter.aggregate(
            the_sum=Coalesce(Sum('sgst_total'), Value(0)))['the_sum']
        context['b2b_igst_total'] = b2b_filter.aggregate(
            the_sum=Coalesce(Sum('igst_total'), Value(0)))['the_sum']
        context['b2b_tax_total'] = context['b2b_cgst_total'] + \
            context['b2b_sgst_total'] + context['b2b_igst_total']
        context['b2b_invoice_total'] = b2b_filter.aggregate(
            the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']

    @staticmethod
    def init_context_b2cl(context, company, period_selected):
        """
        Initializes B2CS Summary in the context parameter
        """
        b2cl_filter = GSTRQueryProvider.get_b2cl_query_set(
            company=company, period_selected=period_selected)

        context['b2cl_count'] = b2cl_filter.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        context['b2cl_taxable'] = b2cl_filter.aggregate(
            the_sum=Coalesce(Sum('sub_total'), Value(0)))['the_sum']

        context['b2cl_igst_total'] = b2cl_filter.aggregate(
            the_sum=Coalesce(Sum('igst_total'), Value(0)))['the_sum']

        context['b2cl_tax_total'] = context['b2cl_igst_total']

        context['b2cl_invoice_total'] = b2cl_filter.aggregate(
            the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']

    @staticmethod
    def init_context_b2cs(context, company, period_selected):
        """
        Initializes B2CS Summary in the context parameter
        """
        b2cs_sale_filter = GSTRQueryProvider.get_b2cs_sale_query_set(
            company=company, period_selected=period_selected)

        b2cs_return_filter = GSTRQueryProvider.get_b2cs_return_query_set(
            company=company, period_selected=period_selected)

        context['b2cs_count'] = b2cs_sale_filter.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        context['b2cs_count'] += b2cs_return_filter.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        context['b2cs_taxable'] = b2cs_sale_filter.aggregate(
            the_sum=Coalesce(Sum('sub_total'), Value(0)))['the_sum']

        context['b2cs_taxable'] -= b2cs_return_filter.aggregate(
            the_sum=Coalesce(Sum('sub_total'), Value(0)))['the_sum']

        context['b2cs_cgst_total'] = b2cs_sale_filter.aggregate(
            the_sum=Coalesce(Sum('cgst_total'), Value(0)))['the_sum']

        context['b2cs_cgst_total'] -= b2cs_return_filter.aggregate(
            the_sum=Coalesce(Sum('cgst_total'), Value(0)))['the_sum']

        context['b2cs_sgst_total'] = b2cs_sale_filter.aggregate(
            the_sum=Coalesce(Sum('sgst_total'), Value(0)))['the_sum']

        context['b2cs_sgst_total'] -= b2cs_return_filter.aggregate(
            the_sum=Coalesce(Sum('sgst_total'), Value(0)))['the_sum']

        context['b2cs_igst_total'] = b2cs_sale_filter.aggregate(
            the_sum=Coalesce(Sum('igst_total'), Value(0)))['the_sum']

        context['b2cs_igst_total'] -= b2cs_return_filter.aggregate(
            the_sum=Coalesce(Sum('igst_total'), Value(0)))['the_sum']

        context['b2cs_tax_total'] = context['b2cs_cgst_total'] + \
            context['b2cs_sgst_total'] + context['b2cs_igst_total']

        context['b2cs_invoice_total'] = b2cs_sale_filter.aggregate(
            the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']

        context['b2cs_invoice_total'] -= b2cs_return_filter.aggregate(
            the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']

    @staticmethod
    def init_context_note_registered(context, company, period_selected):
        """
        Initializes Note (Debit / Credit) to Registered Summary in the context parameter
        """
        notes_reg_filter = GSTRQueryProvider.get_notes_reg_query_set(
            company=company, period_selected=period_selected)

        context['notes_reg_count'] = notes_reg_filter.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        context['notes_reg_taxable'] = notes_reg_filter.aggregate(
            the_sum=Coalesce(Sum('sub_total'), Value(0)))['the_sum'] * -1

        context['notes_reg_cgst_total'] = notes_reg_filter.aggregate(
            the_sum=Coalesce(Sum('cgst_total'), Value(0)))['the_sum'] * -1

        context['notes_reg_sgst_total'] = notes_reg_filter.aggregate(
            the_sum=Coalesce(Sum('sgst_total'), Value(0)))['the_sum'] * -1

        context['notes_reg_igst_total'] = notes_reg_filter.aggregate(
            the_sum=Coalesce(Sum('igst_total'), Value(0)))['the_sum'] * -1

        context['notes_reg_tax_total'] = context['notes_reg_cgst_total'] + \
            context['notes_reg_sgst_total'] + context['notes_reg_igst_total']

        context['notes_reg_invoice_total'] = notes_reg_filter.aggregate(
            the_sum=Coalesce(Sum('total'), Value(0)))['the_sum'] * -1

    @staticmethod
    def init_context_note_unregistered(context, company, period_selected):
        """
        Initializes Note (Debit / Credit) to Unegistered Summary in the context parameter
        """
        notes_ureg_filter = GSTRQueryProvider.get_notes_ureg_query_set(
            company=company, period_selected=period_selected)

        context['notes_ureg_count'] = notes_ureg_filter.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        context['notes_ureg_taxable'] = notes_ureg_filter.aggregate(
            the_sum=Coalesce(Sum('sub_total'), Value(0)))['the_sum'] * -1

        context['notes_ureg_igst_total'] = notes_ureg_filter.aggregate(
            the_sum=Coalesce(Sum('igst_total'), Value(0)))['the_sum'] * -1

        context['notes_ureg_tax_total'] = context['notes_ureg_igst_total']

        context['notes_ureg_invoice_total'] = notes_ureg_filter.aggregate(
            the_sum=Coalesce(Sum('total'), Value(0)))['the_sum'] * -1

    @staticmethod
    def init_context_export(context, company, period_selected):
        """
        Initializes Export Summary in the context parameter
        """
        export_filter = GSTRQueryProvider.get_export_query_set(
            company=company, period_selected=period_selected)

        context['export_count'] = export_filter.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        context['export_taxable'] = export_filter.aggregate(
            the_sum=Coalesce(Sum('sub_total'), Value(0)))['the_sum']

        context['export_igst_total'] = export_filter.aggregate(
            the_sum=Coalesce(Sum('igst_total'), Value(0)))['the_sum']

        context['export_tax_total'] = context['export_igst_total']

        context['export_invoice_total'] = export_filter.aggregate(
            the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']

    @staticmethod
    def init_context_exempted(context, company, period_selected):
        """
        Initializes Nil Rated Summary in the context parameter
        """
        exempt_filter = GSTRQueryProvider.get_exempted_query_set(
            company=company, period_selected=period_selected)

        context['nil_rated_count'] = exempt_filter.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        context['nil_rated_taxable'] = exempt_filter.aggregate(
            the_sum=Coalesce(Sum('sub_total'), Value(0)))['the_sum']

        context['exempted_invoice_total'] = exempt_filter.aggregate(
            the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']


class GSTRInvoiceListView(ProductExistsRequiredMixin, ListView):
    """
    Displays a list of GST Invoices based on GST Summary
    """
    #model = LedgerGroup
    paginate_by = 25

    def __init__(self):
        # instance variables
        self.gst_type_display = "Unknown"
        self.Company = None
        self.PeriodSelected = None

    def get_template_names(self):
        """
        Template used to dispaly list
        """
        return ['gst_reports/gst_invoice_list.html']

    def get_queryset(self):
        """
        Returns custom queryset for the view based on request arguments
        """
        gst_type = self.kwargs['gst_type']
        self.Company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        self.PeriodSelected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])

        if gst_type == "b2b":
            self.gst_type_display = "B2B Invoices - 4A, 4B, 4C, 6B, 6C"
            invoice_filter = GSTRQueryProvider.get_b2b_query_set(
                company=self.Company,
                period_selected=self.PeriodSelected)
        elif gst_type == "b2cl":
            self.gst_type_display = "B2C Large Invoices - 5A, 5B"
            invoice_filter = GSTRQueryProvider.get_b2cl_query_set(
                company=self.Company,
                period_selected=self.PeriodSelected)
        elif gst_type == "b2cs":
            self.gst_type_display = "B2C Small Invoices - 7"
            invoice_filter = GSTRQueryProvider.get_b2cs_summary_query_set(
                company=self.Company,
                period_selected=self.PeriodSelected)
            # print("-----------------------------B2CS---------------------------------------")
            # print(invoice_filter[0])
            # print("------------------------------------------------------------------------")
        elif gst_type == "noter":
            self.gst_type_display = "Credit/Debit notes (Registered) - 9B"
            invoice_filter = GSTRQueryProvider.get_notes_reg_query_set(
                company=self.Company,
                period_selected=self.PeriodSelected)
        elif gst_type == "noteu":
            self.gst_type_display = "Credit/Debit notes (Unregistered) - 9B"
            invoice_filter = GSTRQueryProvider.get_notes_ureg_query_set(
                company=self.Company,
                period_selected=self.PeriodSelected)
        elif gst_type == "expt":
            self.gst_type_display = "Export Invoices - 6A"
            invoice_filter = GSTRQueryProvider.get_export_query_set(
                company=self.Company,
                period_selected=self.PeriodSelected)
        # elif gst_type == "nilr":
        #     self.gst_type_display = "Nil Rated Invoices - 8A, 8B, 8C, 8D"
        #     invoice_filter = GSTRQueryProvider.get_exempted_query_set(
        #         company=self.Company,
        #         period_selected=self.PeriodSelected)
        else:
            raise Http404

        return invoice_filter

        # return LedgerGroup.objects.filter(company=self.kwargs['company_pk']).exclude(group_Name__iexact='Primary')

    def get_context_data(self, **kwargs):
        context = super(GSTRInvoiceListView, self).get_context_data(**kwargs)

        context['company'] = self.Company
        context['period_selected'] = self.PeriodSelected

        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['gst_type'] = self.kwargs['gst_type']
        context['gst_type_display'] = self.gst_type_display

        return context


class GSTR2AView(ProductExistsRequiredMixin, TemplateView):
    """
    GSTR2AView View
    """
    template_name = "gst_reports/gstr_2A.html"

    def get_context_data(self, **kwargs):
        """
        get_context_data
        """
        context = super(GSTR2AView, self).get_context_data(**kwargs)
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


class GSTR3BView(ProductExistsRequiredMixin, TemplateView):
    """
    GSTR3BView View
    """
    template_name = "gst_reports/gstr_3B.html"

    def get_context_data(self, **kwargs):
        """
        get_context_data
        """
        context = super(GSTR3BView, self).get_context_data(**kwargs)
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
