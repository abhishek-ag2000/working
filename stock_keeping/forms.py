"""
Forms
"""
from django import forms
from bracketline.forms import DateInput
from .models import StockGroup, SimpleUnit, CompoundUnit, StockItem


class StockGroupForm(forms.ModelForm):
    """
    Stock Group Form
    """
    class Meta:
        model = StockGroup
        fields = ('group_name', 'self_group', 'set_or_alter_gst', 'hsn', 'is_non_gst', 'taxability',
                  'reverse_charge', 'input_credit', 'integrated_tax', 'central_tax', 'state_tax', 'cess')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.company = kwargs.pop('company', None)
        super(StockGroupForm, self).__init__(*args, **kwargs)

        self.fields['group_name'].widget.attrs = {
            'class': 'form-control', }
        self.fields['self_group'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }
        self.fields['self_group'].queryset = StockGroup.objects.filter(
            user=self.user, company=self.company)
        self.fields['hsn'].widget.attrs = {'class': 'form-control', }
        #self.fields['quantities'].widget.attrs = {'class': 'js-switch_2', }
        self.fields['set_or_alter_gst'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'onchange': 'gst_change(this)', }
        self.fields['is_non_gst'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'onchange': 'change_non_gst(this)', }
        self.fields['taxability'].widget.attrs = {
            'class': 'form-control', 'onchange': 'change_taxability_stock(this)', }
        self.fields['reverse_charge'].widget.attrs = {
            'class': 'form-control', }
        self.fields['input_credit'].widget.attrs = {'class': 'form-control', }
        self.fields['integrated_tax'].widget.attrs = {
            'class': 'form-control', 'step': 'any'}
        self.fields['central_tax'].widget.attrs = {
            'class': 'form-control', 'step': 'any'}
        self.fields['state_tax'].widget.attrs = {
            'class': 'form-control', 'step': 'any'}
        self.fields['cess'].widget.attrs = {
            'class': 'form-control', 'step': 'any'}


class SimpleUnitsForm(forms.ModelForm):
    """
    Simple Unit Form
    """
    class Meta:
        model = SimpleUnit
        fields = ('symbol', 'formal','uqc')

    def __init__(self, *args, **kwargs):
        super(SimpleUnitsForm, self).__init__(*args, **kwargs)
        self.fields['uqc'].widget.attrs = {'class': 'select2_demo_2 form-control', }
        self.fields['symbol'].widget.attrs = {'class': 'form-control', }
        self.fields['formal'].widget.attrs = {'class': 'form-control', }


class CompoundUnitForm(forms.ModelForm):
    """
    Compound Unit Form
    """
    class Meta:
        model = CompoundUnit
        fields = ('first_unit', 'conversion', 'seconds_unit')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.company = kwargs.pop('company', None)
        super(CompoundUnitForm, self).__init__(*args, **kwargs)

        self.fields['first_unit'].queryset = SimpleUnit.objects.filter(
            company=self.company)
        self.fields['first_unit'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }
        self.fields['conversion'].widget.attrs = {'class': 'form-control', }
        self.fields['seconds_unit'].queryset = SimpleUnit.objects.filter(
            company=self.company)
        self.fields['seconds_unit'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }


class StockItemForm(forms.ModelForm):
    """
    Stock Item Form
    """
    class Meta:
        model = StockItem
        fields = ('stock_name', 'rate', 'quantity', 'opening', 'batch_no', 'mfd_date', 'exp_date', 'stock_group', 'simple_unit', 'compound_unit', 'hsn', 'barcode_image',
                  'barcode_text','is_gst', 'set_or_alter_gst', 'is_non_gst', 'taxability', 'reverse_charge', 'input_credit', 'integrated_tax', 'central_tax', 'state_tax', 'cess')
        widgets = {
            'Date': DateInput(),
            'mfd_date': DateInput(),
            'exp_date': DateInput()
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.company = kwargs.pop('company', None)
        super(StockItemForm, self).__init__(*args, **kwargs)

        self.fields['stock_name'].widget.attrs = {'class': 'form-control', }
        self.fields['batch_no'].widget.attrs = {'class': 'form-control', }
        self.fields['mfd_date'].widget.attrs = {'class': 'form-control', }
        self.fields['exp_date'].widget.attrs = {'class': 'form-control', }
        self.fields['rate'].widget.attrs = {'class': 'form-control', }
        self.fields['quantity'].widget.attrs = {'class': 'form-control', }
        self.fields['opening'].widget.attrs = {'class': 'form-control', }
        self.fields['barcode_text'].widget.attrs = {'class': 'form-control', }
        self.fields['stock_group'].queryset = StockGroup.objects.filter(
            user=self.user, company=self.company)
        self.fields['stock_group'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }
        self.fields['simple_unit'].queryset = SimpleUnit.objects.filter(
            user=self.user, company=self.company)
        self.fields['simple_unit'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }
        self.fields['compound_unit'].queryset = CompoundUnit.objects.filter(
            user=self.user, company=self.company)
        self.fields['compound_unit'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }
        self.fields['hsn'].widget.attrs = {'class': 'form-control', }
        self.fields['is_gst'].widget.attrs = {'class': 'form-control',  'onchange': 'change_isgst_applicable_option(this)',}
        self.fields['set_or_alter_gst'].widget.attrs = {
            'class': 'form-control', 'onchange': 'change_setgst_option(this)',}
        self.fields['is_non_gst'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'onchange': 'change_non_gst(this)', }
        self.fields['taxability'].widget.attrs = {
            'class': 'form-control', 'onchange': 'change_taxability_stock(this)', }
        self.fields['reverse_charge'].widget.attrs = {
            'class': 'form-control', }
        self.fields['input_credit'].widget.attrs = {'class': 'form-control', }
        self.fields['integrated_tax'].widget.attrs = {
            'class': 'form-control', 'step': 'any'}
        self.fields['central_tax'].widget.attrs = {
            'class': 'form-control', 'step': 'any'}
        self.fields['state_tax'].widget.attrs = {
            'class': 'form-control', 'step': 'any'}
        self.fields['cess'].widget.attrs = {
            'class': 'form-control', 'step': 'any'}

    def clean_stock_name(self):
        """
        Clean function to raise Validation Error if Stock Name already exist in a company.
        """
        stock_name = self.cleaned_data['stock_name']
        master_id = 0

        if self.instance:
            # master id is used to exclude current master so that it is not checked as duplicate
            master_id = self.instance.id

        if StockItem.objects.filter(company=self.company, stock_name__iexact=stock_name).exclude(id=master_id).exists():
            raise forms.ValidationError("This Stock name already exists")
        return stock_name
