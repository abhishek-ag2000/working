from django import forms
from django.core.exceptions import ValidationError

from . models import EmployeeMasterQR, StockMasterQR


class DateInput(forms.DateInput):
    input_type = 'date'


class StockItemsQRForm(forms.ModelForm):
    """
    Stock Master QR Forms
    """
    class Meta:
        model = StockMasterQR
        fields = ('stock_name', 'bar_code',
                  'batch_no', 'mnf_date', 'exp_date',)
        widgets = {
            'mnf_date': DateInput(),
            'exp_date': DateInput()
        }

    def __init__(self, *args, **kwargs):
        self.Company = kwargs.pop('company', None)
        super(StockItemsQRForm, self).__init__(*args, **kwargs)
        self.fields['stock_name'].widget.attrs = {'class': 'form-control', }
        self.fields['batch_no'].widget.attrs = {'class': 'form-control', }
        self.fields['mnf_date'].widget.attrs = {'class': 'form-control', }
        self.fields['exp_date'].widget.attrs = {'class': 'form-control', }

    def clean_stock_name(self):
        stock_name = self.cleaned_data['stock_name']

        master_id = 0
        if self.instance:
            # master id is used to exclude current master so that it is not checked as duplicate
            master_id = self.instance.id

        if StockMasterQR.objects.filter(company=self.Company, stock_name__iexact=stock_name).exclude(id=master_id).exists():
            raise forms.ValidationError("This Stock name already exists")
        return stock_name


class EmployeeMasterQRForm(forms.ModelForm):
    """
    Employee Master QR Forms
    """
    class Meta:
        model = EmployeeMasterQR
        fields = ('employee_name', 'post', 'email',
                  'phone_no', 'salary', 'joining_date',)
        widgets = {
            'joining_date': DateInput(),
        }

    def __init__(self, *args, **kwargs):
        self.Company = kwargs.pop('organisation', None)
        super(EmployeeMasterQRForm, self).__init__(*args, **kwargs)
        self.fields['employee_name'].widget.attrs = {'class': 'form-control', }
        self.fields['post'].widget.attrs = {'class': 'form-control', }
        self.fields['salary'].widget.attrs = {'class': 'form-control', }
        self.fields['phone_no'].widget.attrs = {'class': 'form-control', }
        self.fields['email'].widget.attrs = {'class': 'form-control', }
        self.fields['joining_date'].widget.attrs = {'class': 'form-control', }
