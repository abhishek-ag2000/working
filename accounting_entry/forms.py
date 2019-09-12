"""
Forms
"""
from django import forms
#from django.core.exceptions import ValidationError
from django.db.models import Q
from django.forms import inlineformset_factory#, BaseInlineFormSet
from bracketline.forms import DateInput
from .models import BankReconciliation, JournalVoucher, LedgerGroup, LedgerMaster, PeriodSelected
from .models import PaymentVoucher, PaymentVoucherRows, ReceiptVoucher, ReceiptVoucherRows, ContraVoucher
from .models import ContraVoucherRows, MultiJournalVoucher, MultiJournalVoucherDrRows, MultiJournalVoucherCrRows


class LedgerGroupForm(forms.ModelForm):
    """
    Ledger Group Form
    """
    class Meta:
        model = LedgerGroup
        fields = ('group_name', 'self_group')
        widgets = {
            'group_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.company = kwargs.pop('company', None)
        super(LedgerGroupForm, self).__init__(*args, **kwargs)
        self.fields['self_group'].widget.attrs = {'class': 'select2_demo_2 form-control', }
        self.fields['self_group'].queryset = LedgerGroup.objects.filter(
            user=self.user, company=self.company).order_by('group_name')

    def clean_group_name(self):
        """
        Clean the field sepcific field
        """
        group_name = self.cleaned_data['group_name']
        master_id = 0

        if self.instance:
            # master id is used to exclude current master so that it is not checked as duplicate
            master_id = self.instance.id

        if LedgerGroup.objects.filter(company=self.company, group_name__iexact=group_name).exclude(id=master_id).exists():
            raise forms.ValidationError("Group name already exists")

        return group_name

    def clean(self):
        """
        Form level cleanup
        """
        cleaned_data = super().clean()

        group_name = cleaned_data.get('group_name')
        if not group_name:
            return

        group_master_obj = cleaned_data.get('self_group')
        if not group_master_obj:
            return

        if group_name.lower() == group_master_obj.group_name.lower():
            self.add_error(
                'group_name', "Group name cannot be same as Under Group name")
            #raise forms.ValidationError("Group name cannot be same as Under Group name")


class LedgerMasterForm(forms.ModelForm):
    """
    Ledger Master Form
    """
    class Meta:
        model = LedgerMaster
        fields = ('ledger_name', 'ledger_group', 'opening_balance', 'party_name', 'address', 'set_or_alter_gst_tax', 'city',
                  'state', 'country', 'pin_code', 'pan_no', 'gst_no', 'account_holder_name', 'account_no', 'ifsc_code', 'bank_name', 'branch',
                  'duty_tax_type', 'tax_type', 'assessable_value', 'appropiate_to', 'calculation_method', 'gst_applicable', 'set_or_alter_gst',
                  'supply_type', 'registration_type', 'is_eoperator', 'deemed_expoter', 'party_type', 'is_transporter', 'transporter_id',
                  'hsn_desc', 'hsn_no', 'is_non_gst', 'nature_transactions_purchase', 'nature_transactions_sales', 'goods_nature',
                  'taxability', 'integrated_tax', 'central_tax', 'state_tax', 'cess','assessee_of_other_teritory')

    def __init__(self,  *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.company = kwargs.pop('company', None)
        #instance = getattr(self, 'instance', None)

        super(LedgerMasterForm, self).__init__(*args, **kwargs)

        self.fields['ledger_name'].widget.attrs = {'class': 'form-control',}
        self.fields['ledger_group'].queryset = LedgerGroup.objects.filter(
            company=self.company)
        self.fields['ledger_group'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'placeholder': "Select Group"}
        self.fields['opening_balance'].widget.attrs = {
            'class': 'form-control', }
        self.fields['party_name'].widget.attrs = {'class': 'form-control', }
        self.fields['address'].widget.attrs = {'class': 'form-control', }
        self.fields['state'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }
        self.fields['country'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'onchange': 'country_change(this)'}
        self.fields['pin_code'].widget.attrs = {'class': 'form-control', }
        self.fields['pan_no'].widget.attrs = {'class': 'form-control', }
        self.fields['gst_no'].widget.attrs = {
            'class': 'form-control', 'onchange': 'GST_No_Changed(this)', }
        self.fields['account_holder_name'].widget.attrs = {
            'class': 'form-control', }
        self.fields['account_no'].widget.attrs = {'class': 'form-control', }
        self.fields['ifsc_code'].widget.attrs = {'class': 'form-control', }
        self.fields['bank_name'].widget.attrs = {'class': 'form-control', }
        self.fields['branch'].widget.attrs = {'class': 'form-control', }
        self.fields['duty_tax_type'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'onchange': 'gst_access_change(this)', }
        self.fields['tax_type'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }
        self.fields['assessable_value'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'onchange': 'access_change(this)', }
        self.fields['appropiate_to'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'onchange': 'appropiate_change(this)', }
        self.fields['calculation_method'].widget.attrs = {
            'class': 'form-control', }
        # self.fields['calculation_method'].widget.attrs['disabled'] = True
        self.fields['gst_applicable'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'onchange': 'gst_change(this)', }
        self.fields['set_or_alter_gst'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'onchange': 'set_gst_change(this)', }
        self.fields['set_or_alter_gst_tax'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'onchange': 'tax_access_change(this)', }
        self.fields['supply_type'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }
        self.fields['registration_type'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'onchange': 'change_gst_regtype(this)', }
        self.fields['is_eoperator'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'onchange': 'change_is_ecommerce(this)', }
        self.fields['is_eoperator'].initial = 'No'
        self.fields['deemed_expoter'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }
        self.fields['party_type'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }
        self.fields['is_transporter'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'onchange': 'change_transporter(this)', }
        self.fields['transporter_id'].widget.attrs = {
            'class': 'form-control', }
        self.fields['transporter_id'].widget.attrs['disabled'] = True
        self.fields['hsn_desc'].widget.attrs = {'class': 'form-control', }
        self.fields['hsn_no'].widget.attrs = {'class': 'form-control', }
        self.fields['is_non_gst'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'onchange': 'change_is_non_gst(this)', }
        self.fields['nature_transactions_purchase'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'onchange': 'change_taxability_purchase(this)', }
        self.fields['nature_transactions_sales'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'onchange': 'change_taxability_sales(this)', }
        self.fields['goods_nature'].widget.attrs = {
            'class': 'form-control', }
        #self.fields['goods_nature'].widget.attrs['disabled'] = True
        self.fields['taxability'].widget.attrs = {'class': 'form-control','onchange': 'change_taxability(this)', }
        self.fields['integrated_tax'].widget.attrs = {
            'class': 'form-control', 'step': 'any'}
        self.fields['central_tax'].widget.attrs = {
            'class': 'form-control', 'step': 'any'}
        self.fields['state_tax'].widget.attrs = {
            'class': 'form-control', 'step': 'any'}
        self.fields['cess'].widget.attrs = {'class': 'form-control', }
        self.fields['assessee_of_other_teritory'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'onchange': 'change_assessee_of_other_teritory(this)', }
        self.fields['assessee_of_other_teritory'].initial = 'No'

    def get_form(self, request, obj=None, **kwargs):
        """
        Returns the form object
        """
        form = super(LedgerMasterForm, self).get_form(request, obj, **kwargs)
        form.base_fields['ledger_group'].label_from_instance = lambda obj: "{} : {}".format(
            obj.group_name, obj.self_group.group_name)
        return form

    def clean_ledger_name(self):
        """
        Validate leder name field
        """
        ledger_name = self.cleaned_data['ledger_name']

        master_id = 0
        if self.instance:
            # master id is used to exclude current master so that it is not checked as duplicate
            master_id = self.instance.id

        if LedgerMaster.objects.filter(company=self.company, ledger_name__iexact=ledger_name).exclude(id=master_id).exists():
            raise forms.ValidationError("Ledger name already exists")

        return ledger_name


class LedgerMasterFormAdmin(forms.ModelForm):
    """
    Ledger Master Form for Admin
    """
    class Meta:
        model = LedgerMaster
        fields = ('ledger_name', 'ledger_group', 'opening_balance', 'party_name', 'address', 'set_or_alter_gst_tax', 'city',
                  'state', 'pin_code', 'pan_no', 'gst_no', 'account_holder_name', 'account_no', 'ifsc_code', 'bank_name', 'branch',
                  'duty_tax_type', 'tax_type', 'assessable_value', 'appropiate_to', 'calculation_method', 'gst_applicable', 'set_or_alter_gst',
                  'supply_type', 'registration_type', 'is_eoperator', 'deemed_expoter', 'party_type', 'is_transporter', 'transporter_id',
                  'hsn_desc', 'hsn_no', 'is_non_gst', 'nature_transactions_purchase', 'nature_transactions_sales',
                  'goods_nature', 'taxability', 'integrated_tax', 'central_tax', 'state_tax', 'cess','assessee_of_other_teritory')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.company = kwargs.pop('company', None)
        #instance = getattr(self, 'instance', None)
        super(LedgerMasterFormAdmin, self).__init__(*args, **kwargs)

        self.fields['ledger_name'].widget.attrs = {'class': 'form-control',}
        self.fields['ledger_group'].queryset = LedgerGroup.objects.filter(
            company=self.company)
        self.fields['ledger_group'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'placeholder': "Select Group", 'onchange': 'group_change(this)', }
        self.fields['opening_balance'].widget.attrs = {
            'class': 'form-control', }
        self.fields['party_name'].widget.attrs = {'class': 'form-control', }
        self.fields['address'].widget.attrs = {'class': 'form-control', }
        self.fields['state'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }
        self.fields['pin_code'].widget.attrs = {'class': 'form-control', }
        self.fields['pan_no'].widget.attrs = {'class': 'form-control', }
        self.fields['gst_no'].widget.attrs = {'class': 'form-control', }
        self.fields['account_holder_name'].widget.attrs = {
            'class': 'form-control', }
        self.fields['account_no'].widget.attrs = {'class': 'form-control', }
        self.fields['ifsc_code'].widget.attrs = {'class': 'form-control', }
        self.fields['bank_name'].widget.attrs = {'class': 'form-control', }
        self.fields['branch'].widget.attrs = {'class': 'form-control', }
        self.fields['duty_tax_type'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'onchange': 'gst_access_change(this)', }
        self.fields['tax_type'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }
        self.fields['assessable_value'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'onchange': 'access_change(this)', }
        self.fields['appropiate_to'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'onchange': 'appropiate_change(this)', }
        self.fields['calculation_method'].widget.attrs = {
            'class': 'form-control', }
        self.fields['calculation_method'].widget.attrs['disabled'] = True
        self.fields['gst_applicable'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'onchange': 'gst_change(this)', }
        self.fields['set_or_alter_gst'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'onchange': 'set_gst_change(this)', }
        self.fields['set_or_alter_gst_tax'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'onchange': 'tax_access_change(this)', }
        self.fields['supply_type'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }
        self.fields['registration_type'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }
        self.fields['is_eoperator'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'onchange': 'change_is_ecommerce(this)', }
        self.fields['is_eoperator'].initial = 'No'
        self.fields['deemed_expoter'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }
        self.fields['party_type'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }
        self.fields['is_transporter'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'onchange': 'change_transporter(this)', }
        self.fields['transporter_id'].widget.attrs = {
            'class': 'form-control', }
        self.fields['transporter_id'].widget.attrs['disabled'] = True
        self.fields['hsn_desc'].widget.attrs = {'class': 'form-control', }
        self.fields['hsn_no'].widget.attrs = {'class': 'form-control', }
        self.fields['is_non_gst'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'onchange': 'change_is_non_gst(this)', }
        self.fields['nature_transactions_purchase'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'onchange': 'change_taxability_purchase(this)', }
        #self.fields['nature_transactions_purchase'].widget.attrs['disabled'] = True #disable causes null field value for select control
        self.fields['nature_transactions_sales'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'onchange': 'change_taxability_sales(this)', }
        self.fields['goods_nature'].widget.attrs = {
            'class': 'form-control', }
        #self.fields['goods_nature'].widget.attrs['disabled'] = True
        self.fields['taxability'].widget.attrs = {'class': 'form-control','onchange': 'change_taxability(this)', }
        self.fields['integrated_tax'].widget.attrs = {
            'class': 'form-control', 'step': 'any'}
        self.fields['central_tax'].widget.attrs = {
            'class': 'form-control', 'step': 'any'}
        self.fields['state_tax'].widget.attrs = {
            'class': 'form-control', 'step': 'any'}
        self.fields['cess'].widget.attrs = {'class': 'form-control', }
        self.fields['assessee_of_other_teritory'].widget.attrs = {
            'class': 'select2_demo_2 form-control', 'onchange': 'change_assessee_of_other_teritory(this)', }
        self.fields['assessee_of_other_teritory'].initial = 'No'


class JournalVoucherForm(forms.ModelForm):
    """
    Journal Voucher Form
    """
    class Meta:
        model = JournalVoucher
        fields = ('voucher_date', 'dr_ledger',
                  'cr_ledger', 'amount', 'narration')
        widgets = {
            'voucher_date': DateInput(),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.company = kwargs.pop('company', None)
        super(JournalVoucherForm, self).__init__(*args, **kwargs)

        self.fields['voucher_date'].widget.attrs = {'class': 'form-control', }
        self.fields['amount'].widget.attrs = {'class': 'form-control journal-amount', 'step': 'any', 'onchange': 'amount_change(this)'}
        self.fields['cr_ledger'].queryset = LedgerMaster.objects.filter(
            company=self.company)
        self.fields['cr_ledger'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }
        self.fields['dr_ledger'].queryset = LedgerMaster.objects.filter(
            company=self.company)
        self.fields['dr_ledger'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }
        self.fields['narration'].widget.attrs = {'class': 'form-control', }


class BankJournalForm(forms.ModelForm):
    """
    Bank Journal Form
    """
    class Meta:
        model = BankReconciliation
        fields = ('transaction_type', 'instrument_no', 'bank_date')
        widgets = {
            'bank_date': DateInput(),
        }

    def __init__(self, *args, **kwargs):
        super(BankJournalForm, self).__init__(*args, **kwargs)

        self.fields['transaction_type'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }
        self.fields['instrument_no'].widget.attrs = {'class': 'form-control', }
        self.fields['bank_date'].widget.attrs = {'class': 'form-control', }


class DateRangeForm(forms.ModelForm):
    """
    Date Range Form
    """

    def __init__(self, *args, **kwargs):
        super(DateRangeForm, self).__init__(*args, **kwargs)
        self.fields['start_date'].widget.attrs = {'class': 'form-control', }
        self.fields['end_date'].widget.attrs = {'class': 'form-control', }

    class Meta:
        model = PeriodSelected
        fields = ('start_date', 'end_date')
        widgets = {
            'start_date': DateInput(),
            'end_date': DateInput(),
        }


class PaymentVoucherForm(forms.ModelForm):
    """
    Payment Voucher Form
    """
    class Meta:
        model = PaymentVoucher
        fields = ('voucher_date', 'account', 'total_amt')
        widgets = {
            'voucher_date': DateInput(),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.company = kwargs.pop('company', None)
        super(PaymentVoucherForm, self).__init__(*args, **kwargs)

        self.fields['voucher_date'].widget.attrs = {'class': 'form-control', }
        self.fields['account'].queryset = LedgerMaster.objects.filter(
            Q(company=self.company),
            Q(ledger_group__group_base__name__exact='Bank Accounts') |
            Q(ledger_group__group_base__name__exact='Cash-in-Hand'))
        self.fields['account'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }
        self.fields['total_amt'].widget.attrs = {'class': 'form-control', }


class PaymentVoucherRowsForm(forms.ModelForm):
    """
    Payment Voucher Rows Form
    """
    class Meta:
        model = PaymentVoucherRows
        fields = ('particular', 'amount')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.company = kwargs.pop('company', None)
        super(PaymentVoucherRowsForm, self).__init__(*args, **kwargs)

        self.fields['particular'].queryset = LedgerMaster.objects.filter(company=self.company).exclude(
            Q(ledger_group__group_base__name__exact='Bank Accounts') |
            Q(ledger_group__group_base__name__exact='Cash-in-Hand') |
            Q(ledger_group__group_base__name__exact='Primary')) #PL ledger in in Primary which is to be excluded

        self.fields['particular'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }
        self.fields['amount'].widget.attrs = {'class': 'form-control', }

    def clean(self):

        cleaned_data = super().clean()
        particular = cleaned_data.get("particular")
        amount = cleaned_data.get("amount")


        if not particular:
            msg = "Particular must be selected."
            self.add_error('particular', msg)
        if amount <= 0:
            msg = "Amount cannot be zero or negative."
            self.add_error('amount', msg)



class PaymentVoucherRowsFormSet(forms.BaseInlineFormSet):
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

        if form_changed_count == 0:
            raise forms.ValidationError("At least one Ledger details must be supplied", "error")


class ReceiptVoucherForm(forms.ModelForm):
    """
    Receipt Voucher Form
    """
    class Meta:
        model = ReceiptVoucher
        fields = ('voucher_date', 'account', 'total_amt')
        widgets = {
            'voucher_date': DateInput(),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.company = kwargs.pop('company', None)
        super(ReceiptVoucherForm, self).__init__(*args, **kwargs)

        self.fields['voucher_date'].widget.attrs = {'class': 'form-control', }
        self.fields['account'].queryset = LedgerMaster.objects.filter(
            Q(company=self.company),
            Q(ledger_group__group_base__name__exact='Bank Accounts') |
            Q(ledger_group__group_base__name__exact='Cash-in-Hand'))
        self.fields['account'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }
        self.fields['total_amt'].widget.attrs = {'class': 'form-control', }


class ReceiptVoucherRowsForm(forms.ModelForm):
    """
    Receipt Voucher Row Form
    """
    class Meta:
        model = ReceiptVoucherRows
        fields = ('particular', 'amount')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.company = kwargs.pop('company', None)
        super(ReceiptVoucherRowsForm, self).__init__(*args, **kwargs)

        self.fields['particular'].queryset = LedgerMaster.objects.filter(company=self.company).exclude(
            Q(ledger_group__group_base__name__exact='Bank Accounts') |
            Q(ledger_group__group_base__name__exact='Cash-in-Hand') |
            Q(ledger_group__group_base__name__exact='Primary')) #PL ledger in in Primary which is to be excluded
        self.fields['particular'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }
        self.fields['amount'].widget.attrs = {'class': 'form-control', }

    def clean(self):

        cleaned_data = super().clean()
        particular = cleaned_data.get("particular")
        amount = cleaned_data.get("amount")


        if not particular:
            msg = "Particular must be selected."
            self.add_error('particular', msg)
        if amount <= 0:
            msg = "Amount cannot be zero or negative."
            self.add_error('amount', msg)



class ReceiptVoucherRowsFormSet(forms.BaseInlineFormSet):
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

        if form_changed_count == 0:
            raise forms.ValidationError("At least one Ledger details must be supplied", "error")

class ContraVoucherForm(forms.ModelForm):
    """
    Contra Voucher Form
    """
    class Meta:
        model = ContraVoucher
        fields = ('voucher_date', 'account', 'total_amt')
        widgets = {
            'voucher_date': DateInput(),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.company = kwargs.pop('company', None)
        super(ContraVoucherForm, self).__init__(*args, **kwargs)

        self.fields['voucher_date'].widget.attrs = {'class': 'form-control', }
        self.fields['account'].queryset = LedgerMaster.objects.filter(
            Q(company=self.company), Q(ledger_group__group_base__name__exact='Bank Accounts') |
            Q(ledger_group__group_base__name__exact='Cash-in-Hand'))
        self.fields['account'].widget.attrs = {'class': 'select2_demo_2 form-control', }
        self.fields['total_amt'].widget.attrs = {'class': 'form-control', }


class ContraVoucherRowsForm(forms.ModelForm):
    """
    Contra Voucher Rows Form
    """
    class Meta:
        model = ContraVoucherRows
        fields = ('particular', 'amount')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.company = kwargs.pop('company', None)
        super(ContraVoucherRowsForm, self).__init__(*args, **kwargs)

        self.fields['particular'].queryset = LedgerMaster.objects.filter(
            Q(company=self.company),
            Q(ledger_group__group_base__name__exact='Bank Accounts') |
            Q(ledger_group__group_base__name__exact='Cash-in-Hand')).exclude(Q(ledger_group__group_base__name__exact='Primary')) #PL ledger in in Primary which is to be excluded
        self.fields['particular'].widget.attrs = {'class': 'select2_demo_2 form-control', }
        self.fields['amount'].widget.attrs = {'class': 'form-control', }

    def clean(self):

        cleaned_data = super().clean()
        particular = cleaned_data.get("particular")
        amount = cleaned_data.get("amount")


        if not particular:
            msg = "Particular must be selected."
            self.add_error('particular', msg)
        if amount <= 0:
            msg = "Amount cannot be zero or negative."
            self.add_error('amount', msg)



class ContraVoucherRowsFormSet(forms.BaseInlineFormSet):
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

        if form_changed_count == 0:
            raise forms.ValidationError("At least one ledger details must be supplied", "error")

class MultiJournalVoucherForm(forms.ModelForm):
    """
    Multi-Journal Voucher Form
    """
    class Meta:
        model = MultiJournalVoucher
        fields = ('voucher_date', 'amount', 'narration')
        widgets = {
            'voucher_date': DateInput(),
        }

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super(MultiJournalVoucherForm, self).__init__(*args, **kwargs)

        self.fields['voucher_date'].widget.attrs = {'class': 'form-control', }
        self.fields['amount'].widget.attrs = {'class': 'form-control', }
        self.fields['narration'].widget.attrs = {'class': 'form-control', }


class MultiJournalVoucherDrRowsForm(forms.ModelForm):
    """
    Multi-Journal Voucher Rows Form
    """
    class Meta:
        model = MultiJournalVoucherDrRows
        fields = ('ledger', 'amount')

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super(MultiJournalVoucherDrRowsForm, self).__init__(*args, **kwargs)

        self.fields['amount'].widget.attrs = {'class': 'form-control', }
        self.fields['ledger'].queryset = LedgerMaster.objects.filter(
            company=self.company)
        self.fields['ledger'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }



class MultiJournalVoucherCrRowsForm(forms.ModelForm):
    """
    Multi-Journal Voucher Rows Form
    """
    class Meta:
        model = MultiJournalVoucherCrRows
        fields = ('ledger', 'amount')

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super(MultiJournalVoucherCrRowsForm, self).__init__(*args, **kwargs)

        self.fields['amount'].widget.attrs = {'class': 'form-control', }
        self.fields['ledger'].queryset = LedgerMaster.objects.filter(
            company=self.company)
        self.fields['ledger'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }



PAYMENT_FORM_SET = inlineformset_factory(PaymentVoucher, PaymentVoucherRows,
                                         form=PaymentVoucherRowsForm,formset=PaymentVoucherRowsFormSet, extra=3)


RECEIPT_FORM_SET = inlineformset_factory(ReceiptVoucher, ReceiptVoucherRows,
                                         form=ReceiptVoucherRowsForm,formset=ReceiptVoucherRowsFormSet, extra=3)

CONTRA_FORM_SET = inlineformset_factory(ContraVoucher, ContraVoucherRows,
                                        form=ContraVoucherRowsForm,formset=ContraVoucherRowsFormSet, extra=3)


MULTI_JOURNAL_DR_FORM_SET = inlineformset_factory(MultiJournalVoucher, MultiJournalVoucherDrRows,
                                                  form=MultiJournalVoucherDrRowsForm, extra=3)

MULTI_JOURNAL_CR_FORM_SET = inlineformset_factory(MultiJournalVoucher, MultiJournalVoucherCrRows,
                                                  form=MultiJournalVoucherCrRowsForm, extra=3)
