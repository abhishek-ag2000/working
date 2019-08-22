"""
Views
"""
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Value, Q
from django.db.models.functions import Coalesce
from django.http import HttpResponseRedirect, JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView, UpdateView, CreateView, ListView
from messaging.models import Message
from messaging.forms import MessageForm
from blog.models import Blog, BlogCategories
from consultancy.models import Consultancy
from .models import Profile, ProductActivated, RoleBasedProductActivated, Post, PostComment, ProfessionalServices, Achievement
from .forms import ProfileForm, PostForm, PostCommentForm, ServiceForm, AchievementForm, ProVerifyForm


class ProfileDetailView(LoginRequiredMixin, DetailView):
    """
    Profile Details View
    """
    context_object_name = 'profile_details'
    model = Profile
    template_name = 'user_profile/profile.html'

    def get_object(self):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        context = super(ProfileDetailView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['products_aggrement'] = ProductActivated.objects.filter(
                user=self.request.user, product__id=9, is_active=True)
            context['products_activated'] = ProductActivated.objects.filter(
                user=self.request.user, product__id=1, is_active=True)
            context['role_products'] = RoleBasedProductActivated.objects.filter(
                user=self.request.user, product__id=1, is_active=True)

            context['inbox'] = Message.objects.filter(
                reciever=self.request.user)
            context['inbox_count'] = context['inbox'].aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['blog_user'] = Blog.objects.filter(
                user=self.request.user).order_by('id')
            context['blog_count'] = context['blog_user'].aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))
            context['consultancy_user'] = Consultancy.objects.filter(
                user=self.request.user).order_by('id')
            context['consultancy_count'] = context['consultancy_user'].aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))
            context['blogs'] = Blog.objects.all().order_by('-id')
            context['consultancies'] = Consultancy.objects.all().order_by('-id')
            context['post_list'] = Post.objects.filter(
                user=self.request.user).order_by('-id')
            context['post_count'] = context['post_list'].aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))
            context['services'] = ProfessionalServices.objects.filter(
                user=self.request.user).order_by('-id')[:4]
            context['case_count'] = Achievement.objects.filter(user=self.request.user).aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['products_legal'] = ProductActivated.objects.filter(
                user=self.request.user, product__id=10, is_active=True)
        else:
            context['products_aggrement'] = ProductActivated.objects.filter(
                product__id=9, is_active=True)
            context['products_activated'] = ProductActivated.objects.filter(
                product__id=1, is_active=True)
            context['role_products'] = RoleBasedProductActivated.objects.filter(
                product__id=1, is_active=True)

            context['inbox'] = Message.objects.all()
            context['inbox_count'] = context['inbox'].aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.all().aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['services'] = ProfessionalServices.objects.all().order_by(
                '-id')[:4]
            context['case_count'] = Achievement.objects.all().aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['products_legal'] = ProductActivated.objects.filter(
                product__id=10, is_active=True)
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """
    Profile Update View
    """
    model = Profile
    form_class = ProfileForm
    template_name = 'user_profile/profile_form.html'

    def get_success_url(self, **kwargs):
        return reverse('user_profile:profiledetail')

    def get_object(self):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        context = super(ProfileUpdateView, self).get_context_data(**kwargs)
        context['profile_details'] = Profile.objects.all()
        if self.request.user.is_authenticated:
            context['products_aggrement'] = ProductActivated.objects.filter(
                user=self.request.user, product__id=9, is_active=True)
            context['products_activated'] = ProductActivated.objects.filter(
                user=self.request.user, product__id=1, is_active=True)
            context['role_products'] = RoleBasedProductActivated.objects.filter(
                user=self.request.user, product__id=1, is_active=True)

            context['inbox'] = Message.objects.filter(
                reciever=self.request.user)
            context['inbox_count'] = context['inbox'].aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['products_legal'] = ProductActivated.objects.filter(
                user=self.request.user, product__id=10, is_active=True)
        else:
            context['products_aggrement'] = ProductActivated.objects.filter(
                product__id=9, is_active=True)
            context['products_activated'] = ProductActivated.objects.filter(
                product__id=1, is_active=True)
            context['role_products'] = RoleBasedProductActivated.objects.filter(
                product__id=1, is_active=True)

            context['inbox'] = Message.objects.all()
            context['inbox_count'] = context['inbox'].aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.all().aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['products_legal'] = ProductActivated.objects.filter(
                product__id=10, is_active=True)
        return context


def specific_profile_view(request, profile_pk):
    """
    This view is used to view profile of user from another page.
    """
    profile_details = get_object_or_404(Profile, pk=profile_pk)

    get_profile = User.objects.get(profile__Name=profile_details.Name)

    if request.method == "POST":
        message_form_profile = MessageForm(request.POST or None)
        if message_form_profile.is_valid():
            msg_content = request.POST.get('msg_content')
            subject = request.POST.get('subject')
            answer = Message.objects.create(
                reciever=get_profile, sender=request.user, msg_content=msg_content, subject=subject)
            answer.save()
            return HttpResponseRedirect(profile_details.get_absolute_url())
    else:
        message_form_profile = MessageForm()

    if not request.user.is_authenticated:
        products_aggrement = ProductActivated.objects.filter(
            product__id=9, is_active=True)
        products_activated = ProductActivated.objects.filter(
            product__id=1, is_active=True)
        role_products = RoleBasedProductActivated.objects.filter(
            product__id=1, is_active=True)
        inbox = Message.objects.all()
        inbox_count = inbox.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.all().aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        products_legal = ProductActivated.objects.filter(
            product__id=10, is_active=True)

    else:
        products_aggrement = ProductActivated.objects.filter(
            user=request.user, product__id=9, is_active=True)
        products_activated = ProductActivated.objects.filter(
            user=request.user, product__id=1, is_active=True)
        role_products = RoleBasedProductActivated.objects.filter(
            user=request.user, product__id=1, is_active=True)
        inbox = Message.objects.filter(reciever=request.user)
        inbox_count = inbox.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.filter(sender=request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        products_legal = ProductActivated.objects.filter(
            user=request.user, product__id=10, is_active=True)

    blog_user = Blog.objects.filter(user=profile_details.Name).order_by('id')
    blog_count = blog_user.aggregate(the_sum=Coalesce(Count('id'), Value(0)))
    consultancy_user = Consultancy.objects.filter(
        user=profile_details.Name).order_by('id')
    consultancy_count = consultancy_user.aggregate(
        the_sum=Coalesce(Count('id'), Value(0)))
    post_list = Post.objects.filter(user=profile_details.Name).order_by('-id')
    post_count = post_list.aggregate(the_sum=Coalesce(Count('id'), Value(0)))
    services = ProfessionalServices.objects.filter(
        user=profile_details.Name).order_by('-id')[:4]
    case_count = Achievement.objects.filter(user=profile_details.Name).aggregate(
        the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

    context = {
        'profile_details': profile_details,
        'message_form_profile': message_form_profile,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
        'products_activated': products_activated,
        'blog_user': blog_user,
        'consultancy_user': consultancy_user,
        'blog_count': blog_count,
        'consultancy_count': consultancy_count,
        'post_list': post_list,
        'post_count': post_count,
        'services': services,
        'case_count': case_count,
        'role_products': role_products,
        'products_aggrement': products_aggrement,
        'products_legal': products_legal
    }
    return render(request, 'user_profile/specific_profile.html', context)


@login_required
def activate_subscription(request, product_activation_id):
    """
    To activate product from  product list view
    """
    product = ProductActivated.objects.get(pk=product_activation_id)
    product.is_active = True
    product.save()

    return redirect('ecommerce_integration:subscribedproductlist')


@login_required
def active_subscription_list_view(request, product_activation_id):
    """
    To activate product from  my subscription list view
    """
    product = ProductActivated.objects.get(pk=product_activation_id)
    product.is_active = True
    product.save()

    return redirect('ecommerce_integration:productlist')


@login_required
def deactivate_subscription(request, product_activation_id):
    """
    To deactivate product from product list view
    """
    product = ProductActivated.objects.get(pk=product_activation_id)
    product.is_active = False
    product.save()

    return redirect('ecommerce_integration:subscribedproductlist')


@login_required
def deactive_subscription_list_view(request, product_activation_id):
    """
    To deactivate product from mysubscriptions list view
    """
    product = ProductActivated.objects.get(pk=product_activation_id)
    product.is_active = False
    product.save()

    return redirect('ecommerce_integration:productlist')


@login_required
def activate_subscription_role_based_list_view(request, product_activation_id):
    """
    To activate the role based products
    """
    product = RoleBasedProductActivated.objects.get(pk=product_activation_id)
    product.is_active = True
    product.save()

    return redirect('ecommerce_integration:subscribedproductlist')


@login_required
def deactive_subscription_role_based_list_view(request, product_activation_id):
    """
    To deactivate role based products
    """
    product = RoleBasedProductActivated.objects.get(pk=product_activation_id)
    product.is_active = False
    product.save()

    return redirect('ecommerce_integration:subscribedproductlist')


class ServiceListView(ListView):
    """
    List view all services provided by professional users
    """
    model = ProfessionalServices
    template_name = 'services/service_list_details.html'

    def get_queryset(self):
        return ProfessionalServices.objects.filter(user=self.request.user).order_by('-id')

    def get_context_data(self, **kwargs):
        context = super(ServiceListView, self).get_context_data(**kwargs)
        context['categories_list'] = BlogCategories.objects.all()
        context['service_list'] = ProfessionalServices.objects.filter(
            user=self.request.user).order_by('-id')
        if self.request.user.is_authenticated:
            context['products_activated'] = ProductActivated.objects.filter(
                user=self.request.user, product__id=1, is_active=True)
            context['role_products'] = RoleBasedProductActivated.objects.filter(
                user=self.request.user, product__id=1, is_active=True)

            context['inbox'] = Message.objects.filter(
                reciever=self.request.user)
            context['inbox_count'] = context['inbox'].aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['products_legal'] = ProductActivated.objects.filter(
                user=self.request.user, product__id=10, is_active=True)
        else:
            context['products_activated'] = ProductActivated.objects.filter(
                product__id=1, is_active=True)
            context['role_products'] = RoleBasedProductActivated.objects.filter(
                product__id=1, is_active=True)

            context['inbox'] = Message.objects.all()
            context['inbox_count'] = context['inbox'].aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.all().aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['products_legal'] = ProductActivated.objects.filter(
                product__id=10, is_active=True)
        return context


def service_specific_profile_view(request, profile_pk):
    """
    Service Details View
    """
    profile_details = get_object_or_404(Profile, pk=profile_pk)

    if not request.user.is_authenticated:
        products_aggrement = ProductActivated.objects.filter(
            user=request.user, product__id=9, is_active=True)
        products_activated = ProductActivated.objects.filter(
            product__id=1, is_active=True)
        role_products = RoleBasedProductActivated.objects.filter(
            product__id=1, is_active=True)
        inbox = Message.objects.all()
        inbox_count = inbox.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.all().aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        products_legal = ProductActivated.objects.filter(
            product__id=10, is_active=True)
    else:
        products_aggrement = ProductActivated.objects.filter(
            product__id=9, is_active=True)
        products_activated = ProductActivated.objects.filter(
            user=request.user, product__id=1, is_active=True)
        role_products = RoleBasedProductActivated.objects.filter(
            user=request.user, product__id=1, is_active=True)
        inbox = Message.objects.filter(reciever=request.user)
        inbox_count = inbox.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.filter(sender=request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        products_legal = ProductActivated.objects.filter(
            user=request.user, product__id=10, is_active=True)

    blog_user = Blog.objects.filter(user=profile_details.Name).order_by('id')
    blog_count = blog_user.aggregate(the_sum=Coalesce(Count('id'), Value(0)))
    consultancy_user = Consultancy.objects.filter(
        user=profile_details.Name).order_by('id')
    consultancy_count = consultancy_user.aggregate(
        the_sum=Coalesce(Count('id'), Value(0)))
    post_list = Post.objects.filter(user=profile_details.Name).order_by('-id')
    post_count = post_list.aggregate(the_sum=Coalesce(Count('id'), Value(0)))
    services = ProfessionalServices.objects.filter(
        user=profile_details.Name).order_by('-id')
    case_count = Achievement.objects.filter(user=profile_details.Name).aggregate(
        the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

    context = {
        'profile_details': profile_details,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
        'products_activated': products_activated,
        'blog_user': blog_user,
        'consultancy_user': consultancy_user,
        'blog_count': blog_count,
        'consultancy_count': consultancy_count,
        'post_list': post_list,
        'post_count': post_count,
        'services': services,
        'case_count': case_count,
        'role_products': role_products,
        'products_aggrement': products_aggrement,
        'products_legal': products_legal
    }
    return render(request, 'services/service_list_details_2.html', context)


def search_professional_view(request):
    """
    Find Professionals View
    """
    template = 'user_profile/find_professional.html'

    user_profile = Profile.objects.filter(user_type__exact='Professional')

    query = request.GET.get('q')

    if query:
        result = user_profile.filter(
            Q(name__username__icontains=query) |
            Q(email__icontains=query) |
            Q(full_name__icontains=query) |
            Q(state__icontains=query))
    else:
        result = Profile.objects.filter(
            user_type__exact='Professional').order_by('-id')[:8]

    professional_count = result.count()

    page = request.GET.get('page', 1)
    paginator = Paginator(result, 9)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)

    if not request.user.is_authenticated:
        products_aggrement = ProductActivated.objects.filter(
            user=request.user, product__id=9, is_active=True)
        products_activated = ProductActivated.objects.filter(
            product__id=1, is_active=True)
        role_products = RoleBasedProductActivated.objects.filter(
            product__id=1, is_active=True)
        inbox = Message.objects.all()
        inbox_count = inbox.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.all().aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        products_legal = ProductActivated.objects.filter(
            product__id=10, is_active=True)
    else:
        products_aggrement = ProductActivated.objects.filter(
            product__id=9, is_active=True)
        products_activated = ProductActivated.objects.filter(
            user=request.user, product__id=1, is_active=True)
        role_products = RoleBasedProductActivated.objects.filter(
            user=request.user, product__id=1, is_active=True)
        inbox = Message.objects.filter(reciever=request.user)
        inbox_count = inbox.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.filter(sender=request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        products_legal = ProductActivated.objects.filter(
            user=request.user, product__id=10, is_active=True)

    context = {
        'professionals': result,
        'users': users,
        'professional_count': professional_count,
        'products_activated': products_activated,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
        'role_products': role_products,
        'products_aggrement': products_aggrement,
        'products_legal': products_legal
    }

    return render(request, template, context)


@login_required
def post_list_view(request):
    """
    List View for all post posted by User
    """
    post_list = Post.objects.all().order_by('-id')

    form = PostForm()

    if not request.user.is_authenticated:
        products_activated = ProductActivated.objects.filter(
            product__id=1, is_active=True)
        role_products = RoleBasedProductActivated.objects.filter(
            product__id=1, is_active=True)
        inbox = Message.objects.all()
        inbox_count = inbox.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.all().aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        blog_user = Blog.objects.all().order_by('id')
        consultancy_user = Consultancy.objects.all().order_by('id')
        blogs = Blog.objects.all().order_by('-id')
        consultancies = Consultancy.objects.all().order_by('-id')
        products_legal = ProductActivated.objects.filter(
            product__id=10, is_active=True)
    else:
        products_aggrement = ProductActivated.objects.filter(
            user=request.user, product__id=9, is_active=True)
        products_activated = ProductActivated.objects.filter(
            user=request.user, product__id=1, is_active=True)
        role_products = RoleBasedProductActivated.objects.filter(
            user=request.user, product__id=1, is_active=True)
        inbox = Message.objects.filter(reciever=request.user)
        inbox_count = inbox.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.filter(sender=request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        blog_user = Blog.objects.filter(user=request.user).order_by('id')
        consultancy_user = Consultancy.objects.filter(
            user=request.user).order_by('id')
        blogs = Blog.objects.all().order_by('-id')
        consultancies = Consultancy.objects.all().order_by('-id')
        products_legal = ProductActivated.objects.filter(
            user=request.user, product__id=10, is_active=True)

    context = {
        'post_list': post_list,
        'form': form,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
        'products_activated': products_activated,
        'blog_user': blog_user,
        'consultancy_user': consultancy_user,
        'blogs': blogs,
        'consultancies': consultancies,
        'role_products': role_products,
        'products_aggrement': products_aggrement,
        'products_legal': products_legal
    }
    return render(request, 'social/social_wall.html', context)


class PostCreateView(LoginRequiredMixin, CreateView):
    """
    Post Create View
    """
    form_class = PostForm
    template_name = 'social/social_wall.html'

    def get_success_url(self, **kwargs):
        return reverse('user_profile:social')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(PostCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(PostCreateView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['products_activated'] = ProductActivated.objects.filter(
                user=self.request.user, product__id=1, is_active=True)
            context['role_products'] = RoleBasedProductActivated.objects.filter(
                user=self.request.user, product__id=1, is_active=True)

            context['inbox'] = Message.objects.filter(
                reciever=self.request.user)
            context['inbox_count'] = context['inbox'].aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['products_legal'] = ProductActivated.objects.filter(
                user=self.request.user, product__id=10, is_active=True)
        else:
            context['products_activated'] = ProductActivated.objects.filter(
                product__id=1, is_active=True)
            context['role_products'] = RoleBasedProductActivated.objects.filter(
                product__id=1, is_active=True)

            context['inbox'] = Message.objects.all()
            context['inbox_count'] = context['inbox'].aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.all().aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['products_legal'] = ProductActivated.objects.filter(
                product__id=10, is_active=True)
        return context


def post_detail_view(request, post_pk):
    """
    Post Details View
    """
    post_details = get_object_or_404(Post, pk=post_pk)
    comments = PostComment.objects.filter(post=post_details.pk).order_by('-id')

    is_liked = False
    if post_details.like.filter(pk=request.user.id).exists():
        is_liked = True

    if request.method == "POST":
        comment_form = PostCommentForm(request.POST or None)
        if comment_form.is_valid():
            text = request.POST.get('text')
            post_comment = PostComment.objects.create(
                post=post_details, user=request.user, text=text)
            post_comment.save()
            return HttpResponseRedirect(post_details.get_absolute_url())
    else:
        comment_form = PostCommentForm()

    if not request.user.is_authenticated:
        products_aggrement = ProductActivated.objects.filter(
            user=request.user, product__id=9, is_active=True)
        products_activated = ProductActivated.objects.filter(
            product__id=1, is_active=True)
        role_products = RoleBasedProductActivated.objects.filter(
            product__id=1, is_active=True)
        inbox = Message.objects.all()
        inbox_count = inbox.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.all().aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        products_legal = ProductActivated.objects.filter(
            product__id=10, is_active=True)
    else:
        products_aggrement = ProductActivated.objects.filter(
            product__id=9, is_active=True)
        products_activated = ProductActivated.objects.filter(
            user=request.user, product__id=1, is_active=True)
        inbox = Message.objects.filter(reciever=request.user)
        inbox_count = inbox.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.filter(sender=request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        products_legal = ProductActivated.objects.filter(
            user=request.user, product__id=10, is_active=True)

    context = {
        'post_details': post_details,
        'comments': comments,
        'is_liked': is_liked,
        'total_like': post_details.total_like(),
        'comment_form': comment_form,
        'products_activated': products_activated,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
        'role_products': role_products,
        'products_aggrement': products_aggrement,
        'products_legal': products_legal
    }

    return render(request, 'social/post_details.html', context)


@login_required
def liked_post_view(request):
    """
    View for Liking a Post
    """
    post_details = get_object_or_404(
        Post, pk=request.POST.get('post_details_id'))

    is_liked = False
    if post_details.like.filter(pk=request.user.id).exists():
        post_details.like.remove(request.user)
        is_liked = False
    else:
        post_details.like.add(request.user)
        is_liked = True

    context = {
        'post_details': post_details,
        'is_liked': is_liked,
        'total_like': post_details.total_like(),
    }

    if request.is_ajax():
        html = render_to_string('social/post_like.html',
                                context, request=request)
        return JsonResponse({'form': html})


def save_all(request, form, template_name):
    """
    """
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            post_comments = PostComment.objects.all().order_by('-id')
            data['post_comment'] = render_to_string(
                'social/post_comment.html', {'post_comments': post_comments})
        else:
            data['form_is_valid'] = False
    context = {
        'form': form
    }
    data['html_form'] = render_to_string(
        template_name, context, request=request)
    return JsonResponse(data)


def post_comment_update_view(request, post_comment_pk):
    """
    View for Updating a Comment made by User
    """
    comment = get_object_or_404(PostComment, pk=post_comment_pk)
    if request.method == 'POST':
        form = PostCommentForm(request.POST, instance=comment)
    else:
        form = PostCommentForm(instance=comment)
    return save_all(request, form, 'social/post_comment_update.html')


def post_comment_delete_view(request, post_comment_pk):
    """
    View for deleting a comment made by User
    """
    data = dict()
    comment = get_object_or_404(PostComment, pk=post_comment_pk)
    if request.method == "POST":
        comment.delete()
        data['form_is_valid'] = True
        post_comments = PostComment.objects.all().order_by('-id')
        data['post_comment'] = render_to_string(
            'social/post_comment.html', {'post_comments': post_comments})
    else:
        context = {'comment': comment}
        data['html_form'] = render_to_string(
            'social/post_comment_delete.html', context, request=request)

    return JsonResponse(data)


class ServiceCreateView(LoginRequiredMixin, CreateView):
    """
    Professional User Service Create View
    """
    form_class = ServiceForm
    template_name = 'services/service_create.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(ServiceCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ServiceCreateView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['products_activated'] = ProductActivated.objects.filter(
                user=self.request.user, product__id=1, is_active=True)
            context['role_products'] = RoleBasedProductActivated.objects.filter(
                user=self.request.user, product__id=1, is_active=True)

            context['inbox'] = Message.objects.filter(
                reciever=self.request.user)
            context['inbox_count'] = context['inbox'].aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['products_legal'] = ProductActivated.objects.filter(
                user=self.request.user, product__id=10, is_active=True)
        else:
            context['products_activated'] = ProductActivated.objects.filter(
                product__id=1, is_active=True)
            context['role_products'] = RoleBasedProductActivated.objects.filter(
                product__id=1, is_active=True)

            context['inbox'] = Message.objects.all()
            context['inbox_count'] = context['inbox'].aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.all().aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['products_legal'] = ProductActivated.objects.filter(
                product__id=10, is_active=True)
        return context


class ServiceUpdateView(LoginRequiredMixin, UpdateView):
    """
    Service Update View
    """
    model = ProfessionalServices
    form_class = ServiceForm
    template_name = 'services/service_create.html'

    def get_context_data(self, **kwargs):
        context = super(ServiceUpdateView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['products_activated'] = ProductActivated.objects.filter(
                user=self.request.user, product__id=1, is_active=True)
            context['role_products'] = RoleBasedProductActivated.objects.filter(
                user=self.request.user, product__id=1, is_active=True)

            context['inbox'] = Message.objects.filter(
                reciever=self.request.user)
            context['inbox_count'] = context['inbox'].aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['products_legal'] = ProductActivated.objects.filter(
                user=self.request.user, product__id=10, is_active=True)
        else:
            context['products_activated'] = ProductActivated.objects.filter(
                product__id=1, is_active=True)
            context['role_products'] = RoleBasedProductActivated.objects.filter(
                product__id=1, is_active=True)

            context['inbox'] = Message.objects.all()
            context['inbox_count'] = context['inbox'].aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.all().aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['products_legal'] = ProductActivated.objects.filter(
                product__id=10, is_active=True)
        return context


def service_detail_view(request, service_pk):
    """
    Professional User Service Details View
    """
    service_details = get_object_or_404(ProfessionalServices, pk=service_pk)

    if not request.user.is_authenticated:
        products_aggrement = ProductActivated.objects.filter(
            user=request.user, product__id=9, is_active=True)
        products_activated = ProductActivated.objects.filter(
            product__id=1, is_active=True)
        role_products = RoleBasedProductActivated.objects.filter(
            product__id=1, is_active=True)
        inbox = Message.objects.all()
        inbox_count = inbox.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.all().aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        products_legal = ProductActivated.objects.filter(
            product__id=10, is_active=True)
    else:
        products_aggrement = ProductActivated.objects.filter(
            product__id=9, is_active=True)
        products_activated = ProductActivated.objects.filter(
            user=request.user, product__id=1, is_active=True)
        role_products = RoleBasedProductActivated.objects.filter(
            user=request.user, product__id=1, is_active=True)
        inbox = Message.objects.filter(reciever=request.user)
        inbox_count = inbox.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.filter(sender=request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        products_legal = ProductActivated.objects.filter(
            user=request.user, product__id=10, is_active=True)

    context = {
        'service_details': service_details,
        'products_activated': products_activated,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
        'role_products': role_products,
        'products_aggrement': products_aggrement,
        'products_legal': products_legal
    }

    return render(request, 'services/service_details.html', context)


def service_delete_view(request, service_pk):
    """
    Service Details View
    """
    data = dict()
    service_details = get_object_or_404(ProfessionalServices, id=service_pk)
    if request.method == "POST":
        service_details.delete()
        data['form_is_valid'] = True
        services = ProfessionalServices.objects.filter(
            user=request.user).order_by('id')
        data['service'] = render_to_string(
            'services/service_list.html', {'services': services})
    else:
        context = {'service_details': service_details}
        data['html_form'] = render_to_string(
            'services/service_delete.html', context, request=request)

    return JsonResponse(data)


class CaseCreateView(LoginRequiredMixin, CreateView):
    """
    Legal Case Create View
    """
    form_class = AchievementForm
    template_name = 'achievement/case_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(CaseCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(CaseCreateView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['products_activated'] = ProductActivated.objects.filter(
                user=self.request.user, product__id=1, is_active=True)
            context['role_products'] = RoleBasedProductActivated.objects.filter(
                user=self.request.user, product__id=1, is_active=True)
            context['inbox'] = Message.objects.filter(
                reciever=self.request.user)
            context['inbox_count'] = context['inbox'].aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['products_legal'] = ProductActivated.objects.filter(
                user=self.request.user, product__id=10, is_active=True)
        else:
            context['products_activated'] = ProductActivated.objects.filter(
                product__id=1, is_active=True)
            context['role_products'] = RoleBasedProductActivated.objects.filter(
                product__id=1, is_active=True)

            context['inbox'] = Message.objects.all()
            context['inbox_count'] = context['inbox'].aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.all().aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['products_legal'] = ProductActivated.objects.filter(
                product__id=10, is_active=True)
        return context


class CaseUpdateView(LoginRequiredMixin, UpdateView):
    """
    Achievement Update View
    """
    model = Achievement
    form_class = AchievementForm
    template_name = 'achievement/case_form.html'

    def get_context_data(self, **kwargs):
        context = super(CaseUpdateView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['products_activated'] = ProductActivated.objects.filter(
                user=self.request.user, product__id=1, is_active=True)
            context['role_products'] = RoleBasedProductActivated.objects.filter(
                user=self.request.user, product__id=1, is_active=True)
            context['inbox'] = Message.objects.filter(
                reciever=self.request.user)
            context['inbox_count'] = context['inbox'].aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['products_legal'] = ProductActivated.objects.filter(
                user=self.request.user, product__id=10, is_active=True)
        else:
            context['products_activated'] = ProductActivated.objects.filter(
                product__id=1, is_active=True)
            context['role_products'] = RoleBasedProductActivated.objects.filter(
                product__id=1, is_active=True)

            context['inbox'] = Message.objects.all()
            context['inbox_count'] = context['inbox'].aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.all().aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['products_legal'] = ProductActivated.objects.filter(
                product__id=10, is_active=True)
        return context


class CaseListView(LoginRequiredMixin, ListView):
    """
    Achievement List VIew
    """
    model = Achievement
    paginate_by = 10

    def get_queryset(self):
        return Achievement.objects.filter(user=self.request.user).order_by('-id')

    def get_template_names(self):
        return ['achievement/case_list.html']

    def get_context_data(self, **kwargs):
        context = super(CaseListView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['products_activated'] = ProductActivated.objects.filter(
                user=self.request.user, product__id=1, is_active=True)
            context['role_products'] = RoleBasedProductActivated.objects.filter(
                user=self.request.user, product__id=1, is_active=True)
            context['inbox'] = Message.objects.filter(
                reciever=self.request.user)
            context['inbox_count'] = context['inbox'].aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['products_legal'] = ProductActivated.objects.filter(
                user=self.request.user, product__id=10, is_active=True)
        else:
            context['products_activated'] = ProductActivated.objects.filter(
                product__id=1, is_active=True)
            context['role_products'] = RoleBasedProductActivated.objects.filter(
                product__id=1, is_active=True)

            context['inbox'] = Message.objects.all()
            context['inbox_count'] = context['inbox'].aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.all().aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['products_legal'] = ProductActivated.objects.filter(
                product__id=10, is_active=True)
        return context


@login_required
def case_detail_view(request, case_pk):
    """
    Achievement Details View
    """
    case_details = get_object_or_404(Achievement, pk=case_pk)

    if not request.user.is_authenticated:
        products_aggrement = ProductActivated.objects.filter(
            user=request.user, product__id=9, is_active=True)
        products_activated = ProductActivated.objects.filter(
            product__id=1, is_active=True)
        role_products = RoleBasedProductActivated.objects.filter(
            product__id=1, is_active=True)
        inbox = Message.objects.all()
        inbox_count = inbox.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.all().aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        products_legal = ProductActivated.objects.filter(
            product__id=10, is_active=True)
    else:
        products_aggrement = ProductActivated.objects.filter(
            product__id=9, is_active=True)
        products_activated = ProductActivated.objects.filter(
            user=request.user, product__id=1, is_active=True)
        role_products = RoleBasedProductActivated.objects.filter(
            user=request.user, product__id=1, is_active=True)
        inbox = Message.objects.filter(reciever=request.user)
        inbox_count = inbox.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.filter(sender=request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        products_legal = ProductActivated.objects.filter(
            user=request.user, product__id=10, is_active=True)

    context = {
        'case_details': case_details,
        'products_activated': products_activated,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
        'role_products': role_products,
        'products_aggrement': products_aggrement,
        'products_legal': products_legal
    }

    return render(request, 'achievement/case_details.html', context)


@login_required
def case_delete_view(self, request, case_pk):
    data = dict()
    case_details = get_object_or_404(Achievement, id=case_pk)
    if request.method == "POST":
        case_details.delete()
        data['form_is_valid'] = True
        case_list = Achievement.objects.filter(
            user=self.request.user).order_by('-id')
        data['cases'] = render_to_string(
            'achievement/case_list2.html', {'case_list': case_list})
    else:
        context = {'case_details': case_details}
        data['html_form'] = render_to_string(
            'achievement/case_delete.html', context, request=request)

    return JsonResponse(data)


class ProVerifyCreateView(LoginRequiredMixin, CreateView):
    """
    Professional verification Create View
    """
    form_class = ProVerifyForm
    template_name = 'ProfessionalVeriry/pro_verify_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(ProVerifyCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ProVerifyCreateView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['products_activated'] = ProductActivated.objects.filter(
                user=self.request.user, product__id=1, is_active=True)
            context['role_products'] = RoleBasedProductActivated.objects.filter(
                user=self.request.user, product__id=1, is_active=True)
            context['inbox'] = Message.objects.filter(
                reciever=self.request.user)
            context['inbox_count'] = context['inbox'].aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['products_legal'] = ProductActivated.objects.filter(
                user=self.request.user, product__id=10, is_active=True)
        else:
            context['products_activated'] = ProductActivated.objects.filter(
                product__id=1, is_active=True)
            context['role_products'] = RoleBasedProductActivated.objects.filter(
                product__id=1, is_active=True)
            context['inbox'] = Message.objects.all()
            context['inbox_count'] = context['inbox'].aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.all().aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['products_legal'] = ProductActivated.objects.filter(
                product__id=10, is_active=True)
        return context
