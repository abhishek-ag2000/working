"""
Forms
"""
#from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django import forms


class DateInput(forms.DateInput):
    """
    Widgets support for date input
    """
    input_type = 'date'


class CreateUserForm(UserCreationForm):
    """
    Create User Form
    """
    email = forms.EmailField()
    term_accepted = forms.BooleanField()

    class Meta:
        fields = ("username", "email", "password1", "password2", "term_accepted")
        model = get_user_model()

    def __init__(self, *args, **kwargs):
        super(CreateUserForm, self).__init__(*args, **kwargs)
        # for terms and conditions checkbox
        # if check_something():
        self.fields['username'].widget.attrs = {'class': 'form-control', }
        self.fields['email'].widget.attrs = {'class': 'form-control', }
        self.fields['password1'].widget.attrs = {'class': 'form-control', }
        self.fields['password2'].widget.attrs = {'class': 'form-control', }
        #self.fields['term_accepted'].initial = True
        self.fields['term_accepted'].required = True
        self.fields['email'].required = True
        self.fields['username'].widget.attrs.update({'placeholder': 'Enter User Name'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Enter Email'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Enter Password'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm Password'})
        self.fields['term_accepted'].widget.attrs = {'class': 'checkbox i-checks form-control', }

        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None

    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        if email and get_user_model().objects.filter(email=email).exclude(username=username).exists():
            raise ValidationError(u'This Email address was already registered')
        return email
