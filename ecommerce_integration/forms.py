"""
Forms
"""
from django import forms
from .models import ProductReview


class ProductReviewForm(forms.ModelForm):
    """
    Product Review Form
    """
    def __init__(self, *args, **kwargs):
        super(ProductReviewForm, self).__init__(*args, **kwargs)

        self.fields['name'].widget.attrs = {'class': 'form-control', 'placeholder': "Name", }
        self.fields['email'].widget.attrs = {'class': 'form-control', 'placeholder': "Email", }
        self.fields['text'].widget.attrs = {'class': 'form-control', 'placeholder': "Your review", }

    class Meta:
        model = ProductReview
        fields = ['name', 'email', 'text']
