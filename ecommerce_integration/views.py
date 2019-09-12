"""
Views
"""
import datetime
from itertools import zip_longest
from django.shortcuts import render, get_object_or_404, render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Value, Count, F, Window
from django.db.models.functions import Coalesce, RowNumber
from django.http import HttpResponseRedirect, JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse
from user_profile.models import ProductActivated, RoleBasedProductActivated
from company.models import Company
from messaging.models import Message
from ecommerce_cart.models import Order, OrderItem
from ecommerce_cart.etran_validation import verify_payment_status
from .models import Product, ProductSubscription, ProductReview, Services, API, RoleBasedProduct, PriceModel
from .forms import ProductToCard, ProductReviewForm
from .utils import calculate_price


@login_required
def product_list_view(request, order_item_pk=0):
    """
    Product List View
    """
    last_order_item = None
    products_list = Product.objects.get_queryset().order_by('id')
    page = request.GET.get('page', 1)
    paginator = Paginator(products_list, 12)

    try:
        product_list_paged = paginator.page(page)
    except PageNotAnInteger:
        product_list_paged = paginator.page(1)
    except EmptyPage:
        product_list_paged = paginator.page(paginator.num_pages)

    order = Order.objects.filter(owner=request.user.profile, is_ordered=False).first()
    current_order_products = []

    if order:
        user_order_items = order.get_cart_items()
        current_order_products = [order_item.price_model.product for order_item in user_order_items]

    if order_item_pk and int(order_item_pk) > 0:
        last_order_item = OrderItem.objects.filter(pk=order_item_pk).first()

    product_aggrement = ProductActivated.objects.filter(user=request.user, product__id=9, is_active=True)
    active_product_1 = ProductActivated.objects.filter(user=request.user, product__id=1, is_active=True)
    role_products = RoleBasedProductActivated.objects.filter(user=request.user, product__id=1, is_active=True)
    inbox = Message.objects.filter(reciever=request.user)
    inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
    send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
    products_legal = ProductActivated.objects.filter(user=request.user, product__id=10, is_active=True)

    context = {
        'last_order_item': last_order_item,
        'products_list': products_list,
        'product_list_paged': product_list_paged,
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
    active_subscriptions = ProductSubscription.objects.filter(
        user=request.user,
        subscription_from__lte=datetime.date.today(),
        subscription_upto__gte=datetime.date.today(),
        subscription_active=True
    ).order_by("-subscription_from")

    product_activated = ProductActivated.objects.filter(user=request.user, is_active=True)
    product_activated_list = []
    if product_activated:
        product_activated_list = [item.product.pk for item in product_activated]

    #products_list = Product.objects.all()
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
        'active_subscriptions': active_subscriptions,
        'product_activated_list': product_activated_list,
        # 'product_aggrement': ProductActivated.objects.filter(user=request.user, product__id=9, is_active=True),
        # 'products': products_list,
        'role_products_list': role_products_list,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
        # 'active_product_1':  ProductActivated.objects.filter(user=request.user, product__id=1, is_active=True),
        'shared_companys': shared_companys,
        # 'role_products': RoleBasedProductActivated.objects.filter(user=request.user, product__id=1, is_active=True),
        # 'products_legal': ProductActivated.objects.filter(user=request.user, product__id=10, is_active=True)
    }

    return render(request, "products/subscribed_product.html", context)


@login_required
def product_price_json(request):
    """
    Returns the product price for the product plan in JSON
    """
    data = {'is_error': False, 'error_message': ""}

    price_model_id = request.POST.get('model_id', None)
    if not price_model_id:
        data['is_error'] = True
        data['error_message'] = "Price Model ID is not supplied"
        return JsonResponse(data)

    month_count = request.POST.get('month_count', None)
    if not month_count:
        data['is_error'] = True
        data['error_message'] = "Month Count is not supplied"
        return JsonResponse(data)

    price_model = PriceModel.objects.filter(pk=price_model_id).first()
    if not price_model:
        data['is_error'] = True
        data['error_message'] = "No Price Model found with the ID supplied"
        return JsonResponse(data)

    #data['price'] = get_price_from_model(price_model, month_count)
    data['price'] = calculate_price(
        price_model.monthly_inclusive_price,
        price_model.quarterly_inclusive_price,
        price_model.half_yearly_inclusive_price,
        price_model.annual_inclusive_price,
        int(month_count))

    return JsonResponse(data)


@login_required
def product_detail_view(request, product_pk):
    """
    Product Details View
    """
    products_details = get_object_or_404(Product, pk=product_pk)
    reviews = ProductReview.objects.filter(reviews=products_details.pk).order_by('-id')

    if request.method == "POST":
        product_to_cart_form = ProductToCard(request.POST)
        if product_to_cart_form.is_valid():
            price_model_id = request.POST.get('model_id')
            month_count = request.POST.get('month_count')
            # return reverse('ecommerce_cart:add_to_cart', kwargs={'price_model_id': price_model_id, 'month_count': month_count})
            return redirect('ecommerce_cart:add_to_cart', price_model_id=price_model_id, month_count=month_count)

        product_review_form = ProductReviewForm(request.POST or None)
        if product_review_form.is_valid():
            name = request.POST.get('name')
            email = request.POST.get('email')
            text = request.POST.get('text')
            answer = ProductReview.objects.create(reviews=products_details, user=request.user, name=name, email=email, text=text)
            answer.save()
            return HttpResponseRedirect(products_details.get_absolute_url())
    else:
        product_to_cart_form = ProductToCard()
        product_review_form = ProductReviewForm()

    order = Order.objects.filter(owner=request.user.profile, is_ordered=False).first()
    current_order_products = []
    if order:
        if order.razorpay_order_id:
            # razorpay order id already exists; checking if payment already made but subscription failed
            if verify_payment_status(order.razorpay_order_id, order):
                return redirect(reverse('ecommerce_integration:subscribedproductlist'))

        user_order_items = order.get_cart_items()
        current_order_products = [item.price_model.product for item in user_order_items]

    product_aggrement = ProductActivated.objects.filter(user=request.user, product__id=9, is_active=True)
    active_product_1 = ProductActivated.objects.filter(user=request.user, product__id=1, is_active=True)
    role_products = RoleBasedProductActivated.objects.filter(user=request.user, product__id=1, is_active=True)
    inbox = Message.objects.filter(reciever=request.user)
    inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
    send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
    products_legal = ProductActivated.objects.filter(user=request.user, product__id=10, is_active=True)

    # -- SQL for listing each product feature latest by date and applicable from today
    # SELECT * FROM (
    # SELECT pm.id, pm.apply_from, pm.annual_inclusive_price, pf.feature_name, pf.sorting_watage,
    #     ROW_NUMBER() OVER (PARTITION BY pf.feature_name ORDER BY pm.apply_from DESC) AS row_num
    # FROM public.ecommerce_integration_pricemodel AS pm
    # INNER JOIN public.ecommerce_integration_productfeature AS pf
    # ON pm.product_feature_id = pf.id
    # WHERE pm.product_id = 1
    # AND pm.apply_from <= Now()
    # AND pm.active_new = true
    # )IT
    # WHERE row_num = 1
    # ORDER BY sorting_watage

    price_models = PriceModel.objects.filter(
        product=products_details,
        apply_from__lte=datetime.date.today(),
        active_new=True
    ).annotate(
        row_number=Window(
            expression=RowNumber(),
            partition_by=F("product_feature__feature_name"),
            order_by=F("apply_from").desc()
        )
        # ).filter(
        #     row_number=1 # filtering not allowed on window function
    ).order_by('product_feature__sorting_watage')   # query need more filter to fetch last plan feature-wise for a product as below

    price_feature_count = 0
    for elmt in price_models:
        if elmt.row_number == 1:
            price_feature_count += 1  # counting applicable record count using loop due to window function limitation of filter

    feature_col_count = 4

    if price_feature_count > 0:
        feature_col_count = int(12 / price_feature_count)

    if feature_col_count <= 2:
        feature_col_count = 4

    # assume lastly active subscription is the active subscription when multiple active subscription exists for the product within the period
    active_subscription = ProductSubscription.objects.filter(
        user=request.user,
        price_model__product=products_details,
        subscription_from__lte=datetime.date.today(),
        subscription_upto__gte=datetime.date.today(),
        subscription_active=True
    ).order_by("-subscription_from").first()

    future_subscription = ProductSubscription.objects.filter(
        user=request.user,
        price_model__product=products_details,
        subscription_from__gt=datetime.date.today(),
        subscription_active=True
    ).order_by("-subscription_from").first()

    context = {
        'products_details': products_details,
        'price_models': price_models,
        'feature_col_count': feature_col_count,
        'price_feature_count': price_feature_count,
        'active_subscription': active_subscription,
        'future_subscription': future_subscription,
        'product_to_cart_form': product_to_cart_form,
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
