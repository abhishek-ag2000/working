"""
Forms
"""
from django import forms
from .models import Consultancy, Answer


class ConsultancyForm(forms.ModelForm):
    """
    Consultancy Form
    """

    def __init__(self, *args, **kwargs):
        super(ConsultancyForm, self).__init__(*args, **kwargs)
        self.fields['question'].widget.attrs = {'class': 'form-control'}

    class Meta:
        model = Consultancy
        fields = ['question', ]

    def clean(self):
        cleaned_data = super(ConsultancyForm, self).clean()
        question = cleaned_data.get('question')


class AnswerForm(forms.ModelForm):
    """
    Answer Form
    """

    def __init__(self, *args, **kwargs):
        super(AnswerForm, self).__init__(*args, **kwargs)
        self.fields['text'].widget.attrs = {'class': 'form-control', 'placeholder': 'Post Answers Here'}

    class Meta:
        model = Answer
        fields = ['text', ]
