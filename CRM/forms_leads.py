from django import forms
from .models_leads import Lead
# from CRMcommon.models import Comment, Attachments 
from .models_teams import Teams 

class LeadForm(forms.ModelForm):
    teams_queryset = []
    teams = forms.MultipleChoiceField(choices=teams_queryset)

    def __init__(self, *args, **kwargs):
        assigned_users = kwargs.pop('assigned_to', [])
        super(LeadForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs = {"class": "form-control"}
        if self.data.get('status') == 'converted':
            self.fields['account_name'].required = True
            self.fields['email'].required = True
        self.fields['first_name'].required = False
        self.fields['last_name'].required = False
        self.fields['title'].required = True
        if assigned_users:
            self.fields['assigned_to'].queryset = assigned_users
        self.fields['assigned_to'].required = False
        for key, value in self.fields.items():

            value.widget.attrs['placeholder'] = value.label

        self.fields['first_name'].widget.attrs.update({
            'placeholder': 'First Name'})
        self.fields['last_name'].widget.attrs.update({
            'placeholder': 'Last Name'})
        self.fields['account_name'].widget.attrs.update({
            'placeholder': 'Account Name'})

        self.fields['description'].widget.attrs.update({
            'rows': '6'})
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
        self.fields["teams"].choices = [(team.get('id'), team.get('name')) for team in Teams.objects.all().values('id', 'name')]
        self.fields["teams"].required = False

    class Meta:
        model = Lead
        fields = ('assigned_to', 'first_name',
                  'last_name', 'account_name', 'title', 'email', 'status', 'source',
                  'website', 'description',
                  'address_line', 'street',
                  'city', 'state', 'postcode', 'country'
                  )
