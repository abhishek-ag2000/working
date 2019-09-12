"""
Forms
"""
from django import forms
from .models import ProductReview


class ProductToCard(forms.Form):
    """
    Product selection to add to cart
    """

    def get_choices(self):
        """
        Returns a list of tuple for 36 monthos
        """
        month_choice = []
        for i in range(1, 37):
            month_choice.append((i, i))
        return month_choice

    def __init__(self, *args, **kwargs):
        super(ProductToCard, self).__init__(*args, **kwargs)

        self.fields['month_count'] = forms.ChoiceField(
            choices=self.get_choices(),
            initial="12",
            label="Months ")
        #self.fields['month_count'].widget.attrs = {'class': 'select2_demo_2 form-control', }
        self.fields['month_count'].widget.attrs = {'onchange': 'month_count_changed(this)', }


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
