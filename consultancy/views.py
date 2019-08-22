"""
View
"""
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Value, Count, Q
from django.db.models.functions import Coalesce
from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from user_profile.models import ProductActivated, RoleBasedProductActivated
from messaging.models import Message
from .models import Consultancy, Answer
from .forms import ConsultancyForm, AnswerForm


class ConsultancyListView(ListView):
    """
    Consultancy List View
    """
    model = Consultancy
    paginate_by = 10

    def get_queryset(self):
        return Consultancy.objects.all().order_by('-id')

    def get_context_data(self, **kwargs):
        context = super(ConsultancyListView, self).get_context_data(**kwargs)
        context['consultancy_count'] = Consultancy.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        if self.request.user.is_authenticated:
            context['active_product_1'] = ProductActivated.objects.filter(user=self.request.user, product__id=1, is_active=True)
            context['role_product_1'] = RoleBasedProductActivated.objects.filter(user=self.request.user, product__id=1, is_active=True)
            context['inbox'] = Message.objects.filter(reciever=self.request.user)
            context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['products_legal'] = ProductActivated.objects.filter(user=self.request.user, product__id=10, is_active=True)
        else:
            context['active_product_1'] = ProductActivated.objects.filter(product__id=1, is_active=True)
            context['role_product_1'] = RoleBasedProductActivated.objects.filter(product__id=1, is_active=True)
            context['inbox'] = Message.objects.all()
            context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['products_legal'] = ProductActivated.objects.filter(product__id=10, is_active=True)
        return context


class MyConsultancyListView(LoginRequiredMixin, ListView):
    """
    My Consultancy List View
    """
    model = Consultancy
    paginate_by = 6

    def get_queryset(self):
        return Consultancy.objects.filter(user=self.request.user).order_by('-id')

    def get_template_names(self):
        if True:
            return ['consultancy/myconsultancy.html']
        else:
            return ['consultancy/consultancy_list.html']

    def get_context_data(self, **kwargs):
        context = super(MyConsultancyListView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['active_product_1'] = ProductActivated.objects.filter(user=self.request.user, product__id=1, is_active=True)
            context['role_product_1'] = RoleBasedProductActivated.objects.filter(user=self.request.user, product__id=1, is_active=True)
            context['inbox'] = Message.objects.filter(reciever=self.request.user)
            context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['products_legal'] = ProductActivated.objects.filter(user=self.request.user, product__id=10, is_active=True)
        else:
            context['active_product_1'] = ProductActivated.objects.filter(product__id=1, is_active=True)
            context['role_product_1'] = RoleBasedProductActivated.objects.filter(product__id=1, is_active=True)
            context['inbox'] = Message.objects.all()
            context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['products_legal'] = ProductActivated.objects.filter(product__id=10, is_active=True)
        return context


def consultancy_detail(request, consultancy_pk):
    consultancy_details = get_object_or_404(Consultancy, pk=consultancy_pk)
    comments = Answer.objects.filter(question=consultancy_details.pk).order_by('-id')

    is_liked = False
    if consultancy_details.like.filter(pk=request.user.id).exists():
        is_liked = True

    if request.method == "POST":
        answer_form = AnswerForm(request.POST or None)
        if answer_form.is_valid():
            text = request.POST.get('text')
            answer = Answer.objects.create(question=consultancy_details, user=request.user, text=text)
            answer.save()
            return HttpResponseRedirect(consultancy_details.get_absolute_url())
    else:
        answer_form = AnswerForm()

    like_user = consultancy_details.like.all()[:5]

    if not request.user.is_authenticated:
        product_aggrement = ProductActivated.objects.filter(user=request.user, product__id=9, is_active=True)
        product = ProductActivated.objects.filter(product__id=1, is_active=True)
        role_product = RoleBasedProductActivated.objects.filter(product__id=1, is_active=True)
        inbox = Message.objects.all()
        inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        products_legal = ProductActivated.objects.filter(product__id=10, is_active=True)
    else:
        product_aggrement = ProductActivated.objects.filter(product__id=9, is_active=True)
        product = ProductActivated.objects.filter(user=request.user, product__id=1, is_active=True)
        role_product = RoleBasedProductActivated.objects.filter(user=request.user, product__id=1, is_active=True)
        inbox = Message.objects.filter(reciever=request.user)
        inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        products_legal = ProductActivated.objects.filter(user=request.user, product__id=10, is_active=True)

    context = {
        'consultancy_details': consultancy_details,
        'comments': comments,
        'is_liked': is_liked,
        'total_like': consultancy_details.total_like(),
        'answer_form': answer_form,
        'product': product,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
        'role_product': role_product,
        'like_user': like_user,
        'product_aggrement': product_aggrement,
        'products_legal': products_legal
    }

    return render(request, 'consultancy/consultancy_details.html', context)


@login_required
def liked_post(request):
    consultancy_details = get_object_or_404(Consultancy, pk=request.POST.get('consultancy_details_id'))
    is_liked = False
    if consultancy_details.like.filter(pk=request.user.id).exists():
        consultancy_details.like.remove(request.user)
        is_liked = False
    else:
        consultancy_details.like.add(request.user)
        is_liked = True

    context = {
        'consultancy_details': consultancy_details,
        'is_liked': is_liked,
        'total_like': consultancy_details.total_like(),
    }

    if request.is_ajax():
        html = render_to_string('consultancy/consultancy_like.html', context, request=request)
        return JsonResponse({'form': html})


class ConsultancyCreateView(LoginRequiredMixin, CreateView):
    """
    Consultancy Create View
    """
    form_class = ConsultancyForm
    template_name = "Consultancy/consultancy_form.html"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(ConsultancyCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ConsultancyCreateView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['active_product_1'] = ProductActivated.objects.filter(user=self.request.user, product__id=1, is_active=True)
            context['role_product_1'] = RoleBasedProductActivated.objects.filter(user=self.request.user, product__id=1, is_active=True)
            context['inbox'] = Message.objects.filter(reciever=self.request.user)
            context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['products_legal'] = ProductActivated.objects.filter(user=self.request.user, product__id=10, is_active=True)
        else:
            context['active_product_1'] = ProductActivated.objects.filter(product__id=1, is_active=True)
            context['role_product_1'] = RoleBasedProductActivated.objects.filter(product__id=1, is_active=True)
            context['inbox'] = Message.objects.all()
            context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['products_legal'] = ProductActivated.objects.filter(product__id=10, is_active=True)
        return context


class ConsultancyUpdateView(LoginRequiredMixin, UpdateView):
    """
    Consultancy Update View
    """
    model = Consultancy
    form_class = ConsultancyForm
    template_name = "Consultancy/consultancy_form.html"

    def get_context_data(self, **kwargs):
        context = super(ConsultancyUpdateView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['active_product_1'] = ProductActivated.objects.filter(user=self.request.user, product__id=1, is_active=True)
            context['role_product_1'] = RoleBasedProductActivated.objects.filter(user=self.request.user, product__id=1, is_active=True)
            context['inbox'] = Message.objects.filter(reciever=self.request.user)
            context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['products_legal'] = ProductActivated.objects.filter(user=self.request.user, product__id=10, is_active=True)
        else:
            context['active_product_1'] = ProductActivated.objects.filter(product__id=1, is_active=True)
            context['role_product_1'] = RoleBasedProductActivated.objects.filter(product__id=1, is_active=True)
            context['inbox'] = Message.objects.all()
            context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['products_legal'] = ProductActivated.objects.filter(product__id=10, is_active=True)
        return context


def save_all_question(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            queries = Consultancy.objects.all().order_by('-id')
            data['query'] = render_to_string('Consultancy/Questions.html', {'queries': queries})
        else:
            data['form_is_valid'] = False
    context = {
        'form': form
    }
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)


def query_update(request, id):
    query_details = get_object_or_404(Consultancy, id=id)
    if request.method == 'POST':
        form = ConsultancyForm(request.POST, instance=query_details)
    else:
        form = ConsultancyForm(instance=query_details)
    return save_all_question(request, form, 'Consultancy/consultancy_update.html')


def query_delete(request, id):
    data = dict()
    query_details = get_object_or_404(Consultancy, id=id)
    if request.method == "POST":
        query_details.delete()
        data['form_is_valid'] = True
        queries = Consultancy.objects.all().order_by('-id')
        data['query'] = render_to_string('Consultancy/Questions.html', {'queries': queries})
    else:
        context = {'query_details': query_details}
        data['html_form'] = render_to_string('Consultancy/consultancy_confirm_delete.html', context, request=request)

    return JsonResponse(data)


def save_all_answer(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            answers = Answer.objects.all().order_by('-id')
            data['comments'] = render_to_string('Consultancy/answers.html', {'answers': answers})
        else:
            data['form_is_valid'] = False
    context = {
        'form': form
    }
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)


def answer_update(request, id):
    answer = get_object_or_404(Answer, id=id)
    if request.method == 'POST':
        form = AnswerForm(request.POST, instance=answer)
    else:
        form = AnswerForm(instance=answer)
    return save_all_answer(request, form, 'Consultancy/answer_update.html')


def answer_delete(request, id):
    data = dict()
    answer = get_object_or_404(Answer, id=id)
    if request.method == "POST":
        answer.delete()
        data['form_is_valid'] = True
        answers = Answer.objects.all().order_by('-id')
        data['comments'] = render_to_string('Consultancy/answers.html', {'answers': answers})
    else:
        context = {'answer': answer}
        data['html_form'] = render_to_string('Consultancy/answer_delete.html', context, request=request)

    return JsonResponse(data)


def search(request):
    template = 'Consultancy/consultancy_list.html'

    query = request.GET.get('q')

    if query:
        result = Consultancy.objects.filter(Q(question__icontains=query) | Q(date__icontains=query))
    else:
        result = Consultancy.objects.all().order_by('id')

    if not request.user.is_authenticated:
        product_aggrement = ProductActivated.objects.filter(user=request.user, product__id=9, is_active=True)
        product = ProductActivated.objects.filter(product__id=1, is_active=True)
        role_product = RoleBasedProductActivated.objects.filter(product__id=1, is_active=True)
        inbox = Message.objects.all()
        inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        products_legal = ProductActivated.objects.filter(product__id=10, is_active=True)
    else:
        product_aggrement = ProductActivated.objects.filter(product__id=9, is_active=True)
        product = ProductActivated.objects.filter(user=request.user, product__id=1, is_active=True)
        role_product = RoleBasedProductActivated.objects.filter(user=request.user, product__id=1, is_active=True)
        inbox = Message.objects.filter(reciever=request.user)
        inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        products_legal = ProductActivated.objects.filter(user=request.user, product__id=10, is_active=True)

    context = {
        'consultancy_list': result,
        'product': product,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
        'role_product': role_product,
        'product_aggrement': product_aggrement,
        'products_legal': products_legal
    }

    return render(request, template, context)
