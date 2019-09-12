"""
Forms
"""
from django import forms
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from accounting_entry.models import LedgerMaster
from bracketline.forms import DateInput
from .model_purchase_accounts import PurchaseVoucherAccounts, PurchaseTermAccounts, PurchaseTaxAccounts


class PurchaseAccountsForm(forms.ModelForm):
    """
    Purchase Form
    """
    class Meta:
        model = PurchaseVoucherAccounts
        fields = ('nature_transactions_purchase', 'voucher_date', 'consignee_name', 'consignee_address', 'consignee_pan',
                  'consignee_gstin', 'consignee_contact', 'consignee_state', 'consignee_country', 'supply_state', 'other_details',
                  'delivery_note', 'supplier_ref', 'ref_no', 'party_ac', 'receipt_no', 'despatch_info', 'destination', 'delivery_terms',
                   'shipper_place', 'flight_no', 'loading_port', 'discharge_port', 'to_country')
        widgets = {
            'voucher_date': DateInput(),
        }

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('Company', None)
        super(PurchaseAccountsForm, self).__init__(*args, **kwargs)

        self.fields['voucher_date'].widget.attrs = {'class': 'form-control', }
        self.fields['ref_no'].widget.attrs = {'class': 'form-control', }
        self.fields['party_ac'].queryset = LedgerMaster.objects.filter(
            Q(company=self.company),
            Q(ledger_group__group_base__name__exact='Sundry Creditors') |
            Q(ledger_group__group_base__name__exact='Bank Accounts') |
            Q(ledger_group__group_base__name__exact='Cash-in-Hand'))
        self.fields['party_ac'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }
        self.fields['consignee_name'].widget.attrs = {
            'class': 'form-control', }
        self.fields['consignee_address'].widget.attrs = {'class': 'form-control', }
        self.fields['consignee_gstin'].widget.attrs = {'class': 'form-control', }
        self.fields['consignee_pan'].widget.attrs = {'class': 'form-control', }
        self.fields['consignee_gstin'].widget.attrs['disabled'] = True
        self.fields['consignee_pan'].widget.attrs['disabled'] = True
        self.fields['consignee_contact'].widget.attrs = {
            'class': 'form-control', }
        self.fields['other_details'].widget.attrs = {
                'class': 'form-control', }
        self.fields['consignee_country'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'onchange': 'country_details_value(this)', }
        self.fields['consignee_state'].widget.attrs = {'class': 'form-control', }
        self.fields['consignee_state'].widget.attrs['disabled'] = True
        self.fields['receipt_no'].widget.attrs = {'class': 'form-control', }
        self.fields['despatch_info'].widget.attrs = {'class': 'form-control', }
        self.fields['destination'].widget.attrs = {'class': 'form-control', }
        self.fields['delivery_terms'].widget.attrs = {
            'class': 'form-control', }
        self.fields['nature_transactions_purchase'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'onchange': 'gst_change(this)', }
        self.fields['supply_state'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }
        self.fields['delivery_note'].widget.attrs = {'class': 'form-control', }
        self.fields['supplier_ref'].widget.attrs = {'class': 'form-control', }
        self.fields['shipper_place'].widget.attrs = {'class': 'form-control', }
        self.fields['flight_no'].widget.attrs = {'class': 'form-control', }
        self.fields['loading_port'].widget.attrs = {'class': 'form-control', }
        self.fields['discharge_port'].widget.attrs = {
            'class': 'form-control', }
        self.fields['to_country'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }

    def clean_supply_place(self):
        """
        Clean Method to raise Validatiom Error if Place of Supply do not match with Nature of Transaction provided.
        """
        nature_transactions_purchase = self.cleaned_data['nature_transactions_purchase']
        supply_state = self.cleaned_data['supply_state']

        if self.company.organisation.state == supply_state and nature_transactions_purchase == 'Interstate Purchase - Taxable':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state == supply_state and nature_transactions_purchase == 'Imports Exempt':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state == supply_state and nature_transactions_purchase == 'Imports Nil Rated':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state == supply_state and nature_transactions_purchase == 'Imports Taxable':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state == supply_state and nature_transactions_purchase == 'Interstate Purchase exempt':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state == supply_state and nature_transactions_purchase == 'Interstate Purchase from Unregistered Dealer - Exempt':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state == supply_state and nature_transactions_purchase == 'Interstate Purchase from Unregistered Dealer - Nil Rated':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state == supply_state and nature_transactions_purchase == 'Interstate Purchase from Unregistered Dealer - Taxable':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state == supply_state and nature_transactions_purchase == 'Interstate Purchase  - Nil Rated':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state == supply_state and nature_transactions_purchase == 'Purchase Deemed Exports - Exempt':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state == supply_state and nature_transactions_purchase == 'Purchase Deemed Exports - Nil Rated':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.organisation.state == supply_state and nature_transactions_purchase == 'Purchase Deemed Exports - Taxable':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.State != supply_state and nature_transactions_purchase == 'Intrastate Purchase Deemed Exports - Exempt':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.State != supply_state and nature_transactions_purchase == 'Intrastate Purchase Deemed Exports - Nil Rated':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.State != supply_state and nature_transactions_purchase == 'Intrastate Purchase Deemed Exports - Taxable':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.State != supply_state and nature_transactions_purchase == 'Purchase Exempt':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.State != supply_state and nature_transactions_purchase == 'Purchase From Unregister Dealer - Exempt':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.State != supply_state and nature_transactions_purchase == 'Purchase From Unregister Dealer - Nil Rated':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.State != supply_state and nature_transactions_purchase == 'Purchase From Unregister Dealer - Taxable':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.State != supply_state and nature_transactions_purchase == 'Purchase Nil Rated':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        if self.company.State != supply_state and nature_transactions_purchase == 'Intrastate Purchase Taxable':
            raise ValidationError(
                "This nature of transaction in not valid for the given Place of Supply")
        return supply_state

    def clean_ref_no(self):
        """
        Clean function to raise Validation Error if Invoice Number already exist in a company.
        """
        ref_no = self.cleaned_data['ref_no']
        master_id = 0

        if self.instance:
            # master id is used to exclude current master so that it is not checked as duplicate
            master_id = self.instance.id

        if PurchaseVoucherAccounts.objects.filter(company=self.company, ref_no__iexact=ref_no).exclude(id=master_id).exists():
            raise forms.ValidationError("This Invoice Number already exists")
        return ref_no



class PurchaseTermAccountsForm(forms.ModelForm):
    """
    Purchase Term Form
    """
    class Meta:
        model = PurchaseTermAccounts
        fields = ('ledger', 'total')

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super(PurchaseTermAccountsForm, self).__init__(*args, **kwargs)

        self.fields['ledger'].queryset = LedgerMaster.objects.filter(
            Q(company=self.company),
            Q(ledger_group__group_base__name__exact='Purchase Accounts') |
            Q(ledger_group__group_base__name__exact='Indirect Expenses') |
            Q(ledger_group__group_base__name__exact='Direct Expenses') |
            Q(ledger_group__group_base__name__exact='Indirect Incomes') |
            Q(ledger_group__group_base__name__exact='Direct Incomes') |
            Q(ledger_group__group_base__name__exact='Fixed Assets'))
        self.fields['ledger'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'onchange': 'additional_ledger_value(this)'}
        self.fields['total'].widget.attrs = {
            'class': 'form-control', 'step': 'any'}

    def clean_ledger(self):
        ledger = self.cleaned_data['ledger']
        if not ledger:
            raise forms.ValidationError("Ledger must be selected")
        return ledger



class PurchaseTermAccountsFormSet(forms.BaseInlineFormSet):
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
            raise forms.ValidationError("At least one ledger details must be supplied", "error")


PURCHASE_TERM_FORM_SET = inlineformset_factory(
    PurchaseVoucherAccounts, 
    PurchaseTermAccounts, 
    form=PurchaseTermAccountsForm,
    formset=PurchaseTermAccountsFormSet, 
    extra=1,
    min_num=1,
    max_num=100,
    validate_max=True,
    can_delete=True
)


class PurchaseTaxForm(forms.ModelForm):
    """
    Purchase Tax Form
    """
    class Meta:
        model = PurchaseTaxAccounts
        fields = ('ledger', 'total')

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super(PurchaseTaxForm, self).__init__(*args, **kwargs)

        self.fields['ledger'].queryset = LedgerMaster.objects.filter(
            Q(company=self.company),
            Q(ledger_group__group_base__name__exact='Duties & Taxes'))
        self.fields['ledger'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'onchange': 'additional_gst_value(this)',}
        self.fields['total'].widget.attrs = {
            'class': 'form-control', 'step': 'any'}


PURCHASE_TAX_FORM_SET = inlineformset_factory(
    PurchaseVoucherAccounts, 
    PurchaseTaxAccounts, 
    form=PurchaseTaxForm, 
    extra=2,
    min_num=1,
    max_num=100,
    validate_max=True,
    can_delete=True
)
