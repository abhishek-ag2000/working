"""
Income Tax Computaion Forms
"""
from django import forms
from django.db.models import Q
from accounting_entry.models import LedgerMaster
from .models import IncomeTax, get_choice_assesment_year, get_default_assesment_year

def get_income_tax_choose_ledger_dynamic_form(amount_field_name):
    """
    Returns a dynamic form class based on model field specified in the parameter
    """
    class IncomeTaxChooseLedgerForm(forms.ModelForm):
        """
        Form Class
        """
        class Meta:
            model = IncomeTax
            fields = (amount_field_name,)

        def __init__(self, *args, **kwargs):
            company = kwargs.pop(
                'company')  # pop before super call
            super(IncomeTaxChooseLedgerForm, self).__init__(*args, **kwargs)
            self.fields['Get_Amount_From_Ledger'] = forms.ModelChoiceField(
                queryset=LedgerMaster.objects.filter(
                    Q(company=company)  # &
                    # (
                    #     Q(LedgerGroup_Name__Nature_of_LedgerGroup='Expenses') |
                    #     Q(LedgerGroup_Name__Nature_of_LedgerGroup='Income')
                    # )
                ),
                required=False
            )
            self.fields['Get_Amount_From_Ledger'].widget.attrs = {
                'class': 'select2_demo_2 form-control', }
            self.fields[amount_field_name].widget.attrs = {
                'class': 'form-control', 'step': 'any'}

    return IncomeTaxChooseLedgerForm


class IncomeTaxChooseYearForm(forms.Form):
    """
    Choose financial/assesment year
    """
    # class Meta:
    #     model = IncomeTax
    #     fields = ('Ledger',)

    def __init__(self, *args, **kwargs):
        last_period = kwargs.pop('last_period', None)
        if last_period is None or last_period == "0000-0000":
            last_period = get_default_assesment_year()
        super(IncomeTaxChooseYearForm, self).__init__(*args, **kwargs)
        self.fields['Choose_Year'] = forms.ChoiceField(
            choices=get_choice_assesment_year(),
            initial=last_period)
        self.fields['Choose_Year'].widget.attrs = {
            'class': 'select2_demo_2 form-control', }
