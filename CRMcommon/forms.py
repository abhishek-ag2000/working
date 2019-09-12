
from django import forms
from .models import Address 
class BillingAddressForm(forms.ModelForm):

    class Meta:
        model = Address
        fields = ('address_line', 'street', 'city',
                  'state', 'postcode', 'country')

    def __init__(self, *args, **kwargs):
        account_view = kwargs.pop('account', False)

        super(BillingAddressForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs = {"class": "form-control"}
        self.fields['address_line'].widget.attrs.update({
            'placeholder': 'Address Line'})
        self.fields['street'].widget.attrs.update({
            'placeholder': 'Street'})
        self.fields['city'].widget.attrs.update({
            'placeholder': 'City'})
        self.fields['state'].widget.attrs.update({
            'placeholder': 'State'})
        self.fields['postcode'].widget.attrs.update({
            'placeholder': 'Postcode'})
        
            

        if account_view:
            self.fields['address_line'].required = True
            self.fields['street'].required = True
            self.fields['city'].required = True
            self.fields['state'].required = True
            self.fields['postcode'].required = True
            self.fields['country'].required = True
