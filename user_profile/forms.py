"""
Forms
"""
from django import forms
from .models import Achievement, Post, PostComment, ProfessionalServices, ProfessionalVerify, Profile


class ProfileForm(forms.ModelForm):
    """
    Profile Form
    """

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)

        self.fields['email'].widget.attrs = {'class': 'form-control', }
        self.fields['user_type'].required = False
        self.fields['user_type'].widget.attrs['disabled'] = 'disabled'
        self.fields['phone_no'].widget.attrs = {'class': 'form-control', }
        self.fields['basic_info'].widget.attrs = {'class': 'form-control', }
        self.fields['full_name'].widget.attrs = {'class': 'form-control', }
        self.fields['permanent_address'].widget.attrs = {'class': 'form-control', }
        self.fields['state'].widget.attrs = {'class': 'select2_demo_2 form-control', }
        self.fields['city'].widget.attrs = {'class': 'form-control', }
        self.fields['country'].widget.attrs = {'class': 'select2_demo_2 form-control', }

    class Meta:
        model = Profile
        fields = ('full_name', 'user_type', 'email', 'permanent_address',
                  'state', 'city', 'country', 'phone_no', 'basic_info', 'image')


class ProVerifyForm(forms.ModelForm):
    """
    Professional Verification Form
    """

    def __init__(self, *args, **kwargs):
        super(ProVerifyForm, self).__init__(*args, **kwargs)

        self.fields['product'].widget.attrs = {'class': 'select2_demo_2 form-control'}
        self.fields['phone_no'].widget.attrs = {'class': 'form-control'}
        self.fields['email'].widget.attrs = {'class': 'form-control'}

    class Meta:
        model = ProfessionalVerify
        fields = ['product', 'phone_no', 'email',
                  'upload_1', 'upload_2', 'upload_3']


class PostForm(forms.ModelForm):
    """
    Post Form
    """
    class Meta:
        model = Post
        fields = ('post',)


class PostCommentForm(forms.ModelForm):
    """
    Post Comment Form
    """

    def __init__(self, *args, **kwargs):
        super(PostCommentForm, self).__init__(*args, **kwargs)

        self.fields['text'].widget.attrs = {
            'class': 'form-control', 'placeholder': 'Post Comments Here'}

    class Meta:
        model = PostComment
        fields = ['text', ]


class ServiceForm(forms.ModelForm):
    """
    Professional Service Form
    """

    def __init__(self, *args, **kwargs):
        super(ServiceForm, self).__init__(*args, **kwargs)

        self.fields['service_name'].widget.attrs = {'class': 'form-control'}
        self.fields['details'].widget.attrs = {'class': 'form-control'}
        self.fields['service_type'].widget.attrs = {
            'class': 'form-control select2'}
        self.fields['duration'].widget.attrs = {
            'class': 'form-control select2'}
        self.fields['service_mode'].widget.attrs = {
            'class': 'form-control select2'}
        self.fields['rate'].widget.attrs = {'class': 'form-control'}

    class Meta:
        model = ProfessionalServices
        fields = ['service_name', 'details', 'service_type',
                  'duration', 'service_mode', 'rate']


class AchievementForm(forms.ModelForm):
    """
    Achievement Form
    """

    def __init__(self, *args, **kwargs):
        super(AchievementForm, self).__init__(*args, **kwargs)
        self.fields['act'].widget.attrs = {'class': 'form-control'}
        self.fields['location'].widget.attrs = {'class': 'form-control'}
        self.fields['facts'].widget.attrs = {'class': 'form-control'}
        self.fields['issue'].widget.attrs = {'class': 'form-control'}
        self.fields['argument'].widget.attrs = {'class': 'form-control'}
        self.fields['judgement'].widget.attrs = {'class': 'form-control'}
        self.fields['user_role'].widget.attrs = {'class': 'form-control'}

    class Meta:
        model = Achievement
        fields = ['legal_case', 'act', 'location', 'facts',
                  'issue', 'argument', 'judgement', 'user_role']
