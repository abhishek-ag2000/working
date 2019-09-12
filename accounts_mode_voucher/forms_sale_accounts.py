"""
Forms
"""
from django import forms
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from accounting_entry.models import LedgerMaster
from bracketline.forms import DateInput
from .models_sale_accounts import SaleVoucherAccounts, SaleTermAccounts, SaleTaxAccounts


class SaleAccountsForm(forms.ModelForm):
    """
    Sales Form
    """
    class Meta:
        model = SaleVoucherAccounts
        fields = ('nature_transactions_sales', 'voucher_date', 'consignee_name', 'consignee_address', 'consignee_gstin', 'consignee_pan', 'consignee_pan',
                  'consignee_contact', 'consignee_state', 'other_details', 'consignee_country', 'despatch_no', 'despatch_info', 'destination',
                  'landing_bill', 'landing_date', 'vechicle_no', 'supply_place', 'supplier_ref', 'ref_no', 'party_ac',
                  'gst_details', 'bill_no', 'bill_date', 'port_code', 'delivery_terms', 'shipper_place', 'flight_no',
                  'loading_port', 'discharge_port', 'supply_country')
        widgets = {
            'voucher_date': DateInput(),
            'bill_date': DateInput(),
            'landing_date': DateInput(),
        }

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super(SaleAccountsForm, self).__init__(*args, **kwargs)

        self.fields['voucher_date'].widget.attrs = {'class': 'form-control', }
        self.fields['ref_no'].widget.attrs = {'class': 'form-control', }
        self.fields['consignee_name'].widget.attrs = {
            'class': 'form-control', }
        self.fields['consignee_address'].widget.attrs = {'class': 'form-control', }
        self.fields['consignee_pan'].widget.attrs = {'class': 'form-control', }
        self.fields['consignee_gstin'].widget.attrs = {'class': 'form-control', }
        self.fields['consignee_pan'].widget.attrs['disabled'] = True
        self.fields['consignee_gstin'].widget.attrs['disabled'] = True
        self.fields['consignee_contact'].widget.attrs = {
            'class': 'form-control', }
        self.fields['consignee_country'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'onchange': 'country_details_value(this)', }
        self.fields['other_details'].widget.attrs = {'class': 'form-control', }
        self.fields['other_details'].widget.attrs['disabled'] = True
        self.fields['party_ac'].queryset = LedgerMaster.objects.filter(
            Q(company=self.company),
            Q(ledger_group__group_base__name__exact='Bank Accounts') |
            Q(ledger_group__group_base__name__exact='Sundry Debtors') |
            Q(ledger_group__group_base__name__exact='Cash-in-Hand'))
        self.fields['party_ac'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }
        self.fields['nature_transactions_sales'].widget.attrs = {
            'class': 'select2_demo_2 form-control col-lg-8', 'onchange': 'gst_change(this)', }
        self.fields['supply_place'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }
        self.fields['supply_place'].initial = self.company.organisation.state.id
        self.fields['consignee_state'].widget.attrs = {'class': 'form-control', }
        self.fields['consignee_state'].widget.attrs['disabled'] = True
        self.fields['consignee_state'].initial = self.company.organisation.state.id
        self.fields['supplier_ref'].widget.attrs = {'class': 'form-control', }
        self.fields['gst_details'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'onchange': 'gst_details_value(this)', }
        self.fields['bill_no'].widget.attrs = {'class': 'form-control', }
        self.fields['bill_date'].widget.attrs = {'class': 'form-control', }
        self.fields['port_code'].widget.attrs = {'class': 'form-control', }
        self.fields['port_code'].widget.attrs['disabled'] = True
        self.fields['despatch_no'].widget.attrs = {'class': 'form-control', }
        self.fields['despatch_info'].widget.attrs = {'class': 'form-control', }
        self.fields['destination'].widget.attrs = {'class': 'form-control', }
        self.fields['landing_bill'].widget.attrs = {'class': 'form-control', }
        self.fields['landing_date'].widget.attrs = {'class': 'form-control', }
        self.fields['vechicle_no'].widget.attrs = {'class': 'form-control', }
        self.fields['delivery_terms'].widget.attrs = {
            'class': 'form-control', }
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

        if self.company.organisation.state == supply_place and nature_transactions_sales == 'Interstate Sales - Taxable':
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
        if self.company.organisation.state != supply_place and nature_transactions_sales == 'Sales to Consumer - Exempt':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state != supply_place and nature_transactions_sales == 'Sales to Consumer - Nil Rated':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state != supply_place and nature_transactions_sales == 'Sales to Consumer - Taxable':
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

        if SaleVoucherAccounts.objects.filter(company=self.company, ref_no__iexact=ref_no).exclude(id=master_id).exists():
            raise forms.ValidationError("This Invoice Number already exists")
        return ref_no


class SaleTermAccountsForm(forms.ModelForm):
    """
    Sale Term Form
    """
    class Meta:
        model = SaleTermAccounts
        fields = ('ledger', 'total')

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super(SaleTermAccountsForm, self).__init__(*args, **kwargs)

        self.fields['ledger'].queryset = LedgerMaster.objects.filter(
            Q(company=self.company),
            Q(ledger_group__group_base__name__exact='Sales Accounts') |
            Q(ledger_group__group_base__name__exact='Direct Incomes') |
            Q(ledger_group__group_base__name__exact='Indirect Incomes') |
            Q(ledger_group__group_base__name__exact='Indirect Expenses') |
            Q(ledger_group__group_base__name__exact='Direct Expenses'))
        self.fields['ledger'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'onchange': 'additional_ledger_value(this)'}
        self.fields['total'].widget.attrs = {
            'class': 'form-control', 'step': 'any'}

    def clean_ledger(self):
        ledger = self.cleaned_data['ledger']
        if not ledger:
            raise forms.ValidationError("Ledger must be selected")
        return ledger



class SaleTermAccountsFormSet(forms.BaseInlineFormSet):
    """
    Form set validation
    """

    def clean(self):
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return

        form_changed_count = 0

        for form in self.forms:
            if form.has_changed():
                form_changed_count += 1
                # stock_item = form.cleaned_data.get('stock_item', '')
                # if not stock_item:
                #     raise forms.ValidationError("Please choose a product", "error")

        if form.changed_data and form_changed_count == 0:
            raise forms.ValidationError("At least one stock details must be supplied", "error")


SALE_TERM_FORM_SET = inlineformset_factory(
    SaleVoucherAccounts,
    SaleTermAccounts,
    form=SaleTermAccountsForm,
    formset=SaleTermAccountsFormSet,
    extra=1,
    min_num=1,
    max_num=100,
    validate_max=True,
    can_delete=True
)


class SaleTaxForm(forms.ModelForm):
    """
    Sales Tax Form
    """
    class Meta:
        model = SaleTaxAccounts
        fields = ('ledger', 'total')

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super(SaleTaxForm, self).__init__(*args, **kwargs)

        self.fields['ledger'].queryset = LedgerMaster.objects.filter(
            Q(company=self.company),
            Q(ledger_group__group_base__name__exact='Duties & Taxes'))
        self.fields['ledger'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'onchange': 'additional_gst_value(this)', }
        self.fields['total'].widget.attrs = {
            'class': 'form-control', 'step': 'any'}


SALE_TAX_FORM_SET = inlineformset_factory(
    SaleVoucherAccounts,
    SaleTaxAccounts, 
    form=SaleTaxForm,
    extra=2,
    min_num=1,
    max_num=100,
    validate_max=True,
    can_delete=True)
