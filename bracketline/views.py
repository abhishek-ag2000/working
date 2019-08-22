"""
Bracketline (Views)
"""
import math
import re
import decimal
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Value
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.shortcuts import render, redirect
from user_profile.models import ProductActivated
from messaging.models import Message
from .forms import CreateUserForm


def signup_view(request):
    """
    Signup View
    """
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created successfully for {username}')
            return redirect('bracketline:login')
    else:
        form = CreateUserForm()

    return render(request, 'bracketline/signup.html', {'form': form})


@login_required
def change_password_view(request):
    """
    Change Password View
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('bracketline:change_password')

        messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)

    if not request.user.is_authenticated:
        our_product = ProductActivated.objects.filter(product__id=1, is_active=True)
        inbox = Message.objects.all()
        inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

    else:
        our_product = ProductActivated.objects.filter(user=request.user, product__id=1, is_active=True)
        inbox = Message.objects.filter(reciever=request.user)
        inbox_count = inbox.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.filter(sender=request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

    context = {
        'form': form,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
        'our_product': our_product,
    }

    return render(request, 'bracketline/change_password.html', context)


def get_gstin_check_sum_char(s_gstin):
    """
    Returns the GSTIN check sum character
    """
    # Rule as extracted from GSTR Returns tool 2.0
    s_gstin = s_gstin.strip().upper()[:14]

    i_factor = 2
    f_sum = decimal.Decimal(0.0)
    check_code_point = 0

    f_digit = decimal.Decimal(0.0)

    i_code_point = 0
    s_cp_chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    i_len_cp_chars = len(s_cp_chars)
    s_input_chars = s_gstin

    for c_loop_input in reversed(s_input_chars):
        i_code_point = -1
        j = -1
        for c_loop_cp_chars in s_cp_chars:
            j += 1
            if c_loop_cp_chars == c_loop_input:
                i_code_point = j
                break

        f_digit = decimal.Decimal(i_factor * i_code_point)
        if i_factor == 2:
            i_factor = 1
        else:
            i_factor = 2

        f_digit = (f_digit / i_len_cp_chars) + (f_digit % i_len_cp_chars)
        f_sum += math.floor(f_digit)
    check_code_point = ((i_len_cp_chars - int(f_sum % i_len_cp_chars)) % i_len_cp_chars)

    return s_cp_chars[check_code_point]


def validate_gstin(s_input_gst_no):
    """
    Returns a tuple with (bool, str) specifing whether the GSTIN valid and the parse result
    """
    # Rule as extracted from GSTR Returns tool 2.0
    s_parse_result = ""

    if len(s_input_gst_no) != 15:
        s_parse_result = "Length found {0} expected 15!".format(len(s_input_gst_no))
        return False, s_parse_result

    b_pattern_check = re.match(
        "[0-9]{2}[a-zA-Z]{5}[0-9]{4}[a-zA-Z]{1}[1-9A-Za-z]{1}[Zz1-9A-Ja-j]{1}[0-9a-zA-Z]{1}", s_input_gst_no)
    if not b_pattern_check:
        s_parse_result = "Pattern mismatch!"
        return False, s_parse_result

    s_gstin = s_input_gst_no.strip().upper()[:14]
    c_check_sum_char = get_gstin_check_sum_char(s_gstin)

    s_new_gstin = s_gstin + c_check_sum_char
    if s_new_gstin != s_input_gst_no.upper():
        s_parse_result = "Checksum error: " + c_check_sum_char + "!"
        return False, s_parse_result

    s_parse_result = "Parse Successful"
    return True, s_parse_result


def validate_gstin_ajax(request):
    """
    Checks if the gstin supplied in the request valid
    """
    gstin = request.GET.get('gstin', None)
    data_obj = {}

    if gstin:
        result = validate_gstin(gstin)
        data_obj['valid'] = result[0]
        data_obj['msg'] = result[1]
    else:
        data_obj['valid'] = False
        data_obj['msg'] = "Empty GSTIN!"

    return JsonResponse(data_obj)
