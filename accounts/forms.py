from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django import forms

User = get_user_model()


class UserCreateForm(UserCreationForm):
	email = forms.EmailField()
	tandc = forms.BooleanField()
	# gives us a nested namespace for cofigurations and keepst hte configs in one place 
	class Meta:
	    fields = ("username", "email", "password1", "password2","tandc")
	    model = get_user_model()

	def __init__(self, *args, **kwargs):
		super(UserCreateForm, self).__init__(*args, **kwargs)
		# for terms and conditions checkbox
		# if check_something():
		self.fields['username'].widget.attrs = {'class': 'form-control',}
		self.fields['email'].widget.attrs = {'class': 'form-control',}
		self.fields['password1'].widget.attrs = {'class': 'form-control',}
		self.fields['password2'].widget.attrs = {'class': 'form-control',}
		self.fields['tandc'].initial  = True
		self.fields['tandc'].required = True 
		self.fields['email'].required = True 
		self.fields['username'].widget.attrs.update({'placeholder': 'Enter Username'})
		self.fields['email'].widget.attrs.update({'placeholder': 'Enter Email'})
		self.fields['password1'].widget.attrs.update({'placeholder': 'Enter Password'})
		self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm Password'})

		self.fields['tandc'].widget.attrs = {'class': 'checkbox i-checks form-control',}
		
		for fieldname in ['username', 'password1', 'password2']:
			self.fields[fieldname].help_text = None

	def clean_email(self):
		email = self.cleaned_data.get('email')
		username = self.cleaned_data.get('username')
		if email and User.objects.filter(email=email).exclude(username=username).exists():
			raise ValidationError(u'This Email addresses was already registered')
		return email

