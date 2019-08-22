"""
Views
"""
import string
import random
from datetime import date
import datetime
from django.contrib.auth.decorators import login_required
from django.db.models.functions import Coalesce
from django.db.models import Value, Count
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from user_profile.models import Profile, ProductActivated, RoleBasedProductActivated
from messaging.models import Message
from ecommerce_integration.models import Product
from .models import OrderItem, Order


def get_new_order_id():
    """
    Function to generate order id
    """
    date_str = date.today().strftime('%Y%m%d')[2:] + str(datetime.datetime.now().second)
    rand_str = "".join([random.choice(string.digits) for count in range(3)])
    return date_str + rand_str


def get_user_pending_order(request):
    """
    Function to get the user pending order
    """
    # get order for the correct user
    user_profile = get_object_or_404(Profile, user=request.user)
    order = Order.objects.filter(owner=user_profile, is_ordered=False)
    if order.exists():
        # get the only order in the list of filtered orders
        return order[0]
    return None


@login_required
def add_to_cart(request, **kwargs):
    """
    Views that will add item to cart
    """
    # get the user profile
    user_profile = get_object_or_404(Profile, user=request.user)
    # filter products by id
    product = Product.objects.filter(id=kwargs.get('item_id', "")).first()
    # check if the user already owns this product
    if product in request.user.profile.subscribed_products.all():
        return redirect(reverse('ecommerce_integration:productlist'))
    # create orderItem of the selected product
    order_item, status = OrderItem.objects.get_or_create(product=product)
    # create order associated with the user
    user_order, status = Order.objects.get_or_create(owner=user_profile, is_ordered=False)
    user_order.items.add(order_item)
    if status:
        # generate a reference code
        user_order.ref_code = get_new_order_id()
        user_order.save()

    # show confirmation message and redirect back to the same page
    return redirect(reverse('ecommerce_integration:productlist'))


@login_required
def order_detail_view(request, **kwargs):
    """
    Add to cart details view
    """
    existing_order = get_user_pending_order(request)
    order_list = Order.objects.all().order_by('-id')

    inbox = Message.objects.filter(reciever=request.user)
    inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
    send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

    context = {

        'product_aggrement': ProductActivated.objects.filter(user=request.user, product__id=9, is_active=True),
        'order': existing_order,
        'order_list': order_list,
        'Products': ProductActivated.objects.filter(user=request.user, product__id=1, is_active=True),
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
        'role_product': RoleBasedProductActivated.objects.filter(user=request.user, product__id=1, is_active=True),
        'product_legal': ProductActivated.objects.filter(user=request.user, product__id=10, is_active=True)
    }
    return render(request, 'cart/cart.html', context)


@login_required
def check_out_view(request, **kwargs):
    """
    View to generate check_out_view Bill
    """
    existing_order = get_user_pending_order(request)
    order_list = Order.objects.all()

    inbox = Message.objects.filter(reciever=request.user)
    inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
    send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

    context = {
        'product_aggrement': ProductActivated.objects.filter(user=request.user, product__id=9, is_active=True),
        'order': existing_order,
        'order_list': order_list,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
        'Products': ProductActivated.objects.filter(user=request.user, product__id=1, is_active=True),
        'role_product': RoleBasedProductActivated.objects.filter(user=request.user, product__id=1, is_active=True),
        'product_legal': ProductActivated.objects.filter(user=request.user, product__id=10, is_active=True)
    }
    return render(request, 'cart/checkout.html', context)


@login_required()
def delete_from_cart(request, item_id):
    """
    View that will delete items from cart
    """
    item_to_delete = OrderItem.objects.filter(pk=item_id)
    if item_to_delete.exists():
        item_to_delete[0].delete()
    return redirect(reverse('ecommerce_cart:order_summary'))


@login_required()
def update_tran_record(request):
    """
    View to Update the Transaction Records and to complete the payment and checkout process
    """
    # get the order being processed
    order_to_purchase = get_user_pending_order(request)
    if not order_to_purchase:
        return redirect(reverse('ecommerce_integration:productlist'))

    # update the placed order
    order_to_purchase.is_ordered = True
    order_to_purchase.date_ordered = datetime.datetime.now()
    order_to_purchase.save()

    # get all items in the order - generates a queryset
    order_items = order_to_purchase.items.all()

    # update order items
    order_items.update(is_ordered=True, date_ordered=datetime.datetime.now())

    # Add products to user profile
    user_profile = get_object_or_404(Profile, user=request.user)
    # get the products from the items
    order_products = [item.product for item in order_items]
    user_profile.subscribed_products.add(*order_products)
    user_profile.save()

    # # create a transaction
    # transaction = Transaction(profile=request.user.profile,
    #                         token=token,
    #                         order_id=order_to_purchase.id,
    #                         amount=order_to_purchase.get_cart_total(),
    #                         success=True)
    # # save the transcation (otherwise doesn't exist)
    # transaction.save()

    # messages.info(request, "Thank you! Your purchase was successful!")
    return redirect(reverse('ecommerce_integration:productlist'))
