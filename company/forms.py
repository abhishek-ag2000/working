from django import forms
from company.models import company
from accounting_double_entry.models import selectdatefield



class DateInput(forms.DateInput):
    input_type = 'date'




class companyform(forms.ModelForm):

	def __init__(self, *args, **kwargs):
		super(companyform, self).__init__(*args, **kwargs)
		self.fields['Name'].widget.attrs = {'class': 'form-control',}
		self.fields['Type_of_company'].widget.attrs = {'class': 'select2_demo_2 form-control',}
		self.fields['bussiness_nature'].widget.attrs = {'class': 'select2_demo_2 form-control',}
		self.fields['maintain'].widget.attrs = {'class': 'select2_demo_2 form-control',}
		self.fields['Address'].widget.attrs = {'class': 'form-control',}
		self.fields['Country'].widget.attrs = {'class': 'form-control',}
		self.fields['State'].widget.attrs = {'class': 'select2_demo_2 form-control',}
		self.fields['Pincode'].widget.attrs = {'class': 'form-control',}
		self.fields['Telephone_No'].widget.attrs = {'class': 'form-control',}
		self.fields['Mobile_No'].widget.attrs = {'class': 'form-control',}
		self.fields['Financial_Year_From'].widget.attrs = {'class': 'form-control select2',}
		self.fields['Books_Begining_From'].widget.attrs = {'class': 'form-control',}
		self.fields['gst'].widget.attrs = {'class': 'form-control',}
		self.fields['gst_enabled'].widget.attrs = {'class': 'js-switch',}
		self.fields['composite_enable'].widget.attrs = {'class': 'js-switch_2',}
		self.fields['enable_purchase'].widget.attrs = {'class': 'js-switch_3',}
		self.fields['enable_sales'].widget.attrs = {'class': 'js-switch_4',}
		self.fields['pan'].widget.attrs = {'class': 'form-control',}


	class Meta:
		model = company
		fields = ('Name', 'Type_of_company', 'maintain', 'bussiness_nature', 'gst_enabled','composite_enable','enable_purchase', 'enable_sales','Address','Country','State','Pincode','Telephone_No','Mobile_No','Financial_Year_From','Books_Begining_From','gst','pan')
		widgets = {
            'Books_Begining_From': DateInput(),
        }

class companyupdateform(forms.ModelForm):

	def __init__(self, *args, **kwargs):
		super(companyupdateform, self).__init__(*args, **kwargs)
		self.fields['Name'].widget.attrs = {'class': 'form-control',}
		self.fields['Type_of_company'].widget.attrs = {'class': 'select2_demo_2 form-control',}
		self.fields['bussiness_nature'].widget.attrs = {'class': 'select2_demo_2 form-control',}
		self.fields['Address'].widget.attrs = {'class': 'form-control',}
		self.fields['Country'].widget.attrs = {'class': 'form-control',}
		self.fields['State'].widget.attrs = {'class': 'select2_demo_2 form-control',}
		self.fields['Pincode'].widget.attrs = {'class': 'form-control',}
		self.fields['Telephone_No'].widget.attrs = {'class': 'form-control',}
		self.fields['Mobile_No'].widget.attrs = {'class': 'form-control',}
		self.fields['Financial_Year_From'].widget.attrs = {'class': 'form-control select2',}
		self.fields['Books_Begining_From'].widget.attrs = {'class': 'form-control',}
		self.fields['gst'].widget.attrs = {'class': 'form-control',}
		self.fields['gst_enabled'].widget.attrs = {'class': 'js-switch',}
		self.fields['composite_enable'].widget.attrs = {'class': 'js-switch_2',}
		self.fields['enable_purchase'].widget.attrs = {'class': 'js-switch_3',}
		self.fields['enable_sales'].widget.attrs = {'class': 'js-switch_4',}
		self.fields['pan'].widget.attrs = {'class': 'form-control',}


	class Meta:
		model = company
		fields = ('Name', 'Type_of_company', 'bussiness_nature', 'gst_enabled','composite_enable','enable_purchase', 'enable_sales','Address','Country','State','Pincode','Telephone_No','Mobile_No','Financial_Year_From','Books_Begining_From','gst','pan')
		widgets = {
            'Books_Begining_From': DateInput(),
        }






