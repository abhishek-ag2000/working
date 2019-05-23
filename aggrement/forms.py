from django import forms
from aggrement.models import Aggrement, User_aggrement

class Aggrement_form(forms.ModelForm):

	def __init__(self, *args, **kwargs):
		self.User = kwargs.pop('User', None)		
		self.aggrement = kwargs.pop('aggrement', None)
		super(Aggrement_form, self).__init__(*args, **kwargs)
		self.fields['title'].widget.attrs = {'class': 'form-control'}
		self.fields['act'].widget.attrs = {'class': 'form-control'}
		self.fields['section'].widget.attrs = {'class': 'form-control'}
		self.fields['form_type'].widget.attrs = {'class': 'select2_demo_2 form-control'}
		self.fields['category'].widget.attrs = {'class': 'select2_demo_2 form-control'}
		self.fields['textbody'].widget.attrs = {'class': 'form-control'}
		self.fields['guideline'].widget.attrs = {'class': 'form-control'}

	class Meta:
		model = Aggrement
		fields = ['title','act','section', 'form_type','category','textbody','guideline']




class User_aggrement_form(forms.ModelForm):

	def __init__(self, *args, **kwargs):
		self.User = kwargs.pop('User', None)		
		self.aggrement = kwargs.pop('aggrement', None)
		super(User_aggrement_form, self).__init__(*args, **kwargs)
		self.fields['textbody'].widget.attrs = {'class': 'form-control', 'placeholder' : 'Change aggrement text here'}
		self.fields['special_note'].widget.attrs = {'class': 'form-control'}

	class Meta:
		model = User_aggrement
		fields = ['textbody','special_note']