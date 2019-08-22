"""
Views
"""
from itertools import zip_longest
from django.shortcuts import render, get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models.functions import Coalesce
from django.db.models import Value, Count
from django.http import HttpResponseRedirect, JsonResponse
from django.template.loader import render_to_string
from user_profile.models import ProductActivated, RoleBasedProductActivated
from company.models import Company
from messaging.models import Message
from ecommerce_cart.models import Order
from .models import Product, ProductReview, Services, API, RoleBasedProduct
from .forms import ProductReviewForm


def product_list_view(request):
    """
    Product List View
    """
    products_list = Product.objects.get_queryset().order_by('id')
    page = request.GET.get('page', 1)
    paginator = Paginator(products_list, 12)

    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)

    if not request.user.is_authenticated:
        filtered_orders = Order.objects.filter(is_ordered=False)
        current_order_products = []

        if filtered_orders.exists():
            user_order = filtered_orders[0]
            user_order_items = user_order.items.all()
            current_order_products = [product.product for product in user_order_items]

        product_aggrement = ProductActivated.objects.filter(product__id=9, is_active=True)
        active_product_1 = ProductActivated.objects.filter(product__id=1, is_active=True)
        role_products = RoleBasedProductActivated.objects.filter(product__id=1, is_active=True)
        inbox = Message.objects.all()
        inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        products_legal = ProductActivated.objects.filter(product__id=10, is_active=True)
    else:
        filtered_orders = Order.objects.filter(owner=request.user.profile, is_ordered=False)
        current_order_products = []
        if filtered_orders.exists():
            user_order = filtered_orders[0]
            user_order_items = user_order.items.all()
            current_order_products = [product.product for product in user_order_items]
        product_aggrement = ProductActivated.objects.filter(user=request.user, product__id=9, is_active=True)
        active_product_1 = ProductActivated.objects.filter(user=request.user, product__id=1, is_active=True)
        role_products = RoleBasedProductActivated.objects.filter(user=request.user, product__id=1, is_active=True)
        inbox = Message.objects.filter(reciever=request.user)
        inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        products_legal = ProductActivated.objects.filter(user=request.user, product__id=10, is_active=True)

    context = {
        'products_list': products_list,
        'users': users,
        'current_order_products': current_order_products,
        'active_product_1': active_product_1,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
        'role_products': role_products,
        'product_aggrement': product_aggrement,
        'products_legal': products_legal
    }

    return render(request, "products/product_list.html", context)


@login_required
def subscribed_product_list_view(request):
    """
    My Subscription View
    """
    products_list = Product.objects.all()
    role_products_list = RoleBasedProduct.objects.all()

    inbox = Message.objects.filter(reciever=request.user)
    inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
    send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

    auditor_company = Company.objects.filter(auditor=request.user).order_by('id')
    accountant_company = Company.objects.filter(accountant=request.user).order_by('id')
    purchase_company = Company.objects.filter(purchase_personel=request.user).order_by('id')
    sales_company = Company.objects.filter(sale_personel=request.user).order_by('id')
    cb_company = Company.objects.filter(cb_personal=request.user).order_by('id')
    shared_companys = zip_longest(auditor_company, accountant_company, purchase_company, sales_company, cb_company)

    context = {
        'product_aggrement': ProductActivated.objects.filter(user=request.user, product__id=9, is_active=True),
        'products': products_list,
        'role_products_list': role_products_list,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
        'active_product_1':  ProductActivated.objects.filter(user=request.user, product__id=1, is_active=True),
        'shared_companys': shared_companys,
        'role_products': RoleBasedProductActivated.objects.filter(user=request.user, product__id=1, is_active=True),
        'products_legal': ProductActivated.objects.filter(user=request.user, product__id=10, is_active=True)
    }

    return render(request, "products/subscribed_product.html", context)


def product_detail_view(request, product_pk):
    """
    Product Details View
    """
    products_details = get_object_or_404(Product, pk=product_pk)
    reviews = ProductReview.objects.filter(reviews=products_details.pk).order_by('-id')

    if request.method == "POST":
        product_review_form = ProductReviewForm(request.POST or None)
        if product_review_form.is_valid():
            name = request.POST.get('name')
            email = request.POST.get('email')
            text = request.POST.get('text')
            answer = ProductReview.objects.create(reviews=products_details, user=request.user, name=name, email=email, text=text)
            answer.save()
            return HttpResponseRedirect(products_details.get_absolute_url())
    else:
        product_review_form = ProductReviewForm()

    if not request.user.is_authenticated:

        filtered_orders = Order.objects.filter(is_ordered=False)
        current_order_products = []
        if filtered_orders.exists():
            user_order = filtered_orders[0]
            user_order_items = user_order.items.all()
            current_order_products = [product.product for product in user_order_items]

        product_aggrement = ProductActivated.objects.filter(product__id=9, is_active=True)
        active_product_1 = ProductActivated.objects.filter(product__id=1, is_active=True)
        role_products = RoleBasedProductActivated.objects.filter(product__id=1, is_active=True)
        inbox = Message.objects.all()
        inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        products_legal = ProductActivated.objects.filter(product__id=10, is_active=True)
    else:

        filtered_orders = Order.objects.filter(owner=request.user.profile, is_ordered=False)
        current_order_products = []
        if filtered_orders.exists():
            user_order = filtered_orders[0]
            user_order_items = user_order.items.all()
            current_order_products = [product.product for product in user_order_items]

        product_aggrement = ProductActivated.objects.filter(user=request.user, product__id=9, is_active=True)
        active_product_1 = ProductActivated.objects.filter(user=request.user, product__id=1, is_active=True)
        role_products = RoleBasedProductActivated.objects.filter(user=request.user, product__id=1, is_active=True)
        inbox = Message.objects.filter(reciever=request.user)
        inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        products_legal = ProductActivated.objects.filter(user=request.user, product__id=10, is_active=True)

    context = {
        'products_details': products_details,
        'reviews': reviews,
        'product_review_form': product_review_form,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
        'current_order_products': current_order_products,
        'active_product_1': active_product_1,
        'role_products': role_products,
        'product_aggrement': product_aggrement,
        'products_legal': products_legal
    }

    return render(request, 'products/product_details.html', context)


def role_product_detail_view(request, product_pk):
    """
    Role Based Product Details View
    """
    products_details = get_object_or_404(RoleBasedProduct, pk=product_pk)

    if not request.user.is_authenticated:
        product_aggrement = ProductActivated.objects.filter(user=request.user, product__id=9, is_active=True)
        active_product_1 = ProductActivated.objects.filter(product__id=1, is_active=True)
        role_products = RoleBasedProductActivated.objects.filter(product__id=1, is_active=True)
        inbox = Message.objects.all()
        inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        products_legal = ProductActivated.objects.filter(product__id=10, is_active=True)
    else:
        product_aggrement = ProductActivated.objects.filter(product__id=9, is_active=True)
        active_product_1 = ProductActivated.objects.filter(user=request.user, product__id=1, is_active=True)
        role_products = RoleBasedProductActivated.objects.filter(user=request.user, product__id=1, is_active=True)
        inbox = Message.objects.filter(reciever=request.user)
        inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        products_legal = ProductActivated.objects.filter(user=request.user, product__id=10, is_active=True)

    context = {
        'products_details': products_details,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
        'active_product_1': active_product_1,
        'role_products': role_products,
        'product_aggrement': product_aggrement,
        'products_legal': products_legal
    }

    return render(request, 'products/role_products_details.html', context)


def review_delete(request, product_pk):
    """
    Review Delete View
    """
    data = dict()
    review = get_object_or_404(ProductReview, id=product_pk)
    if request.method == "POST":
        review.delete()
        data['form_is_valid'] = True
        reviews = ProductReview.objects.all().order_by('-id')
        data['comments'] = render_to_string('products/reviews.html', {'reviews': reviews})
    else:
        context = {'review': review}
        data['html_form'] = render_to_string('products/reviews_delete.html', context, request=request)

    return JsonResponse(data)


def csrf_failure(request, reason=""):
    """
    csrf failure
    """
    context = {'message': 'Request is Forbidden'}
    return render_to_response('products/403_csrf.html', context)


def service_list_view(request):
    """
    Service List View
    """
    services_list = Services.objects.get_queryset().order_by('id')
    page = request.GET.get('page', 1)
    paginator = Paginator(services_list, 9)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)

    if not request.user.is_authenticated:
        product_aggrement = ProductActivated.objects.filter(user=request.user, product__id=9, is_active=True)
        active_product_1 = ProductActivated.objects.filter(product__id=1, is_active=True)
        role_products = RoleBasedProductActivated.objects.filter(product__id=1, is_active=True)
        inbox = Message.objects.all()
        inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        products_legal = ProductActivated.objects.filter(product__id=10, is_active=True)
    else:
        product_aggrement = ProductActivated.objects.filter(product__id=9, is_active=True)
        active_product_1 = ProductActivated.objects.filter(user=request.user, product__id=1, is_active=True)
        role_products = RoleBasedProductActivated.objects.filter(user=request.user, product__id=1, is_active=True)
        inbox = Message.objects.filter(reciever=request.user)
        inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        products_legal = ProductActivated.objects.filter(user=request.user, product__id=10, is_active=True)

    context = {
        'services_list': services_list,
        'services': users,
        'active_product_1': active_product_1,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
        'role_products': role_products,
        'product_aggrement': product_aggrement,
        'products_legal': products_legal
    }

    return render(request, "services/services_list.html", context)


def service_detail_view(request, service_pk):
    """
    Service Details View
    """
    service_details = get_object_or_404(Services, pk=service_pk)

    if not request.user.is_authenticated:
        product_aggrement = ProductActivated.objects.filter(user=request.user, product__id=9, is_active=True)
        active_product_1 = ProductActivated.objects.filter(product__id=1, is_active=True)
        role_products = RoleBasedProductActivated.objects.filter(product__id=1, is_active=True)
        inbox = Message.objects.all()
        inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        products_legal = ProductActivated.objects.filter(product__id=10, is_active=True)
    else:
        product_aggrement = ProductActivated.objects.filter(product__id=9, is_active=True)
        active_product_1 = ProductActivated.objects.filter(user=request.user, product__id=1, is_active=True)
        role_products = RoleBasedProductActivated.objects.filter(user=request.user, product__id=1, is_active=True)
        inbox = Message.objects.filter(reciever=request.user)
        inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        products_legal = ProductActivated.objects.filter(user=request.user, product__id=10, is_active=True)

    context = {
        'service_details': service_details,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
        'active_product_1': active_product_1,
        'role_products': role_products,
        'product_aggrement': product_aggrement,
        'products_legal': products_legal
    }

    return render(request, 'services/service_description.html', context)


def api_list_view(request):
    """
    Api List View
    """
    api_list = API.objects.get_queryset().order_by('id')
    page = request.GET.get('page', 1)
    paginator = Paginator(api_list, 9)

    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)

    if not request.user.is_authenticated:
        product_aggrement = ProductActivated.objects.filter(user=request.user, product__id=9, is_active=True)
        active_product_1 = ProductActivated.objects.filter(product__id=1, is_active=True)
        role_products = RoleBasedProductActivated.objects.filter(product__id=1, is_active=True)
        inbox = Message.objects.all()
        inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        products_legal = ProductActivated.objects.filter(product__id=10, is_active=True)
    else:
        product_aggrement = ProductActivated.objects.filter(product__id=9, is_active=True)
        active_product_1 = ProductActivated.objects.filter(user=request.user, product__id=1, is_active=True)
        role_products = RoleBasedProductActivated.objects.filter(user=request.user, product__id=1, is_active=True)
        inbox = Message.objects.filter(reciever=request.user)
        inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        products_legal = ProductActivated.objects.filter(user=request.user, product__id=10, is_active=True)

    context = {
        'api_list': api_list,
        'apis': users,
        'active_product_1': active_product_1,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
        'role_products': role_products,
        'product_aggrement': product_aggrement,
        'products_legal': products_legal
    }

    return render(request, "apis/api_list.html", context)


def api_detail_view(request, api_pk):
    """
    Api Details View
    """
    api_details = get_object_or_404(API, pk=api_pk)

    if not request.user.is_authenticated:
        product_aggrement = ProductActivated.objects.filter(user=request.user, product__id=9, is_active=True)
        active_product_1 = ProductActivated.objects.filter(product__id=1, is_active=True)
        role_products = RoleBasedProductActivated.objects.filter(product__id=1, is_active=True)
        inbox = Message.objects.all()
        inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        products_legal = ProductActivated.objects.filter(product__id=10, is_active=True)
    else:
        product_aggrement = ProductActivated.objects.filter(product__id=9, is_active=True)
        active_product_1 = ProductActivated.objects.filter(user=request.user, product__id=1, is_active=True)
        role_products = RoleBasedProductActivated.objects.filter(user=request.user, product__id=1, is_active=True)
        inbox = Message.objects.filter(reciever=request.user)
        inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        products_legal = ProductActivated.objects.filter(user=request.user, product__id=10, is_active=True)

    context = {
        'api_details': api_details,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
        'active_product_1': active_product_1,
        'role_products': role_products,
        'product_aggrement': product_aggrement,
        'products_legal': products_legal
    }

    return render(request, 'apis/api_details.html', context)
