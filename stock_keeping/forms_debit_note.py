"""
Forms
"""
import datetime
from django import forms
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from accounting_entry.models import LedgerMaster
from bracketline.forms import DateInput
from .models import StockItem
from .models_purchase import PurchaseVoucher
from .models_debit_note import DebitNoteVoucher, DebitNoteStock, DebitNoteTerm, DebitNoteTax


class DebitNoteForm(forms.ModelForm):
    """
    Debit Note Form
    """
    class Meta:
        model = DebitNoteVoucher
        fields = ('nature_transactions_purchase', 'voucher_date', 'purchase_date', 'purchase_invno', 'purchase_voucher', 'purchase_amount', 'supply_place',
                  'supplier_ref', 'mode', 'ref_no', 'party_ac', 'doc_ledger', 'gst_details', 'issue_reason', 'despatch_no', 'despatch_info',
                  'note_no', 'date_after_no', 'bill_no', 'bill_date', 'port_code', 'destination', 'landing_bill', 'landing_date', 'vechicle_no',
                  'shipper_place', 'flight_no', 'loading_port', 'discharge_port', 'supply_country','manual')
        widgets = {
            'voucher_date': DateInput(),
            'purchase_date': DateInput(),
            'date_after_no': DateInput(),
            'bill_date': DateInput(),
            'landing_date': DateInput(),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.company = kwargs.pop('company', None)
        super(DebitNoteForm, self).__init__(*args, **kwargs)

        self.fields['voucher_date'].widget.attrs = {'class': 'form-control', }
        self.fields['purchase_voucher'].queryset = PurchaseVoucher.objects.filter(
            company=self.company)
        self.fields['purchase_voucher'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }
        self.fields['party_ac'].queryset = LedgerMaster.objects.filter(
            Q(company=self.company),
            Q(ledger_group__group_base__name__exact='Sundry Debtors') |
            Q(ledger_group__group_base__name__exact='Bank Accounts') |
            Q(ledger_group__group_base__name__exact='Cash-in-Hand') |
            Q(ledger_group__group_base__name__exact='Sundry Creditors'))
        self.fields['party_ac'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }
        self.fields['doc_ledger'].queryset = LedgerMaster.objects.filter(
            Q(company=self.company),
            Q(ledger_group__group_base__name__exact='Purchase Accounts'))
        self.fields['doc_ledger'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }
        self.fields['nature_transactions_purchase'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'onchange': 'import_change(this)', }
        self.fields['purchase_invno'].widget.attrs = {
            'class': 'form-control', }
        self.fields['purchase_date'].widget.attrs = {'class': 'form-control', }
        self.fields['purchase_amount'].widget.attrs = {
            'class': 'form-control', }
        self.fields['supply_place'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }
        self.fields['supplier_ref'].widget.attrs = {'class': 'form-control', }
        self.fields['mode'].widget.attrs = {'class': 'form-control', }
        self.fields['ref_no'].widget.attrs = {'class': 'form-control', }
        self.fields['gst_details'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'onchange': 'gst_change(this)', }
        self.fields['manual'].widget.attrs = {
                'class': 'select2_demo_2 form-control', 'onchange': 'purchase_change(this)', }
        self.fields['issue_reason'].widget.attrs = {'class': 'form-control', }
        self.fields['note_no'].widget.attrs = {'class': 'form-control', }
        self.fields['date_after_no'].widget.attrs = {'class': 'form-control', }
        self.fields['bill_no'].widget.attrs = {'class': 'form-control', }
        self.fields['bill_no'].widget.attrs['disabled'] = True
        self.fields['bill_date'].widget.attrs = {'class': 'form-control', }
        self.fields['bill_date'].widget.attrs['disabled'] = True
        self.fields['bill_date'].initial = datetime.date.today
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
        nature_transactions_purchase = self.cleaned_data['nature_transactions_purchase']
        supply_place = self.cleaned_data['supply_place']

        if self.company.organisation.state == supply_place and nature_transactions_purchase == 'Interstate Purchase  - Taxable':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state == supply_place and nature_transactions_purchase == 'Imports Exempt':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state == supply_place and nature_transactions_purchase == 'Imports Nil Rated':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state == supply_place and nature_transactions_purchase == 'Imports Taxable':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state == supply_place and nature_transactions_purchase == 'Interstate Purchase exempt':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state == supply_place and nature_transactions_purchase == 'Interstate Purchase from Unregistered Dealer - Exempt':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state == supply_place and nature_transactions_purchase == 'Interstate Purchase from Unregistered Dealer - Nil Rated':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state == supply_place and nature_transactions_purchase == 'Interstate Purchase from Unregistered Dealer - Taxable':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state == supply_place and nature_transactions_purchase == 'Interstate Purchase  - Nil Rated':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state == supply_place and nature_transactions_purchase == 'Purchase Deemed Exports - Exempt':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state == supply_place and nature_transactions_purchase == 'Purchase Deemed Exports - Nil Rated':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state == supply_place and nature_transactions_purchase == 'Purchase Deemed Exports - Taxable':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state != supply_place and nature_transactions_purchase == 'Intrastate Purchase Deemed Exports - Exempt':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state != supply_place and nature_transactions_purchase == 'Intrastate Purchase Deemed Exports - Nil Rated':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state != supply_place and nature_transactions_purchase == 'Intrastate Purchase Deemed Exports - Taxable':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state != supply_place and nature_transactions_purchase == 'Purchase Exempt':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state != supply_place and nature_transactions_purchase == 'Purchase From Unregister Dealer - Exempt':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state != supply_place and nature_transactions_purchase == 'Purchase From Unregister Dealer - Nil Rated':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state != supply_place and nature_transactions_purchase == 'Purchase From Unregister Dealer - Taxable':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state != supply_place and nature_transactions_purchase == 'Purchase Nil Rated':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state != supply_place and nature_transactions_purchase == 'Intrastate Purchase Taxable':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        return supply_place


class DebitNoteStockForm(forms.ModelForm):
    """
    Debit Note Stock Form
    """
    class Meta:
        model = DebitNoteStock
        fields = ('stock_item', 'quantity', 'rate', 'disc', 'total')

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super(DebitNoteStockForm, self).__init__(*args, **kwargs)
        self.fields['stock_item'].queryset = StockItem.objects.filter(
            company=self.company)
        self.fields['stock_item'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }
        self.fields['quantity'].widget.attrs = {'class': 'form-control', 'onchange': 'calcProductTotal(this)'}
        self.fields['rate'].widget.attrs = {
            'class': 'form-control', 'onchange': 'calcProductTotal(this)','step': 'any'}
        self.fields['disc'].widget.attrs = {'class': 'form-control', 'onchange': 'calcProductTotal(this)'}
        self.fields['total'].widget.attrs = {
            'class': 'form-control','onchange': 'calcProductRate(this)', 'step': 'any'}


DEBIT_NOTE_STOCK_FORM_SET = inlineformset_factory(
    DebitNoteVoucher, DebitNoteStock, form=DebitNoteStockForm, extra=3)


class DebitNoteTermForm(forms.ModelForm):
    """
    Debit Note Term Form
    """
    class Meta:
        model = DebitNoteTerm
        fields = ('ledger', 'rate', 'total')

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super(DebitNoteTermForm, self).__init__(*args, **kwargs)

        self.fields['ledger'].queryset = LedgerMaster.objects.filter(
            Q(company=self.company),
            Q(ledger_group__group_base__is_revenue__exact='Yes'))
        self.fields['ledger'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }
        self.fields['rate'].widget.attrs = {
            'class': 'form-control', 'step': 'any'}
        self.fields['total'].widget.attrs = {
            'class': 'form-control', 'step': 'any'}


DEBIT_NOTE_TERM_FORM_SET = inlineformset_factory(
    DebitNoteVoucher, DebitNoteTerm, form=DebitNoteTermForm, extra=3)


class DebitNoteTaxForm(forms.ModelForm):
    """
    Debit Note Tax Form
    """
    class Meta:
        model = DebitNoteTax
        fields = ('ledger', 'total')

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super(DebitNoteTaxForm, self).__init__(*args, **kwargs)
        self.fields['ledger'].queryset = LedgerMaster.objects.filter(
            Q(company=self.company), Q(ledger_group__group_base__name__exact='Duties & Taxes'))
        self.fields['ledger'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }
        self.fields['total'].widget.attrs = {
            'class': 'form-control', 'step': 'any'}


DEBIT_NOTE_TAX_FORM_SET = inlineformset_factory(
    DebitNoteVoucher, DebitNoteTax, form=DebitNoteTaxForm, extra=3)
