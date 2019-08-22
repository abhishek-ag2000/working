"""
Forms
"""
from django import forms
from blog.models import Blog, BlogComments

class BlogForm(forms.ModelForm):
    """
    Blog Form
    """
    def __init__(self, *args, **kwargs):
        super(BlogForm, self).__init__(*args, **kwargs)
        self.fields['category'].widget.attrs = {'class': 'select2_demo_2 form-control', 'placeholder': "Select Category", }

    blog_title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Blog
        fields = ['blog_title', 'description', 'blog_image', 'category']


class BlogSearchForm(forms.Form):
    """
    Blog Search Form
    """
    name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))


class BlogCommentForm(forms.ModelForm):
    """
    Blog Comment Form
    """
    def __init__(self, *args, **kwargs):
        super(BlogCommentForm, self).__init__(*args, **kwargs)
        self.fields['text'].widget.attrs = {'class': 'form-control', 'placeholder': 'Post Comment Here'}

    class Meta:
        model = BlogComments
        fields = ['text', ]
