"""
View
"""
from django.shortcuts import render

from django.views.generic import (ListView, DetailView,
                                  CreateView, UpdateView, DeleteView)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.db.models.functions import Coalesce
from django.db.models import Value, Sum, Count, F, ExpressionWrapper, Subquery, OuterRef, FloatField
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.urls import reverse

from .models import HelpCategory, Articles, ArticleAnswers, ArticleQuestions, SubmitRequest
from .forms import Questionform, ResponseForm
from ecommerce_integration.models import Product
from user_profile.models import Profile, ProductActivated, RoleBasedProductActivated
from messaging.models import Message


class HelpCategoryListView(ListView):
    """
    HelpCategoryListView
    """
    model = HelpCategory
    template_name = 'home.html'

    def get_queryset(self):
        return HelpCategory.objects.all().order_by('-id')

    def get_context_data(self, **kwargs):
        context = super(HelpCategoryListView, self).get_context_data(**kwargs)
        context['categoriest'] = HelpCategory.objects.all().order_by('-id')
        if self.request.user.is_authenticated:
            context['active_product_1'] = ProductActivated.objects.filter(user=self.request.user, product__id=1, is_active=True)
            context['role_product_1'] = RoleBasedProductActivated.objects.filter(user=self.request.user, product__id=1, is_active=True)
            context['inbox'] = Message.objects.filter(reciever=self.request.user)
            context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['product_legal'] = ProductActivated.objects.filter(user=self.request.user, product__id=10, is_active=True)
        else:
            context['active_product_1'] = ProductActivated.objects.filter(product__id=1, is_active=True)
            context['role_product_1'] = RoleBasedProductActivated.objects.filter(product__id=1, is_active=True)
            context['inbox'] = Message.objects.all()
            context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['product_legal'] = ProductActivated.objects.filter(product__id=10, is_active=True)
        return context


class HelpCategoryDetailView(DetailView):
    """
    Help Category Detail View
    """
    model = HelpCategory
    template_name = 'catdetail.html'

    def get_context_data(self, **kwargs):
        context = super(HelpCategoryDetailView, self).get_context_data(**kwargs)
        #context['categories_list'] = BlogCategories.objects.all()
        if self.request.user.is_authenticated:
            context['active_product_1'] = ProductActivated.objects.filter(user=self.request.user, product__id=1, is_active=True)
            context['role_product_1'] = RoleBasedProductActivated.objects.filter(user=self.request.user, product__id=1, is_active=True)
            context['inbox'] = Message.objects.filter(reciever=self.request.user)
            context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['product_legal'] = ProductActivated.objects.filter(user=self.request.user, product__id=10, is_active=True)
        else:
            context['active_product_1'] = ProductActivated.objects.filter(product__id=1, is_active=True)
            context['role_product_1'] = RoleBasedProductActivated.objects.filter(product__id=1, is_active=True)
            context['inbox'] = Message.objects.all()
            context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['product_legal'] = ProductActivated.objects.filter(product__id=10, is_active=True)

        return context


def article_detail_view(request, slug1, slug):
    """
    Article Detail View
    """
    categories_slug = get_object_or_404(HelpCategory, slug=slug1)
    article_details = get_object_or_404(Articles, slug=slug)
    questions = ArticleQuestions.objects.filter(Article=article_details).order_by('-id')

    if request.method == "POST":
        question_form = Questionform(request.POST or None)
        if question_form.is_valid():
            text = request.POST.get('text')
            question = ArticleQuestions.objects.create(Article=article_details, user=request.user, text=text)
            question.save()
            # return HttpResponseRedirect(article_details.get_absolute_url())
    else:
        question_form = Questionform()

    if not request.user.is_authenticated:
        product_aggrement = ProductActivated.objects.filter(user=request.user, product__id=9, is_active=True)
        product = ProductActivated.objects.filter(product__id=1, is_active=True)
        role_product = RoleBasedProductActivated.objects.filter(product__id=1, is_active=True)
        inbox = Message.objects.all()
        inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        product_legal = ProductActivated.objects.filter(product__id=10, is_active=True)
    else:
        product_aggrement = ProductActivated.objects.filter(product__id=9, is_active=True)
        product = ProductActivated.objects.filter(user=request.user, product__id=1, is_active=True)
        role_product = RoleBasedProductActivated.objects.filter(user=request.user, product__id=1, is_active=True)
        inbox = Message.objects.filter(reciever=request.user)
        inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        product_legal = ProductActivated.objects.filter(user=request.user, product__id=10, is_active=True)

    context = {
        'questions': questions,
        'question_form': question_form,
        'article_details': article_details,
        'categories_slug': categories_slug,
        'product': product,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
        'role_product': role_product,
        'product_legal': product_legal,
        'product_aggrement': product_aggrement
    }

    if request.is_ajax():
        html = render_to_string('questions.html', context, request=request)
        return JsonResponse({'form': html})

    return render(request, 'articledetail.html', context)


class RequestSubmitListView(LoginRequiredMixin, ListView):
    """
    Submit Request List View
    """
    context_object_name = 'request_list'
    model = SubmitRequest
    template_name = 'submit_request_list.html'
    paginate_by = 10

    def get_queryset(self):
        return SubmitRequest.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(RequestSubmitListView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['Products'] = ProductActivated.objects.filter(user=self.request.user,product__id = 1, is_active=True)
            context['Role_products'] = RoleBasedProductActivated.objects.filter(user=self.request.user,product__id = 1, is_active=True)
            context['inbox'] = Message.objects.filter(reciever=self.request.user)
            context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
            context['Products_legal'] = ProductActivated.objects.filter(user=self.request.user,product__id = 10, is_active=True)
        else:
            context['Products'] = ProductActivated.objects.filter(product__id = 1, is_active=True)
            context['Role_products'] = RoleBasedProductActivated.objects.filter(product__id = 1, is_active=True)
            context['inbox'] = Message.objects.all()
            context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']     
            context['Products_legal'] = ProductActivated.objects.filter(product__id = 10, is_active=True)
        return context


class RequestSubmitCreateView(LoginRequiredMixin,CreateView):
    """
    Submit Request Create View
    """
    form_class = ResponseForm
    template_name = "submit_request.html"

    def get_success_url(self, **kwargs):
        return reverse('help_support:submit_request_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(RequestSubmitCreateView, self).form_valid(form)


    def get_context_data(self, **kwargs):
        context = super(RequestSubmitCreateView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['Products'] = ProductActivated.objects.filter(user=self.request.user,product__id = 1, is_active=True)
            context['Role_products'] = RoleBasedProductActivated.objects.filter(user=self.request.user,product__id = 1, is_active=True)
            context['inbox'] = Message.objects.filter(reciever=self.request.user)
            context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum'] 
            context['Products_legal'] = ProductActivated.objects.filter(user=self.request.user,product__id = 10, is_active=True)
        else:
            context['Products'] = ProductActivated.objects.filter(product__id = 1, is_active=True)
            context['Role_products'] = RoleBasedProductActivated.objects.filter(product__id = 1, is_active=True)
            context['inbox'] = Message.objects.all()
            context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']     
            context['Products_legal'] = ProductActivated.objects.filter(product__id = 10, is_active=True)
        return context


# def save_all(request,form,template_name):
#     data = dict()
#     if request.method == 'POST':
#         if form.is_valid():
#             form.save()
#             data['form_is_valid'] = True
#             questions_list = ArticleQuestions.objects.all().order_by('-id')
#             data['questions_list'] = render_to_string('questions.html',{'questions_list':questions_list})
#         else:
#             data['form_is_valid'] = False
#     context = {

#         'form':form,
#     }
#     data['html_form'] = render_to_string(template_name,context,request=request)

#     return JsonResponse(data)

# def question_create(request):
#     if request.method == 'POST':
#         form = Questionform(request.POST or None)
#     else:
#         form = Questionform()

#     context = {
#         'form' : form,
#     }

#     return save_all(request,context,'question_create.html')
