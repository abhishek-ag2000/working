"""
Forms
"""
from django import forms
from bracketline.forms import DateInput
from .models import *
from django.forms import inlineformset_factory



class OrganisationForm(forms.ModelForm):
    """
    Organisation Form
    """
    class Meta:
        model = Organisation
        fields = ('name', 'address', 'country', 'state','telephone_no', 'mobile_no')

    def __init__(self, *args, **kwargs):
        super(OrganisationForm, self).__init__(*args, **kwargs)

        self.fields['name'].widget.attrs = {'class': 'form-control',}
        self.fields['address'].widget.attrs = {'class': 'form-control',}
        self.fields['country'].widget.attrs = {'class': 'select2_demo_2 form-control',}
        self.fields['state'].widget.attrs = {'class': 'select2_demo_2 form-control',}
        self.fields['telephone_no'].widget.attrs = {'class': 'form-control',}
        self.fields['mobile_no'].widget.attrs = {'class': 'form-control' }


class CompanyForm(forms.ModelForm):
    """
    Company Form
    """
    class Meta:
        model = Company
        fields = ('type_of_company', 'maintain', 'bussiness_nature', 'gst_enabled','financial_year_from', 'books_begining_from', 'gst', 'pan_no',
                  'gst_registration_type', 'is_other_territory', 'way_bill', 'threshold_limit_inc', 'threshold_limit', 'interstate_apl',
                  'intrastate_apl', 'threshold_limit_intra', 'adv_receipt_tax', 'tax_liability', 'set_or_alter_gst', 'hsn',
                  'taxability', 'reverse_charge', 'input_credit', 'integrated_tax', 'central_tax', 'state_tax', 'cess',
                  'provide_lut', 'lut_bond_no', 'gst_applicable', 'applicable_from', 'applicable_to', 'tax_rate', 'purchase_tax')
        widgets = {
            'books_begining_from': DateInput(),
            'applicable_from': DateInput(),
            'applicable_to': DateInput(),
            'gst_applicable': DateInput(),
        }

    def __init__(self, *args, **kwargs):
        super(CompanyForm, self).__init__(*args, **kwargs)

        self.fields['type_of_company'].widget.attrs = {'class': 'select2_demo_2 form-control', }
        self.fields['bussiness_nature'].widget.attrs = {'class': 'select2_demo_2 form-control', }
        self.fields['maintain'].widget.attrs = {'class': 'select2_demo_2 form-control', }
        self.fields['financial_year_from'].widget.attrs = {'class': 'select2_demo_2 form-control', }
        self.fields['books_begining_from'].widget.attrs = {'class': 'form-control', }
        self.fields['gst'].widget.attrs = {'class': 'form-control', 'onchange': 'GST_No_Changed(this)', }
        self.fields['gst_enabled'].widget.attrs = {'class': 'select2_demo_2 form-control', 'onchange': 'gst_change_enability(this)', }
        self.fields['gst_registration_type'].widget.attrs = {'class': 'select2_demo_2 form-control', 'onchange': 'registration_effects(this)', }
        self.fields['pan_no'].widget.attrs = {'class': 'form-control', }
        self.fields['is_other_territory'].widget.attrs = {'class': 'js-switch', }
        self.fields['way_bill'].widget.attrs = {'class': 'select2_demo_2 form-control', 'onchange': 'waybill_change_enability(this)', }
        self.fields['threshold_limit_inc'].widget.attrs = {'class': 'form-control', }
        self.fields['threshold_limit'].widget.attrs = {'class': 'form-control', }
        self.fields['interstate_apl'].widget.attrs = {'class': 'select2_demo_2 form-control', }
        self.fields['threshold_limit_intra'].widget.attrs = {'class': 'form-control', }
        self.fields['intrastate_apl'].widget.attrs = {'class': 'select2_demo_2 form-control', }
        self.fields['taxability'].widget.attrs = {'class': 'select2_demo_2 form-control', 'onchange': 'change_taxability_stock(this)', }
        self.fields['hsn'].widget.attrs = {'class': 'form-control', }
        self.fields['set_or_alter_gst'].widget.attrs = {'class': 'select2_demo_2 form-control', 'onchange': 'gst_change_setalter_enability(this)', }
        self.fields['tax_liability'].widget.attrs = {'class': 'js-switch_2', }
        self.fields['adv_receipt_tax'].widget.attrs = {'class': 'js-switch_3', }
        self.fields['reverse_charge'].widget.attrs = {'class': 'form-control', }
        self.fields['input_credit'].widget.attrs = {'class': 'form-control', }
        self.fields['integrated_tax'].widget.attrs = {'class': 'form-control', 'step' : 'any' }
        self.fields['central_tax'].widget.attrs = {'class': 'form-control', 'step' : 'any'}
        self.fields['state_tax'].widget.attrs = {'class': 'form-control', 'step' : 'any'}
        self.fields['cess'].widget.attrs = {'class': 'form-control', 'step' : 'any'}
        self.fields['provide_lut'].widget.attrs = {'class': 'select2_demo_2 form-control', 'onchange': 'lut_details_enability(this)', }
        self.fields['lut_bond_no'].widget.attrs = {'class': 'form-control', }
        self.fields['gst_applicable'].widget.attrs = {'class': 'form-control', }
        self.fields['applicable_from'].widget.attrs = {'class': 'form-control', }
        self.fields['applicable_to'].widget.attrs = {'class': 'form-control', }
        self.fields['tax_rate'].widget.attrs = {'class': 'form-control', }
        self.fields['purchase_tax'].widget.attrs = {'class': 'select2_demo_2 form-control', }


class CompanyUpdateForm(forms.ModelForm):
    """
    Company Update Form
    """
    class Meta:
        model = Company
        fields = ('type_of_company', 'bussiness_nature', 'gst_enabled','financial_year_from', 'books_begining_from', 'gst', 'pan_no', 'gst_registration_type',
                  'is_other_territory', 'way_bill', 'threshold_limit_inc', 'threshold_limit', 'interstate_apl',
                  'intrastate_apl', 'threshold_limit_intra', 'adv_receipt_tax', 'tax_liability', 'set_or_alter_gst', 'hsn',
                  'taxability', 'reverse_charge', 'input_credit', 'integrated_tax', 'central_tax', 'state_tax', 'cess',
                  'provide_lut', 'lut_bond_no', 'gst_applicable', 'applicable_from', 'applicable_to', 'tax_rate', 'purchase_tax')
        widgets = {
            'books_begining_from': DateInput(),
            'applicable_from': DateInput(),
            'applicable_to': DateInput(),
            'gst_applicable': DateInput(),
        }

    def __init__(self, *args, **kwargs):
        super(CompanyUpdateForm, self).__init__(*args, **kwargs)
        self.fields['type_of_company'].widget.attrs = {'class': 'select2_demo_2 form-control', }
        self.fields['bussiness_nature'].widget.attrs = {'class': 'select2_demo_2 form-control', }
        self.fields['financial_year_from'].widget.attrs = {'class': 'select2_demo_2 form-control', }
        self.fields['books_begining_from'].widget.attrs = {'class': 'form-control', }
        self.fields['gst'].widget.attrs = {'class': 'form-control', }
        self.fields['gst_enabled'].widget.attrs = {'class': 'select2_demo_2 form-control', 'onchange': 'gst_change_enability(this)', }
        self.fields['gst_registration_type'].widget.attrs = {'class': 'select2_demo_2 form-control', 'onchange': 'registration_effects(this)', }
        self.fields['pan_no'].widget.attrs = {'class': 'form-control', }
        self.fields['is_other_territory'].widget.attrs = {'class': 'js-switch', }
        self.fields['way_bill'].widget.attrs = {'class': 'select2_demo_2 form-control', 'onchange': 'waybill_change_enability(this)', }
        self.fields['threshold_limit_inc'].widget.attrs = {'class': 'form-control', }
        self.fields['threshold_limit'].widget.attrs = {'class': 'form-control', }
        self.fields['interstate_apl'].widget.attrs = {'class': 'select2_demo_2 form-control', }
        self.fields['threshold_limit_intra'].widget.attrs = {'class': 'form-control', }
        self.fields['intrastate_apl'].widget.attrs = {'class': 'select2_demo_2 form-control', }
        self.fields['taxability'].widget.attrs = {'class': 'select2_demo_2 form-control', 'onchange': 'change_taxability_stock(this)', }
        self.fields['hsn'].widget.attrs = {'class': 'form-control', }
        self.fields['set_or_alter_gst'].widget.attrs = {'class': 'select2_demo_2 form-control', 'onchange': 'gst_change_setalter_enability(this)', }
        self.fields['tax_liability'].widget.attrs = {'class': 'js-switch_2', }
        self.fields['adv_receipt_tax'].widget.attrs = {'class': 'js-switch_3', }
        self.fields['reverse_charge'].widget.attrs = {'class': 'form-control', }
        self.fields['input_credit'].widget.attrs = {'class': 'form-control', }
        self.fields['integrated_tax'].widget.attrs = {'class': 'form-control', }
        self.fields['central_tax'].widget.attrs = {'class': 'form-control', }
        self.fields['state_tax'].widget.attrs = {'class': 'form-control', }
        self.fields['cess'].widget.attrs = {'class': 'form-control', }
        self.fields['provide_lut'].widget.attrs = {'class': 'select2_demo_2 form-control', 'onchange': 'lut_details_enability(this)', }
        self.fields['lut_bond_no'].widget.attrs = {'class': 'form-control', }
        self.fields['gst_applicable'].widget.attrs = {'class': 'form-control', }
        self.fields['applicable_from'].widget.attrs = {'class': 'form-control', }
        self.fields['applicable_to'].widget.attrs = {'class': 'form-control', }
        self.fields['tax_rate'].widget.attrs = {'class': 'form-control', }
        self.fields['purchase_tax'].widget.attrs = {'class': 'select2_demo_2 form-control', }


class StaticPageForm(forms.ModelForm):
    '''
    static page create form
    '''

    class Meta:
        model = StaticPage
        fields = ('name', 'title1', 'title2', 'head_bg','service_desc','portfolio_desc','team_desc','facebook_url','twitter_url','linkedin_url',)


    def __init__(self, *args, **kwargs):
        super(StaticPageForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs = {'class': 'form-control',}
        self.fields['title1'].widget.attrs = {'class': 'form-control',}
        self.fields['title2'].widget.attrs = {'class': 'form-control',}
        self.fields['head_bg'].widget.attrs = {'class': 'form-control',}
        self.fields['service_desc'].widget.attrs = {'class': 'form-control',}
        self.fields['portfolio_desc'].widget.attrs = {'class': 'form-control',}
        self.fields['team_desc'].widget.attrs = {'class': 'form-control',}
        self.fields['facebook_url'].widget.attrs = {'class': 'form-control',}
        self.fields['twitter_url'].widget.attrs = {'class': 'form-control',}
        self.fields['linkedin_url'].widget.attrs = {'class': 'form-control',}


class ServiceForm(forms.ModelForm):
    class Meta:
        model  = Service
        fields = ('name', 'desc', 'icon')

    def __init__(self, *args, **kwargs):
        super(ServiceForm, self).__init__(*args, **kwargs)
        
        self.fields['name'].widget.attrs = {'class': 'form-control',}
        self.fields['desc'].widget.attrs     = {'class': 'form-control'}
        self.fields['icon'].widget.attrs = {'class': 'form-control'}


ServiceForm_formset =  inlineformset_factory(StaticPage, Service,
                                            form=ServiceForm, extra=1, can_delete=True)

class PortfolioForm(forms.ModelForm):
    class Meta:
        model  = Portfolio
        fields = ('name', 'desc', 'image')

    def __init__(self, *args, **kwargs):
        super(PortfolioForm, self).__init__(*args, **kwargs)
        
        self.fields['name'].widget.attrs = {'class': 'form-control',}
        self.fields['desc'].widget.attrs     = {'class': 'form-control'}
        self.fields['image'].widget.attrs = {'class': 'form-control'}


PortfolioForm_formset =  inlineformset_factory(StaticPage, Portfolio,
                                            form=PortfolioForm, extra=1)

class TeamForm(forms.ModelForm):
    class Meta:
        model  = TeamMember
        fields = ('name', 'profession', 'pic','facebook_url','twitter_url','linkedin_url')

    def __init__(self, *args, **kwargs):
        super(TeamForm, self).__init__(*args, **kwargs)
        
        self.fields['name'].widget.attrs = {'class': 'form-control',}
        self.fields['profession'].widget.attrs     = {'class': 'form-control'}
        self.fields['pic'].widget.attrs = {'class': 'form-control'}
        self.fields['facebook_url'].widget.attrs = {'class': 'form-control',}
        self.fields['twitter_url'].widget.attrs     = {'class': 'form-control'}
        self.fields['linkedin_url'].widget.attrs = {'class': 'form-control'}


TeamForm_formset =  inlineformset_factory(StaticPage, TeamMember,
                                            form=TeamForm, extra=1)