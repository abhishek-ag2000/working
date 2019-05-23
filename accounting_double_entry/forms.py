from django import forms
from accounting_double_entry.models import Bank_reconcilation,Pl_journal,journal,group1,ledger1,selectdatefield,Payment,Particularspayment,Receipt,Particularsreceipt,Contra,Particularscontra,Multijournal,Multijournaltotal
from company.models import company
import datetime
from django.db.models import Q
from django.forms import inlineformset_factory



class group1Form(forms.ModelForm):		
	class Meta:
		model = group1
		fields = ('group_Name', 'Master', 'balance_nature','Nature_of_group1')
		widgets = {
			'group_Name': forms.TextInput(attrs= {'class' : 'form-control'}),
			
		}

	def __init__(self, *args, **kwargs):
		self.User = kwargs.pop('User', None)		
		self.Company = kwargs.pop('Company', None)
		super(group1Form, self).__init__(*args, **kwargs)
		self.fields['Master'].widget.attrs = {'class': 'select2_demo_2 form-control',}
		self.fields['Master'].queryset = group1.objects.filter(User= self.User,Company = self.Company).exclude(group_Name__icontains='Primary')
		self.fields['Nature_of_group1'].widget.attrs = {'class': 'select2_demo_2 form-control',}
		self.fields['balance_nature'].widget.attrs = {'class': 'select2_demo_2 form-control',}
		

class DateInput(forms.DateInput):
    input_type = 'date'


class Ledgerform(forms.ModelForm):

	class Meta:
		model = ledger1
		fields = ('name', 'group1_Name', 'Opening_Balance', 'User_Name', 'Address', 'State', 'Pin_Code', 'PanIt_No', 'GST_No')

	def __init__(self,  *args, **kwargs):
		self.User = kwargs.pop('User', None)		
		self.Company = kwargs.pop('Company', None)
		super(Ledgerform, self).__init__(*args, **kwargs)
		self.fields['name'].widget.attrs = {'class': 'form-control',}
		self.fields['group1_Name'].widget.attrs = {'class': 'select2_demo_2 form-control', 'placeholder':"Select Group",}
		self.fields['group1_Name'].queryset = group1.objects.filter(Company = self.Company).exclude(group_Name__icontains='Primary')
		self.fields['Opening_Balance'].widget.attrs = {'class': 'form-control',}
		self.fields['User_Name'].widget.attrs = {'class': 'form-control',}
		self.fields['Address'].widget.attrs = {'class': 'form-control',}
		self.fields['State'].widget.attrs = {'class': 'select2_demo_2 form-control',}
		self.fields['Pin_Code'].widget.attrs = {'class': 'form-control',}
		self.fields['PanIt_No'].widget.attrs = {'class': 'form-control',}
		self.fields['GST_No'].widget.attrs = {'class': 'form-control',}

class Ledgerformadmin(forms.ModelForm):

	class Meta:
		model = ledger1
		fields = ('name', 'group1_Name', 'Opening_Balance', 'User_Name', 'Address', 'State', 'Pin_Code', 'PanIt_No', 'GST_No', 'Closing_balance')

	def __init__(self,  *args, **kwargs):
		super(Ledgerformadmin, self).__init__(*args, **kwargs)
		self.fields['name'].widget.attrs = {'class': 'form-control',}
		self.fields['group1_Name'].widget.attrs = {'class': 'select2_demo_2 form-control', 'placeholder':"Select Group",}
		self.fields['group1_Name'].queryset = group1.objects.exclude(group_Name__icontains='Primary')
		self.fields['Opening_Balance'].widget.attrs = {'class': 'form-control',}
		self.fields['User_Name'].widget.attrs = {'class': 'form-control',}
		self.fields['Address'].widget.attrs = {'class': 'form-control',}
		self.fields['State'].widget.attrs = {'class': 'select2_demo_2 form-control',}
		self.fields['Pin_Code'].widget.attrs = {'class': 'form-control',}
		self.fields['PanIt_No'].widget.attrs = {'class': 'form-control',}
		self.fields['GST_No'].widget.attrs = {'class': 'form-control',}



class journalForm(forms.ModelForm):
	
	class Meta:
		model = journal
		fields = ('Date','By','To','Debit','Credit','narration')
		widgets = {
            'Date': DateInput(),
        }

	def __init__(self, *args, **kwargs):
		self.User = kwargs.pop('User', None)		
		self.Company = kwargs.pop('Company', None)
		super(journalForm, self).__init__(*args, **kwargs)
		self.fields['Date'].widget.attrs = {'class': 'form-control',}
		self.fields['Debit'].widget.attrs = {'class': 'form-control',}
		self.fields['Credit'].widget.attrs = {'class': 'form-control',}
		self.fields['To'].queryset = ledger1.objects.filter(Company = self.Company)
		self.fields['To'].widget.attrs = {'class': 'select2_demo_2 form-control',}
		self.fields['By'].queryset = ledger1.objects.filter(Company = self.Company)
		self.fields['By'].widget.attrs = {'class': 'select2_demo_2 form-control',}
		self.fields['narration'].widget.attrs = {'class': 'form-control',}

class pl_journalForm(forms.ModelForm):
	
	class Meta:
		model = Pl_journal
		fields = ('Date','By','To','Debit','Credit')
		widgets = {
            'Date': DateInput(),
        }

	def __init__(self, *args, **kwargs):
		self.User = kwargs.pop('User', None)		
		self.Company = kwargs.pop('Company', None)
		super(pl_journalForm, self).__init__(*args, **kwargs)
		self.fields['Date'].widget.attrs = {'class': 'form-control',}
		self.fields['Debit'].widget.attrs = {'class': 'form-control',}
		self.fields['Credit'].widget.attrs = {'class': 'form-control',}
		self.fields['To'].queryset = ledger1.objects.filter(Company = self.Company)
		self.fields['To'].widget.attrs = {'class': 'select2_demo_2 form-control',}
		self.fields['By'].queryset = ledger1.objects.filter(Company = self.Company)
		self.fields['By'].widget.attrs = {'class': 'select2_demo_2 form-control',}
		
			
class bank_journalForm(forms.ModelForm):
	
	class Meta:
		model = Bank_reconcilation
		fields = ('transaction_type','instrument_no','bank_date')
		widgets = {
            'bank_date': DateInput(),
        }

	def __init__(self, *args, **kwargs):
		super(bank_journalForm, self).__init__(*args, **kwargs)
		self.fields['transaction_type'].widget.attrs = {'class': 'select2_demo_2 form-control',}
		self.fields['instrument_no'].widget.attrs = {'class': 'form-control',}
		self.fields['bank_date'].widget.attrs = {'class': 'form-control',}


class DateRangeForm(forms.ModelForm):

	def __init__(self, *args, **kwargs):
		super(DateRangeForm, self).__init__(*args, **kwargs)
		self.fields['Start_Date'].widget.attrs = {'class': 'form-control',}
		self.fields['End_Date'].widget.attrs = {'class': 'form-control',}


	class Meta:
		model = selectdatefield
		fields = ('Start_Date', 'End_Date')
		widgets = {
			'Start_Date'  : DateInput(),
			'End_Date'    : DateInput(),
		}


class PaymentForm(forms.ModelForm):
	
	class Meta:
		model = Payment
		fields = ('date','account','total_amt')
		widgets = {
            'date': DateInput(),
        }

	def __init__(self, *args, **kwargs):
		self.User = kwargs.pop('User', None)		
		self.Company = kwargs.pop('Company', None)
		super(PaymentForm, self).__init__(*args, **kwargs)
		self.fields['date'].widget.attrs = {'class': 'form-control',}
		self.fields['account'].queryset = ledger1.objects.filter(Q(Company = self.Company) ,  Q(group1_Name__group_Name__icontains='Bank Accounts') | Q(group1_Name__group_Name__icontains='Cash-in-hand'))
		self.fields['account'].widget.attrs = {'class': 'select2_demo_2 form-control',}
		self.fields['total_amt'].widget.attrs = {'class': 'form-control',}



class ParticularspaymentForm(forms.ModelForm):
	
	class Meta:
		model = Particularspayment
		fields = ('particular','amount')

	def __init__(self, *args, **kwargs):
		self.User = kwargs.pop('User', None)		
		self.Company = kwargs.pop('Company', None)
		super(ParticularspaymentForm, self).__init__(*args, **kwargs)
		self.fields['particular'].queryset = ledger1.objects.filter(Company = self.Company).exclude(Q(group1_Name__group_Name__icontains='Bank Accounts') | Q(group1_Name__group_Name__icontains='Cash-in-hand') | Q(name__icontains='Profit & Loss A/c'))
		self.fields['particular'].widget.attrs = {'class': 'select2_demo_2 form-control',}
		self.fields['amount'].widget.attrs = {'class': 'form-control',}

Payment_formSet = inlineformset_factory(Payment, Particularspayment,
                                            form=ParticularspaymentForm, extra=6)



class ReceiptForm(forms.ModelForm):
	
	class Meta:
		model = Receipt
		fields = ('date','account','total_amt')
		widgets = {
            'date': DateInput(),
        }

	def __init__(self, *args, **kwargs):
		self.User = kwargs.pop('User', None)		
		self.Company = kwargs.pop('Company', None)
		super(ReceiptForm, self).__init__(*args, **kwargs)
		self.fields['date'].widget.attrs = {'class': 'form-control',}
		self.fields['account'].queryset = ledger1.objects.filter(Q(Company = self.Company) ,  Q(group1_Name__group_Name__icontains='Bank Accounts') | Q(group1_Name__group_Name__icontains='Cash-in-hand'))
		self.fields['account'].widget.attrs = {'class': 'select2_demo_2 form-control',}
		self.fields['total_amt'].widget.attrs = {'class': 'form-control',}



class ParticularsreceiptForm(forms.ModelForm):
	
	class Meta:
		model = Particularsreceipt
		fields = ('particular','amount')

	def __init__(self, *args, **kwargs):
		self.User = kwargs.pop('User', None)		
		self.Company = kwargs.pop('Company', None)
		super(ParticularsreceiptForm, self).__init__(*args, **kwargs)
		self.fields['particular'].queryset = ledger1.objects.filter(Company = self.Company).exclude(Q(group1_Name__group_Name__icontains='Bank Accounts') | Q(group1_Name__group_Name__icontains='Cash-in-hand') | Q(name__icontains='Profit & Loss A/c'))
		self.fields['particular'].widget.attrs = {'class': 'select2_demo_2 form-control',}
		self.fields['amount'].widget.attrs = {'class': 'form-control',}

Receipt_formSet = inlineformset_factory(Receipt, Particularsreceipt,
                                            form=ParticularsreceiptForm, extra=6)

class ContraForm(forms.ModelForm):
	
	class Meta:
		model = Contra
		fields = ('date','account','total_amt')
		widgets = {
            'date': DateInput(),
        }

	def __init__(self, *args, **kwargs):
		self.User = kwargs.pop('User', None)		
		self.Company = kwargs.pop('Company', None)
		super(ContraForm, self).__init__(*args, **kwargs)
		self.fields['date'].widget.attrs = {'class': 'form-control',}
		self.fields['account'].queryset = ledger1.objects.filter(Q(Company = self.Company) ,  Q(group1_Name__group_Name__icontains='Bank Accounts') | Q(group1_Name__group_Name__icontains='Cash-in-hand'))
		self.fields['account'].widget.attrs = {'class': 'select2_demo_2 form-control',}
		self.fields['total_amt'].widget.attrs = {'class': 'form-control',}



class ParticularscontraForm(forms.ModelForm):
	
	class Meta:
		model = Particularscontra
		fields = ('particular','amount')

	def __init__(self, *args, **kwargs):
		self.User = kwargs.pop('User', None)		
		self.Company = kwargs.pop('Company', None)
		super(ParticularscontraForm, self).__init__(*args, **kwargs)
		self.fields['particular'].queryset = ledger1.objects.filter(Q(Company = self.Company), Q(group1_Name__group_Name__icontains='Bank Accounts') | Q(group1_Name__group_Name__icontains='Cash-in-hand')).exclude(name__icontains='Profit & Loss A/c')
		self.fields['particular'].widget.attrs = {'class': 'select2_demo_2 form-control',}
		self.fields['amount'].widget.attrs = {'class': 'form-control',}

Contra_formSet = inlineformset_factory(Contra, Particularscontra,
                                            form=ParticularscontraForm, extra=6)





class MultijournaltotalForm(forms.ModelForm):
	
	class Meta:
		model = Multijournaltotal
		fields = ('Date', 'Total_Debit', 'Total_Credit','narration')
		widgets = {
            'Date': DateInput(),
        }

	def __init__(self, *args, **kwargs):
		self.Company = kwargs.pop('Company', None)
		super(MultijournaltotalForm, self).__init__(*args, **kwargs)
		self.fields['Date'].widget.attrs = {'class': 'form-control',}
		self.fields['Total_Debit'].widget.attrs = {'class': 'form-control',}
		self.fields['Total_Credit'].widget.attrs = {'class': 'form-control',}
		self.fields['narration'].widget.attrs = {'class': 'form-control',}
			

class MultijournalForm(forms.ModelForm):
	
	class Meta:
		model = Multijournal
		fields = ('By','To','Debit','Credit')


	def __init__(self, *args, **kwargs):
		self.Company = kwargs.pop('Company', None)
		super(MultijournalForm, self).__init__(*args, **kwargs)
		self.fields['Debit'].widget.attrs = {'class': 'form-control',}
		self.fields['Credit'].widget.attrs = {'class': 'form-control',}
		self.fields['To'].queryset = ledger1.objects.filter(Company=self.Company)
		self.fields['To'].widget.attrs = {'class': 'select2_demo_2 form-control',}
		self.fields['By'].queryset = ledger1.objects.filter(Company=self.Company)
		self.fields['By'].widget.attrs = {'class': 'select2_demo_2 form-control',}
		
			

Multijournal_formSet = inlineformset_factory(Multijournaltotal, Multijournal,
                                            form=MultijournalForm, extra=3)
