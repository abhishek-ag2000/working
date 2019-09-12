"""
Forms
"""
from django import forms
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from accounting_entry.models import LedgerMaster
from bracketline.forms import DateInput
from .models import StockItem
from .models_sale import SaleVoucher
from .models_credit_note import CreditNoteVoucher, CreditNoteStock, CreditNoteTerm, CreditNoteTax


class CreditNoteForm(forms.ModelForm):
    """
    Credit Note Form
    """
    class Meta:
        model = CreditNoteVoucher
        fields = ('nature_transactions_sales', 'voucher_date', 'sales_date', 'sales_invno', 'sales_amount', 'manual', 'sale_voucher',
                  'supply_place', 'delivery_note', 'supplier_ref', 'mode', 'ref_no', 'party_ac', 'doc_ledger', 'despatch_no', 'despatch_info',
                  'gst_details', 'issue_reason', 'note_no', 'date_after_no', 'bill_no', 'bill_date', 'port_code','destination','landing_bill',
                  'landing_date','vechicle_no','shipper_place','flight_no','loading_port','discharge_port','supply_country')
        widgets = {
            'voucher_date': DateInput(),
            'bill_date': DateInput(),
            'date_after_no': DateInput(),
            'date_entry': DateInput(),
            'sales_date' : DateInput(),
            'landing_date' : DateInput(),
        }

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super(CreditNoteForm, self).__init__(*args, **kwargs)

        self.fields['voucher_date'].widget.attrs = {'class': 'form-control', }
        self.fields['ref_no'].widget.attrs = {'class': 'form-control', }
        self.fields['sale_voucher'].queryset = SaleVoucher.objects.filter(
            company=self.company)
        self.fields['sale_voucher'].widget.attrs = {'class': 'form-control', }
        self.fields['party_ac'].queryset = LedgerMaster.objects.filter(
            Q(company=self.company),
            Q(ledger_group__group_base__name__exact='Sundry Debtors') |
            Q(ledger_group__group_base__name__exact='Bank Accounts') |
            Q(ledger_group__group_base__name__exact='Cash-in-Hand'))
        self.fields['party_ac'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }
        self.fields['doc_ledger'].queryset = LedgerMaster.objects.filter(
            Q(company=self.company),
            Q(ledger_group__group_base__name__exact='Sales Accounts'))
        self.fields['doc_ledger'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }
        self.fields['nature_transactions_sales'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'onchange': 'import_change(this)', }
        self.fields['sales_invno'].widget.attrs = {'class': 'form-control', }
        self.fields['sales_date'].widget.attrs = {'class': 'form-control', }
        self.fields['sales_amount'].widget.attrs = {'class': 'form-control', }
        self.fields['manual'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'onchange': 'sales_change(this)', }
        self.fields['supply_place'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }
        self.fields['delivery_note'].widget.attrs = {'class': 'form-control', }
        self.fields['supplier_ref'].widget.attrs = {'class': 'form-control', }
        self.fields['mode'].widget.attrs = {'class': 'form-control', }
        self.fields['gst_details'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'onchange': 'gst_change(this)', }
        self.fields['issue_reason'].widget.attrs = {'class': 'form-control', }
        self.fields['note_no'].widget.attrs = {'class': 'form-control', }
        self.fields['date_after_no'].widget.attrs = {'class': 'form-control', }
        self.fields['bill_no'].widget.attrs = {'class': 'form-control', }
        self.fields['bill_no'].widget.attrs['disabled'] = True
        self.fields['bill_date'].widget.attrs = {'class': 'form-control', }
        self.fields['bill_date'].widget.attrs['disabled'] = True
        self.fields['port_code'].widget.attrs = {'class': 'form-control', }
        self.fields['port_code'].widget.attrs['disabled'] = True
        self.fields['despatch_no'].widget.attrs = {'class': 'form-control', }
        self.fields['despatch_info'].widget.attrs = {'class': 'form-control', }
        self.fields['destination'].widget.attrs = {'class': 'form-control', }
        self.fields['landing_bill'].widget.attrs = {'class': 'form-control', }
        self.fields['landing_date'].widget.attrs = {'class': 'form-control', }
        self.fields['vechicle_no'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }
        self.fields['shipper_place'].widget.attrs = {'class': 'form-control', }
        self.fields['flight_no'].widget.attrs = {'class': 'form-control', }
        self.fields['loading_port'].widget.attrs = {'class': 'form-control', }
        self.fields['discharge_port'].widget.attrs = {
            'class': 'form-control', }
        self.fields['supply_country'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }

    def clean_supply_place(self):
        """
        Clean Method to raise Validatiom Error if Place of Supply do not match with Nature of Transaction provided.
        """
        nature_transactions_sales = self.cleaned_data['nature_transactions_sales']
        supply_place = self.cleaned_data['supply_place']

        if self.company.organisation.state == supply_place and nature_transactions_sales == 'Interstate Sales   - Taxable':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state == supply_place and nature_transactions_sales == 'Deemed Exports Exempt':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state == supply_place and nature_transactions_sales == 'Deemed Exports Nil Rated':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state == supply_place and nature_transactions_sales == 'Deemed Exports Taxable':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state == supply_place and nature_transactions_sales == 'Exports Exempt':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state == supply_place and nature_transactions_sales == 'Exports LUT/Bond':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state == supply_place and nature_transactions_sales == 'Exports Nil Rated':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state == supply_place and nature_transactions_sales == 'Exports Taxable':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state == supply_place and nature_transactions_sales == 'Interstate Sales Exempt':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state == supply_place and nature_transactions_sales == 'Interstate Sales Nil Rated':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state == supply_place and nature_transactions_sales == 'Interstate Sales to Embassy / UN Body Exempt':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state == supply_place and nature_transactions_sales == 'Interstate Sales to Embassy / UN Body Nil Rated':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state == supply_place and nature_transactions_sales == 'Interstate Sales to Embassy / UN Body Taxable':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state != supply_place and nature_transactions_sales == 'Intrastate Deemed Exports Exempt':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state != supply_place and nature_transactions_sales == 'Intrastate Deemed Exports Nil Rated':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state != supply_place and nature_transactions_sales == 'Intrastate Deemed Exports Taxable':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state != supply_place and nature_transactions_sales == 'Sales Exempt':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state != supply_place and nature_transactions_sales == 'Sales Nil Rated':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state != supply_place and nature_transactions_sales == 'Intrastate Sales Taxable':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state != supply_place and nature_transactions_sales == 'sales to Consumer - Exempt':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state != supply_place and nature_transactions_sales == 'sales to Consumer - Nil Rated':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state != supply_place and nature_transactions_sales == 'sales to Consumer - Taxable':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        return supply_place

    def clean_ref_no(self):
        """
        Clean function to raise Validation Error if Invoice Number already exist in a company.
        """
        ref_no = self.cleaned_data['ref_no']
        master_id = 0

        if self.instance:
            # master id is used to exclude current master so that it is not checked as duplicate
            master_id = self.instance.id

        if CreditNoteVoucher.objects.filter(company=self.company, ref_no__iexact=ref_no).exclude(id=master_id).exists():
            raise forms.ValidationError("This Invoice Number already exists")
        return ref_no


class CreditNoteStockForm(forms.ModelForm):
    """
    Credit Note Stock Form
    """
    class Meta:
        model = CreditNoteStock
        fields = ('stock_item', 'quantity', 'rate', 'disc', 'total')

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super(CreditNoteStockForm, self).__init__(*args, **kwargs)

        self.fields['stock_item'].queryset = StockItem.objects.filter(
            company=self.company)
        self.fields['stock_item'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'onchange': 'stock_based_value(this)'}
        self.fields['quantity'].widget.attrs = {'class': 'form-control', 'onchange': 'calcProductTotal(this)'}
        self.fields['rate'].widget.attrs = {
            'class': 'form-control', 'onchange': 'calcProductTotal(this)','step': 'any'}
        self.fields['disc'].widget.attrs = {'class': 'form-control','step': 'any', 'onchange': 'calcProductTotal(this)'}
        self.fields['total'].widget.attrs = {
            'class': 'form-control', 'onchange': 'calcProductRate(this)','step': 'any'}


CREDIT_NOTE_STOCK_FORM_SET = inlineformset_factory(CreditNoteVoucher, CreditNoteStock, form=CreditNoteStockForm, extra=3)


class CreditNoteTermForm(forms.ModelForm):
    """
    Credit Note Term Form
    """
    class Meta:
        model = CreditNoteTerm
        fields = ('ledger', 'rate', 'total')

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super(CreditNoteTermForm, self).__init__(*args, **kwargs)

        self.fields['ledger'].queryset = LedgerMaster.objects.filter(
            Q(company=self.company),
            Q(ledger_group__group_base__is_revenue__exact='Yes'))
        self.fields['ledger'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'onchange': 'additional_ledger_value(this)'}
        self.fields['rate'].widget.attrs = {
            'class': 'form-control', 'step': 'any','onchange': 'additional_ledger_changed_rate(this)',}
        self.fields['total'].widget.attrs = {
            'class': 'form-control', 'step': 'any'}


CREDIT_NOTE_TERM_FORM_SET = inlineformset_factory(CreditNoteVoucher, CreditNoteTerm, form=CreditNoteTermForm, extra=3)


class CreditNoteTaxForm(forms.ModelForm):
    """
    Credit Note Tax Form
    """
    class Meta:
        model = CreditNoteTax
        fields = ('ledger', 'total')

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super(CreditNoteTaxForm, self).__init__(*args, **kwargs)

        self.fields['ledger'].queryset = LedgerMaster.objects.filter(
            Q(company=self.company),
            Q(ledger_group__group_base__name__exact='Duties & Taxes'))
        self.fields['ledger'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'onchange': 'additional_gst_value(this)',}
        self.fields['total'].widget.attrs = {
            'class': 'form-control', 'step': 'any'}


CREDIT_NOTE_TAX_FORM_SET = inlineformset_factory(CreditNoteVoucher, CreditNoteTax, form=CreditNoteTaxForm, extra=3)
