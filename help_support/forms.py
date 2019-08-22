from help_support.models import HelpCategory,Articles,ArticleAnswers,ArticleQuestions, SubmitRequest
from django import forms


class Questionform(forms.ModelForm):

	def __init__(self, *args, **kwargs):
		super(Questionform, self).__init__(*args, **kwargs)
		self.fields['text'].widget.attrs = {'class': 'form-control', 'placeholder' : 'Post Questions Here'}

	class Meta:
		model = ArticleQuestions
		fields = ['text',]

class ResponseForm(forms.ModelForm):
	"""
	Submit a response form
	"""

	def __init__(self,*args,**kwargs):
		super(ResponseForm, self).__init__(*args,**kwargs)
		self.fields['email'].widget.attrs = {'class': 'form-control'}
		self.fields['subject'].widget.attrs = {'class': 'form-control'}
		self.fields['description'].widget.attrs = {'class': 'form-control', 'placeholder' : 'Please enter the details of your request. A member of our support staff will respond as soon as possible.'}
		self.fields['ticket_type'].widget.attrs = {'class': 'select2_demo_2'}

	class Meta:
		model = SubmitRequest
		fields = ['email','subject','description','ticket_type','file_upload']