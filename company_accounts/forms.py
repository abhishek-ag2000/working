from django import forms
from company.models import company
import datetime
from django.db.models import Q
from django.forms import inlineformset_factory
from accounting_double_entry.models import ledger1
from company_accounts.models import Purchase_accounts,Sales_accounts,Purchase_Total,Sales_total


class DateInput(forms.DateInput):
    input_type = 'date'

class Purchase_form(forms.ModelForm):
	class Meta:
		model  = Purchase_accounts
		fields = ('User','Company','date','Address','billname','GSTIN','PAN','State','Contact','DeliveryNote','Supplierref','Mode', 'ref_no', 'Party_ac', 'purchase', 'sub_total')
		widgets = {
            'date': DateInput(),
        }

	def __init__(self, *args, **kwargs):
		self.User = kwargs.pop('User', None)		
		self.Company = kwargs.pop('Company', None)
		super(Purchase_form, self).__init__(*args, **kwargs)
		self.fields['date'].widget.attrs     = {'class': 'form-control',}
		self.fields['ref_no'].widget.attrs   = {'class': 'form-control',}
		self.fields['billname'].widget.attrs   = {'class': 'form-control',}
		self.fields['Party_ac'].queryset = ledger1.objects.filter(Q(Company = self.Company) , Q(group1_Name__group_Name__icontains='Sundry Creditors') | Q(group1_Name__group_Name__icontains='Bank Accounts') | Q(group1_Name__group_Name__icontains='Cash-in-hand') | Q(group1_Name__Master__group_Name__icontains='Sundry Creditors') | Q(group1_Name__Master__group_Name__icontains='Bank Accounts') | Q(group1_Name__Master__group_Name__icontains='Cash-in-hand'))
		self.fields['Party_ac'].widget.attrs = {'class': 'select2_demo_2 form-control',}
		self.fields['purchase'].queryset = ledger1.objects.filter(Q(Company = self.Company) ,Q(group1_Name__group_Name__icontains='Purchase Accounts') | Q(group1_Name__Master__group_Name__icontains='Purchase Accounts'))
		self.fields['purchase'].widget.attrs = {'class': 'select2_demo_2 form-control',}
		self.fields['sub_total'].widget.attrs = {'class': 'form-control',}
		self.fields['Address'].widget.attrs = {'class': 'form-control',}
		self.fields['GSTIN'].widget.attrs = {'class': 'form-control',}
		self.fields['PAN'].widget.attrs = {'class': 'form-control',}
		self.fields['State'].widget.attrs = {'class': 'select2_demo_2 form-control',}
		self.fields['Contact'].widget.attrs = {'class': 'form-control',}
		self.fields['DeliveryNote'].widget.attrs = {'class': 'form-control',}
		self.fields['Supplierref'].widget.attrs = {'class': 'form-control',}
		self.fields['Mode'].widget.attrs = {'class': 'form-control',}


class Sales_form(forms.ModelForm):
	class Meta:
		model  = Sales_accounts
		fields = ('User','Company','date','Address','billname','GSTIN','PAN','State','Contact','DeliveryNote','Supplierref','Mode', 'ref_no', 'Party_ac', 'sales', 'sub_total')
		widgets = {
            'date': DateInput(),
        }

	def __init__(self, *args, **kwargs):
		self.User = kwargs.pop('User', None)		
		self.Company = kwargs.pop('Company', None)
		super(Sales_form, self).__init__(*args, **kwargs)
		self.fields['date'].widget.attrs     = {'class': 'form-control',}
		self.fields['ref_no'].widget.attrs   = {'class': 'form-control',}
		self.fields['billname'].widget.attrs   = {'class': 'form-control',}
		self.fields['Party_ac'].queryset = ledger1.objects.filter(Q(Company = self.Company) , Q(group1_Name__group_Name__icontains='Sundry Debtors') | Q(group1_Name__group_Name__icontains='Bank Accounts') | Q(group1_Name__group_Name__icontains='Cash-in-hand') | Q(group1_Name__Master__group_Name__icontains='Sundry Debtors') | Q(group1_Name__Master__group_Name__icontains='Bank Accounts') | Q(group1_Name__Master__group_Name__icontains='Cash-in-hand'))
		self.fields['Party_ac'].widget.attrs = {'class': 'select2_demo_2 form-control',}
		self.fields['sales'].queryset = ledger1.objects.filter(Q(Company = self.Company) ,Q(group1_Name__group_Name__icontains='Sales Account') | Q(group1_Name__Master__group_Name__icontains='Sales Account'))
		self.fields['sales'].widget.attrs = {'class': 'select2_demo_2 form-control',}
		self.fields['sub_total'].widget.attrs = {'class': 'form-control',}
		self.fields['Address'].widget.attrs = {'class': 'form-control',}
		self.fields['GSTIN'].widget.attrs = {'class': 'form-control',}
		self.fields['PAN'].widget.attrs = {'class': 'form-control',}
		self.fields['State'].widget.attrs = {'class': 'select2_demo_2 form-control',}
		self.fields['Contact'].widget.attrs = {'class': 'form-control',}
		self.fields['DeliveryNote'].widget.attrs = {'class': 'form-control',}
		self.fields['Supplierref'].widget.attrs = {'class': 'form-control',}
		self.fields['Mode'].widget.attrs = {'class': 'form-control',}


class Purchase_Total_form(forms.ModelForm):
	class Meta:
		model  = Purchase_Total
		fields = ('purchase_ledger', 'Quantity_p', 'rate_p', 'gst_rate', 'Disc_p', 'Total_p')


	def __init__(self, *args, **kwargs):
		self.Company = kwargs.pop('Company', None)
		super(Purchase_Total_form, self).__init__(*args, **kwargs)
		self.fields['purchase_ledger'].queryset = ledger1.objects.filter(group1_Name__group_Name__icontains='Purchase Accounts') 
		self.fields['purchase_ledger'].widget.attrs = {'class': 'select2_demo_2 form-control',}
		self.fields['Quantity_p'].widget.attrs = {'class': 'form-control',}
		self.fields['gst_rate'].widget.attrs = {'class': 'form-control',}
		self.fields['rate_p'].widget.attrs     = {'class': 'form-control',}
		self.fields['Disc_p'].widget.attrs = {'class': 'form-control',}
		self.fields['Total_p'].widget.attrs = {'class': 'form-control',}

Purchase_formSet = inlineformset_factory(Purchase_accounts, Purchase_Total,
                                            form=Purchase_Total_form, extra=3)



class Sales_total_form_accounts(forms.ModelForm):
	class Meta:
		model  = Sales_total
		fields = ('sales_ledger', 'Quantity', 'rate','gst_rate', 'Disc', 'Total')


	def __init__(self, *args, **kwargs):
		self.Company = kwargs.pop('Company', None)
		super(Sales_total_form_accounts, self).__init__(*args, **kwargs)
		self.fields['sales_ledger'].queryset = ledger1.objects.filter(group1_Name__group_Name__icontains='Sales Account') 
		self.fields['sales_ledger'].widget.attrs = {'class': 'select2_demo_2 form-control',}
		self.fields['Quantity'].widget.attrs = {'class': 'form-control',}
		self.fields['rate'].widget.attrs     = {'class': 'form-control',}
		self.fields['gst_rate'].widget.attrs = {'class': 'form-control',}
		self.fields['Disc'].widget.attrs = {'class': 'form-control',}
		self.fields['Total'].widget.attrs = {'class': 'form-control',}

Sales_ledger_formSet = inlineformset_factory(Sales_accounts, Sales_total,
                                            form=Sales_total_form_accounts, extra=3)