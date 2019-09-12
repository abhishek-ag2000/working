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
from .models_sale import SaleVoucher, SaleStock, SaleTerm, SaleTax


class SaleForm(forms.ModelForm):
    """
    Sales Form
    """
    class Meta:
        model = SaleVoucher
        fields = ('nature_transactions_sales', 'voucher_date', 'consignee_name', 'consignee_address', 'consignee_gstin', 'consignee_pan', 'consignee_pan',
                  'consignee_contact', 'consignee_state', 'other_details', 'consignee_country', 'despatch_no', 'despatch_info', 'destination',
                  'landing_bill', 'landing_date', 'vechicle_no', 'supply_place', 'supplier_ref', 'ref_no', 'party_ac', 'doc_ledger',
                  'gst_details', 'bill_no', 'bill_date', 'port_code', 'delivery_terms', 'shipper_place', 'flight_no',
                  'loading_port', 'discharge_port', 'supply_country')
        widgets = {
            'voucher_date': DateInput(),
            'bill_date': DateInput(),
            'landing_date': DateInput(),
        }

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super(SaleForm, self).__init__(*args, **kwargs)

        self.fields['voucher_date'].widget.attrs = {'class': 'form-control', }
        self.fields['ref_no'].widget.attrs = {'class': 'form-control', }
        self.fields['consignee_name'].widget.attrs = {
            'class': 'form-control', }
        self.fields['consignee_address'].widget.attrs = {'class': 'form-control', }
        self.fields['consignee_pan'].widget.attrs = {'class': 'form-control', }
        self.fields['consignee_gstin'].widget.attrs = {'class': 'form-control', }
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
        self.fields['doc_ledger'].queryset = LedgerMaster.objects.filter(
            Q(company=self.company),
            Q(ledger_group__group_base__name__exact='Sales Accounts'))
        self.fields['doc_ledger'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }
        self.fields['doc_ledger'].empty_label = None
        self.fields['nature_transactions_sales'].widget.attrs = {
            'class': 'select2_demo_2 form-control col-lg-8', 'onchange': 'gst_change(this)', }
        self.fields['supply_place'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'onchange': 'place_details_value(this)',}
        self.fields['supply_place'].initial = self.company.organisation.state.id
        self.fields['consignee_state'].widget.attrs = {'class': 'form-control', }
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

        if SaleVoucher.objects.filter(company=self.company, ref_no__iexact=ref_no).exclude(id=master_id).exists():
            raise forms.ValidationError("This Invoice Number already exists")
        return ref_no


class SaleFormAdmin(forms.ModelForm):
    """
    Sales Form for Admin
    """
    class Meta:
        model = SaleVoucher
        fields = ('user', 'company', 'nature_transactions_sales', 'voucher_date', 'other_details', 'consignee_name',
                  'consignee_address', 'consignee_pan', 'consignee_pan', 'consignee_contact', 'consignee_state', 'consignee_country',
                  'despatch_no', 'despatch_info', 'destination', 'landing_bill', 'landing_date', 'vechicle_no',
                  'supply_place', 'supplier_ref', 'ref_no', 'party_ac', 'doc_ledger', 'sub_total', 'gst_details',
                  'bill_no', 'bill_date', 'port_code')
        widgets = {
            'voucher_date': DateInput(),
            'bill_date': DateInput(),
        }

    def __init__(self, *args, **kwargs):
        super(SaleFormAdmin, self).__init__(*args, **kwargs)
        self.fields['voucher_date'].widget.attrs = {'class': 'form-control', }
        self.fields['ref_no'].widget.attrs = {'class': 'form-control', }
        self.fields['consignee_name'].widget.attrs = {
            'class': 'form-control', }
        self.fields['consignee_address'].widget.attrs = {'class': 'form-control', }
        self.fields['consignee_pan'].widget.attrs = {'class': 'form-control', }
        self.fields['consignee_pan'].widget.attrs = {'class': 'form-control', }
        self.fields['consignee_contact'].widget.attrs = {
            'class': 'form-control', }
        self.fields['consignee_country'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }
        self.fields['other_details'].widget.attrs = {'class': 'form-control', }
        self.fields['other_details'].widget.attrs['disabled'] = True
        self.fields['party_ac'].queryset = LedgerMaster.objects.filter(
            Q(ledger_group___group_base__name__exact='Sundry Debtors') |
            Q(ledger_group___group_base__name__exact='Bank Accounts') |
            Q(ledger_group___group_base__name__exact='Cash-in-Hand'))
        self.fields['party_ac'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }
        self.fields['doc_ledger'].queryset = LedgerMaster.objects.filter(
            Q(ledger_group___group_base__name__exact='Sales Account') |
            Q(ledger_group___group_base__name__exact='Sales Accounts'))
        self.fields['doc_ledger'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }
        self.fields['nature_transactions_sales'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }
        self.fields['sub_total'].widget.attrs = {'class': 'form-control', }
        self.fields['supply_place'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }
        self.fields['supplier_ref'].widget.attrs = {'class': 'form-control', }
        self.fields['gst_details'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }
        self.fields['bill_no'].widget.attrs = {'class': 'form-control', }
        self.fields['bill_date'].widget.attrs = {'class': 'form-control', }
        self.fields['port_code'].widget.attrs = {'class': 'form-control', }
        self.fields['port_code'].widget.attrs['disabled'] = True
        self.fields['despatch_no'].widget.attrs = {'class': 'form-control', }
        self.fields['despatch_info'].widget.attrs = {'class': 'form-control', }
        self.fields['destination'].widget.attrs = {'class': 'form-control', }
        self.fields['landing_bill'].widget.attrs = {'class': 'form-control', }
        self.fields['landing_date'].widget.attrs = {'class': 'form-control', }
        self.fields['vechicle_no'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }

    def clean(self):
        party_ac = self.cleaned_data['party_ac']
        doc_ledger = self.cleaned_data['doc_ledger']
        if party_ac not in LedgerMaster.objects.filter(
                Q(ledger_group___group_base__name__exact='Sundry Debtors') |
                Q(ledger_group___group_base__name__exact='Bank Accounts') |
                Q(ledger_group___group_base__name__exact='Cash-in-Hand')):
            raise forms.ValidationError(
                "Party Account should be for that ledgers which is present under of Sundry Debtors, Bank Accounts & Cash-in-Hand")
        if doc_ledger not in LedgerMaster.objects.filter(ledger_group___group_base__name__exact='Sales Account'):
            raise forms.ValidationError(
                "Sale Ledgers should be for that ledgers which is present under of Sales Account")


class SaleStockForm(forms.ModelForm):
    """
    Sale Stock Form
    """
    class Meta:
        model = SaleStock
        fields = ('stock_item', 'quantity', 'rate', 'disc', 'total')

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super(SaleStockForm, self).__init__(*args, **kwargs)

        self.fields['stock_item'].queryset = StockItem.objects.filter(company=self.company)
        self.fields['stock_item'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'onchange': 'stock_based_value(this)'}
        self.fields['quantity'].widget.attrs = {
            'class': 'form-control', 'onchange': 'calcProductTotal(this)'}
        self.fields['rate'].widget.attrs = {
            'class': 'form-control', 'step': 'any', 'onchange': 'calcProductTotal(this)'}
        self.fields['disc'].widget.attrs = {
            'class': 'form-control', 'step': 'any', 'onchange': 'calcProductTotal(this)', }
        self.fields['total'].widget.attrs = {
            'class': 'form-control', 'step': 'any', 'onchange': 'calcProductRate(this)', }

    # def clean(self):

    #     cleaned_data = super().clean()
    #     stock_item = cleaned_data.get("stock_item")
    #     quantity = cleaned_data.get("quantity")
    #     rate = cleaned_data.get("rate")


    #     if not stock_item:
    #         msg = "Product must be selected."
    #         self.add_error('stock_item', msg)
    #     if quantity <= 0:
    #         msg = "Quantity cannot be zero or negative."
    #         self.add_error('quantity', msg)
    #     if  rate <= 0:
    #         msg = "Rate cannot be zero or negative."
    #         self.add_error('rate', msg)

    def clean_stock_item(self):
        stock_item = self.cleaned_data['stock_item']
        print(self.company)
        if not stock_item:
            raise forms.ValidationError("Product must be selected")
        return stock_item

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity < 0:
            raise forms.ValidationError("Quantity cannot be zero or negative")
        print(quantity)
        return quantity

    def clean_rate(self):
        rate = self.cleaned_data['rate']
        if rate < 0:
            raise forms.ValidationError("Rate cannot be negative")
        return rate

    def clean_total(self):
        total = self.cleaned_data['total']
        if total < 0:
            raise forms.ValidationError("Sub total cannot be negative")
        return total


class SaleStockFormSet(forms.BaseInlineFormSet):
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
            print('Form Changed')
            raise forms.ValidationError("At least one stock details must be supplied", "error")


SALE_STOCK_FORM_SET = inlineformset_factory(
    SaleVoucher,
    SaleStock,
    form=SaleStockForm,
    formset=SaleStockFormSet,
    extra=1,
    min_num=1,
    max_num=100,
    validate_max=True,
    can_delete=True
)


class SaleTermForm(forms.ModelForm):
    """
    Sale Term Form
    """
    class Meta:
        model = SaleTerm
        fields = ('ledger', 'rate', 'total')

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super(SaleTermForm, self).__init__(*args, **kwargs)

        self.fields['ledger'].queryset = LedgerMaster.objects.filter(
            Q(company=self.company),
            Q(ledger_group__group_base__name__exact='Sales Accounts') |
            Q(ledger_group__group_base__name__exact='Direct Incomes') |
            Q(ledger_group__group_base__name__exact='Indirect Incomes') |
            Q(ledger_group__group_base__name__exact='Indirect Expenses') |
            Q(ledger_group__group_base__name__exact='Direct Expenses'))
        self.fields['ledger'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'onchange': 'additional_ledger_value(this)'}
        self.fields['rate'].widget.attrs = {
            'class': 'form-control', 'step': 'any','onchange': 'additional_ledger_changed_rate(this)',}
        self.fields['total'].widget.attrs = {
            'class': 'form-control', 'step': 'any'}



SALE_TERM_FORM_SET = inlineformset_factory(
    SaleVoucher,
    SaleTerm,
    form=SaleTermForm,
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
        model = SaleTax
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
    SaleVoucher,
    SaleTax,
    form=SaleTaxForm,
    extra=2,
    min_num=1,
    max_num=100,
    validate_max=True,
    can_delete=True
)
