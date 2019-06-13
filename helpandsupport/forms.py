from helpandsupport.models import HelpCategories,Articles,Article_Answers,Article_Questions
from django import forms


class Questionform(forms.ModelForm):

	def __init__(self, *args, **kwargs):
		super(Questionform, self).__init__(*args, **kwargs)
		self.fields['text'].widget.attrs = {'class': 'form-control', 'placeholder' : 'Post Questions Here'}

	class Meta:
		model = Article_Questions
		fields = ['text',]