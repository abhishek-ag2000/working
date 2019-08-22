"""
Forms
"""
from django import forms
from aggrement.models import Aggrement, UserAggrements


class AggrementForm(forms.ModelForm):
    """
    Aggrement Form
    """

    def __init__(self, *args, **kwargs):
        self.User = kwargs.pop('User', None)
        self.aggrement = kwargs.pop('aggrement', None)
        super(AggrementForm, self).__init__(*args, **kwargs)

        self.fields['title'].widget.attrs = {'class': 'form-control'}
        self.fields['act'].widget.attrs = {'class': 'form-control'}
        self.fields['section'].widget.attrs = {'class': 'form-control'}
        self.fields['form_type'].widget.attrs = {'class': 'select2_demo_2 form-control'}
        self.fields['category'].widget.attrs = {'class': 'select2_demo_2 form-control'}
        self.fields['textbody'].widget.attrs = {'class': 'form-control'}
        self.fields['guideline'].widget.attrs = {'class': 'form-control'}

    class Meta:
        model = Aggrement
        fields = ['title', 'act', 'section', 'form_type', 'category', 'textbody', 'guideline']


class UserAggrementForm(forms.ModelForm):
    """
    User Aggrement Form
    """
    def __init__(self, *args, **kwargs):
        self.User = kwargs.pop('User', None)
        self.aggrement = kwargs.pop('aggrement', None)
        super(UserAggrementForm, self).__init__(*args, **kwargs)

        self.fields['textbody'].widget.attrs = {'class': 'form-control', 'placeholder': 'Change aggrement text here'}
        self.fields['special_note'].widget.attrs = {'class': 'form-control'}

    class Meta:
        model = UserAggrements
        fields = ['textbody', 'special_note']
