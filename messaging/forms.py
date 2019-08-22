"""
Forms
"""
from django import forms
from .models import Message


class MessageForm(forms.ModelForm):
    """
    Messaging Form
    """

    def __init__(self, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)
        self.fields['reciever'].widget.attrs = {
            'class': 'form-control select2', }
        self.fields['subject'].widget.attrs = {'class': 'form-control', }
        self.fields['msg_content'].widget.attrs = {'class': 'form-control', }
        self.fields['attchment'].widget.attrs = {'class': 'form-control', }

    class Meta:
        model = Message
        fields = ['reciever', 'subject', 'msg_content', 'attchment']

    # def clean(self):
    #     cleaned_data = super(ConsultancyForm, self).clean()
    #     Questions = cleaned_data.get('Questions')
