from django.shortcuts import render

from django.views.generic import (ListView,DetailView,
								  CreateView,UpdateView,DeleteView)
from helpandsupport.models import HelpCategories,Articles,Article_Answers,Article_Questions
from django.shortcuts import get_object_or_404

# Create your views here.
class CategoriesListView(ListView):
	model = HelpCategories
	template_name = 'home.html' # <app>/<model>_<viewtype>.html
	context_object_name = 'HelpCategories'
	#ordering = ["-  "]

# Create your views here.
class CategoryDetailView(DetailView):
	model = HelpCategories
	template_name = 'catdetail.html'
	

