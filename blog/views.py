"""
View
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Value, Count
from django.db.models.functions import Coalesce
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from user_profile.models import ProductActivated, RoleBasedProductActivated
from messaging.models import Message
from .models import Blog, BlogCategories, BlogComments
from .forms import BlogForm, BlogCommentForm


class BlogListView(ListView):
    """
    Blog List View
    """
    model = Blog
    paginate_by = 3

    def get_template_names(self):
        return ['blog/view_blogs.html']

    def get_queryset(self):
        return Blog.objects.all().order_by('-blog_views')[:20]

    def get_context_data(self, **kwargs):
        context = super(BlogListView, self).get_context_data(**kwargs)
        context['categories_list'] = BlogCategories.objects.all()

        if self.request.user.is_authenticated:
            context['active_product_1'] = ProductActivated.objects.filter(user=self.request.user, product__id=1, is_active=True)
            context['role_products'] = RoleBasedProductActivated.objects.filter(user=self.request.user, product__id=1, is_active=True)
            context['inbox'] = Message.objects.filter(reciever=self.request.user)
            context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['products_legal'] = ProductActivated.objects.filter(user=self.request.user, product__id=10, is_active=True)
        else:
            context['active_product_1'] = ProductActivated.objects.filter(product__id=1, is_active=True)
            context['role_products'] = RoleBasedProductActivated.objects.filter(product__id=1, is_active=True)
            context['inbox'] = Message.objects.all()
            context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['products_legal'] = ProductActivated.objects.filter(product__id=10, is_active=True)
        return context


class BlogLikedListView(ListView):
    """
    Blog Liked List View
    """
    model = Blog
    paginate_by = 3

    def get_template_names(self):
        return['blog/blog_by_likes.html']

    def get_queryset(self):
        return Blog.objects.annotate(like_count=Count('likes')).order_by('-like_count')[:20]

    def get_context_data(self, **kwargs):
        context = super(BlogLikedListView, self).get_context_data(**kwargs)
        context['categories_list'] = BlogCategories.objects.all()

        if self.request.user.is_authenticated:
            context['active_product_1'] = ProductActivated.objects.filter(user=self.request.user, product__id=1, is_active=True)
            context['role_products'] = RoleBasedProductActivated.objects.filter(user=self.request.user, product__id=1, is_active=True)
            context['inbox'] = Message.objects.filter(reciever=self.request.user)
            context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['products_legal'] = ProductActivated.objects.filter(user=self.request.user, product__id=10, is_active=True)
        else:
            context['active_product_1'] = ProductActivated.objects.filter(product__id=1, is_active=True)
            context['role_products'] = RoleBasedProductActivated.objects.filter(product__id=1, is_active=True)
            context['inbox'] = Message.objects.all()
            context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['products_legal'] = ProductActivated.objects.filter(product__id=10, is_active=True)
        return context


class BlogLatestListView(ListView):
    """
    Blog Latest List View
    """
    model = Blog
    paginate_by = 3

    def get_template_names(self):
        return ['blog/latest_blog.html']

    def get_queryset(self):
        return Blog.objects.all().order_by('-id')

    def get_context_data(self, **kwargs):
        context = super(BlogLatestListView, self).get_context_data(**kwargs)
        context['categories_list'] = BlogCategories.objects.all()
        if self.request.user.is_authenticated:
            context['active_product_1'] = ProductActivated.objects.filter(user=self.request.user, product__id=1, is_active=True)
            context['role_products'] = RoleBasedProductActivated.objects.filter(user=self.request.user, product__id=1, is_active=True)
            context['inbox'] = Message.objects.filter(reciever=self.request.user)
            context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['products_legal'] = ProductActivated.objects.filter(user=self.request.user, product__id=10, is_active=True)
        else:
            context['active_product_1'] = ProductActivated.objects.filter(product__id=1, is_active=True)
            context['role_products'] = RoleBasedProductActivated.objects.filter(product__id=1, is_active=True)
            context['inbox'] = Message.objects.all()
            context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['products_legal'] = ProductActivated.objects.filter(product__id=10, is_active=True)
        return context


class BlogCategoryListView(LoginRequiredMixin, ListView):
    """
    Blog Category List View
    """
    model = Blog
    paginate_by = 3

    def get_queryset(self):
        return Blog.objects.filter(user=self.request.user).order_by('id')

    def get_context_data(self, **kwargs):
        context = super(BlogCategoryListView, self).get_context_data(**kwargs)
        context['categories_list'] = BlogCategories.objects.all()
        if self.request.user.is_authenticated:
            context['active_product_1'] = ProductActivated.objects.filter(user=self.request.user, product__id=1, is_active=True)
            context['role_products'] = RoleBasedProductActivated.objects.filter(user=self.request.user, product__id=1, is_active=True)
            context['inbox'] = Message.objects.filter(reciever=self.request.user)
            context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['products_legal'] = ProductActivated.objects.filter(user=self.request.user, product__id=10, is_active=True)
        else:
            context['active_product_1'] = ProductActivated.objects.filter(product__id=1, is_active=True)
            context['role_products'] = RoleBasedProductActivated.objects.filter(product__id=1, is_active=True)
            context['inbox'] = Message.objects.all()
            context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['products_legal'] = ProductActivated.objects.filter(product__id=10, is_active=True)
        return context


class BlogAllListView(ListView):
    """
    Blog All List View
    """
    model = Blog
    paginate_by = 3

    def get_template_names(self):
        return ['blog/all_blogs.html']

    def get_queryset(self):
        return Blog.objects.all().order_by('id')

    def get_context_data(self, **kwargs):
        context = super(BlogAllListView, self).get_context_data(**kwargs)
        context['categories_list'] = BlogCategories.objects.all()
        if self.request.user.is_authenticated:
            context['active_product_1'] = ProductActivated.objects.filter(user=self.request.user, product__id=1, is_active=True)
            context['role_products'] = RoleBasedProductActivated.objects.filter(user=self.request.user, product__id=1, is_active=True)
            context['inbox'] = Message.objects.filter(reciever=self.request.user)
            context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['products_legal'] = ProductActivated.objects.filter(user=self.request.user, product__id=10, is_active=True)
        else:
            context['active_product_1'] = ProductActivated.objects.filter(product__id=1, is_active=True)
            context['role_products'] = RoleBasedProductActivated.objects.filter(product__id=1, is_active=True)
            context['inbox'] = Message.objects.all()
            context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['products_legal'] = ProductActivated.objects.filter(product__id=10, is_active=True)
        return context


def post_detail(request, blog_pk):
    """
    blog post view
    """
    blog_details = get_object_or_404(Blog, pk=blog_pk)
    blogcomments = BlogComments.objects.filter(questions=blog_details.pk).order_by('-id')

    blog_details.blog_views = blog_details.blog_views + 1
    blog_details.save()

    is_liked = False
    if blog_details.likes.filter(pk=request.user.id).exists():
        is_liked = True

    if request.method == "POST":
        blog_comment_form = BlogCommentForm(request.POST or None)
        if blog_comment_form.is_valid():
            text = request.POST.get('text')
            answer = BlogComments.objects.create(questions=blog_details, user=request.user, text=text)
            answer.save()
            return HttpResponseRedirect(blog_details.get_absolute_url())
    else:
        blog_comment_form = BlogCommentForm()

    if not request.user.is_authenticated:
        products_aggrement = ProductActivated.objects.filter(user=request.user, product__id=9, is_active=True)
        products = ProductActivated.objects.filter(product__id=1, is_active=True)
        role_products = RoleBasedProductActivated.objects.filter(product__id=1, is_active=True)
        inbox = Message.objects.all()
        inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        products_legal = ProductActivated.objects.filter(product__id=10, is_active=True)
    else:
        products_aggrement = ProductActivated.objects.filter(product__id=9, is_active=True)
        products = ProductActivated.objects.filter(user=request.user, product__id=1, is_active=True)
        role_products = RoleBasedProductActivated.objects.filter(user=request.user, product__id=1, is_active=True)
        inbox = Message.objects.filter(reciever=request.user)
        inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        products_legal = ProductActivated.objects.filter(user=request.user, product__id=10, is_active=True)

    context = {

        'blogcomments'		: blogcomments,
        'blog_comment_form'	: blog_comment_form,
        'blog_details': blog_details,
        'is_liked': is_liked,
        'total_likes': blog_details.total_likes(),
        'products'	: products,
        'categories_list': BlogCategories.objects.all(),
        'inbox'			: inbox,
        'inbox_count'	: inbox_count,
        'send_count'	: send_count,
        'role_products': role_products,
        'products_legal': products_legal,
        'products_aggrement': products_aggrement
    }

    return render(request, 'blog/blog_details.html', context)


@login_required
def like_post(request):
    """
    List Post
    """
    blog_details = get_object_or_404(Blog, pk=request.POST.get('blog_details_id'))
    is_liked = False
    if blog_details.likes.filter(pk=request.user.id).exists():
        blog_details.likes.remove(request.user)
        is_liked = False
    else:
        blog_details.likes.add(request.user)
        is_liked = True

    context = {
        'blog_details': blog_details,
        'is_liked': is_liked,
        'total_likes': blog_details.total_likes(),
    }

    if request.is_ajax():
        html = render_to_string('blog/like_section.html', context, request=request)
        return JsonResponse({'form': html})


class BlogCreateView(LoginRequiredMixin, CreateView):
    """
    Blog Create View
    """
    form_class = BlogForm
    template_name = 'blog/blog_form.html'

    def get_success_url(self, **kwargs):
        blog_list = Blog.objects.all().order_by('-id')
        for blog in blog_list:
            return reverse('blog:blogdetail', kwargs={'blog_pk': blog.pk})

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(BlogCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(BlogCreateView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['active_product_1'] = ProductActivated.objects.filter(user=self.request.user, product__id=1, is_active=True)
            context['role_products'] = RoleBasedProductActivated.objects.filter(user=self.request.user, product__id=1, is_active=True)
            context['inbox'] = Message.objects.filter(reciever=self.request.user)
            context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['products_legal'] = ProductActivated.objects.filter(user=self.request.user, product__id=10, is_active=True)
        else:
            context['active_product_1'] = ProductActivated.objects.filter(product__id=1, is_active=True)
            context['role_products'] = RoleBasedProductActivated.objects.filter(product__id=1, is_active=True)
            context['inbox'] = Message.objects.all()
            context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['products_legal'] = ProductActivated.objects.filter(product__id=10, is_active=True)
        return context


class BlogUpdateView(LoginRequiredMixin, UpdateView):
    """
    Blog Update View
    """
    model = Blog
    form_class = BlogForm
    template_name = 'blog/blog_form.html'

    def get_object(self):
        return get_object_or_404(Blog, pk=self.kwargs['blog_pk'])

    def get_context_data(self, **kwargs):
        context = super(BlogUpdateView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['active_product_1'] = ProductActivated.objects.filter(user=self.request.user, product__id=1, is_active=True)
            context['role_products'] = RoleBasedProductActivated.objects.filter(user=self.request.user, product__id=1, is_active=True)
            context['inbox'] = Message.objects.filter(reciever=self.request.user)
            context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['products_legal'] = ProductActivated.objects.filter(user=self.request.user, product__id=10, is_active=True)
        else:
            context['active_product_1'] = ProductActivated.objects.filter(product__id=1, is_active=True)
            context['role_products'] = RoleBasedProductActivated.objects.filter(product__id=1, is_active=True)
            context['inbox'] = Message.objects.all()
            context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['products_legal'] = ProductActivated.objects.filter(product__id=10, is_active=True)
        return context


class BlogDeleteView(LoginRequiredMixin, DeleteView):
    """
    Blog Delete View
    """
    model = Blog
    success_url = reverse_lazy("blog:bloglist")

    def get_object(self):
        return get_object_or_404(Blog, pk=self.kwargs['blog_pk'])

    def get_context_data(self, **kwargs):
        context = super(BlogDeleteView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['active_product_1'] = ProductActivated.objects.filter(user=self.request.user, product__id=1, is_active=True)
            context['role_products'] = RoleBasedProductActivated.objects.filter(user=self.request.user, product__id=1, is_active=True)
            context['inbox'] = Message.objects.filter(reciever=self.request.user)
            context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['products_legal'] = ProductActivated.objects.filter(user=self.request.user, product__id=10, is_active=True)
        else:
            context['active_product_1'] = ProductActivated.objects.filter(product__id=1, is_active=True)
            context['role_products'] = RoleBasedProductActivated.objects.filter(product__id=1, is_active=True)
            context['inbox'] = Message.objects.all()
            context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['products_legal'] = ProductActivated.objects.filter(product__id=10, is_active=True)
        return context


class CategoryListView(ListView):
    """
    Category List View
    """
    model = BlogCategories
    template_name = 'blog/blog_list.html'
    paginate_by = 6

    def get_queryset(self):
        return Blog.objects.order_by('-id')

    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['active_product_1'] = ProductActivated.objects.filter(user=self.request.user, product__id=1, is_active=True)
            context['role_products'] = RoleBasedProductActivated.objects.filter(user=self.request.user, product__id=1, is_active=True)
            context['inbox'] = Message.objects.filter(reciever=self.request.user)
            context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['products_legal'] = ProductActivated.objects.filter(user=self.request.user, product__id=10, is_active=True)
        else:
            context['active_product_1'] = ProductActivated.objects.filter(product__id=1, is_active=True)
            context['role_products'] = RoleBasedProductActivated.objects.filter(product__id=1, is_active=True)
            context['inbox'] = Message.objects.all()
            context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['products_legal'] = ProductActivated.objects.filter(product__id=10, is_active=True)
        return context


class HelpCategoryDetailView(DetailView):
    """
    Category Detail View
    """
    context_object_name = 'category_details'
    model = BlogCategories
    template_name = 'blog/category_detail.html'
    paginate_by = 6

    def get_object(self):
        return get_object_or_404(BlogCategories, pk=self.kwargs['blog_pk'])

    def get_context_data(self, **kwargs):
        context = super(HelpCategoryDetailView, self).get_context_data(**kwargs)
        context['blog_list'] = Blog.objects.all()
        context['categories_list'] = BlogCategories.objects.all()
        if self.request.user.is_authenticated:
            context['active_product_1'] = ProductActivated.objects.filter(user=self.request.user, product__id=1, is_active=True)
            context['role_products'] = RoleBasedProductActivated.objects.filter(user=self.request.user, product__id=1, is_active=True)
            context['inbox'] = Message.objects.filter(reciever=self.request.user)
            context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['products_legal'] = ProductActivated.objects.filter(user=self.request.user, product__id=10, is_active=True)
        else:
            context['active_product_1'] = ProductActivated.objects.filter(product__id=1, is_active=True)
            context['role_products'] = RoleBasedProductActivated.objects.filter(product__id=1, is_active=True)
            context['inbox'] = Message.objects.all()
            context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['products_legal'] = ProductActivated.objects.filter(product__id=10, is_active=True)
        return context


def search(request):
    """
    Search View
    """
    template = 'blog/blog_list.html'

    query = request.GET.get('q')

    if query:
        result = Blog.objects.filter(Q(blog_title__icontains=query) | Q(description__icontains=query) | Q(category__title__icontains=query))
    else:
        result = Blog.objects.all().order_by('id')

    if not request.user.is_authenticated:
        products_aggrement = ProductActivated.objects.filter(user=request.user, product__id=9, is_active=True)
        products = ProductActivated.objects.filter(product__id=1, is_active=True)
        role_products = RoleBasedProductActivated.objects.filter(product__id=1, is_active=True)
        inbox = Message.objects.all()
        inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        products_legal = ProductActivated.objects.filter(product__id=10, is_active=True)
    else:
        products_aggrement = ProductActivated.objects.filter(product__id=9, is_active=True)
        products = ProductActivated.objects.filter(user=request.user, product__id=1, is_active=True)
        role_products = RoleBasedProductActivated.objects.filter(user=request.user, product__id=1, is_active=True)
        inbox = Message.objects.filter(reciever=request.user)
        inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        products_legal = ProductActivated.objects.filter(user=request.user, product__id=10, is_active=True)

    context = {
        'blogs'					: result,
        'categories_l'			: BlogCategories.objects.all(),
        'products'				: products,
        'inbox'					: inbox,
        'inbox_count'			: inbox_count,
        'send_count'			: send_count,
        'role_products' 		: role_products,
        'products_legal' 		: products_legal,
        'products_aggrement' 	: products_aggrement
    }

    return render(request, template, context)
