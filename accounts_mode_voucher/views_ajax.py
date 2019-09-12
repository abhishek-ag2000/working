"""
Views for AJAX
"""
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from ecommerce_integration.decorators import product_1_activation
from company.models import Company
from accounting_entry.models import LedgerMaster

######################################## AJAX CALLS FOR SALES ACCOUNTS ONLY VOUCHERS ################################

@login_required
@product_1_activation
def is_ledger_nature_same_json(request):
    """
    View to handle AJAX call to return the nature of transactions of additional ledgers
    """
    data = {'is_error': False, 'error_message': ""}

    ledger_id = request.GET.get('ledger_id', None)
    if not ledger_id:
        data['is_error'] = True
        data['error_message'] = "Ledger ID is not supplied"
        return JsonResponse(data)

    ledger_master = LedgerMaster.objects.filter(pk=ledger_id).first()
    if not ledger_master:
        data['is_error'] = True
        data['error_message'] = "No Ledger found with the ID supplied"
        return JsonResponse(data)

    data['nature_sales'] = ledger_master.nature_transactions_sales

    return JsonResponse(data)

@login_required
@product_1_activation
def is_ledger_gst_reg_type_registered_json(request):
    """
    View to handle AJAX call to return Unregistered Party during sales invoice creation
    """
    data = {'is_error': False, 'error_message': ""}

    ledger_id = request.GET.get('ledger_id', None)
    if not ledger_id:
        data['is_error'] = True
        data['error_message'] = "Ledger ID is not supplied"
        return JsonResponse(data)

    ledger_master = LedgerMaster.objects.filter(pk=ledger_id).first()
    if not ledger_master:
        data['is_error'] = True
        data['error_message'] = "No Ledger found with the ID supplied"
        return JsonResponse(data)

    data['is_registered'] = ledger_master.registration_type == 'Regular' or ledger_master.registration_type == 'Composition'
    # data['is_composition'] = ledger_master.registration_type == 'Registered'

    return JsonResponse(data)


@login_required
@product_1_activation
def is_ledger_nature_with_gst_accounts_json(request):
    """
    View to handle AJAX call to return the tax_type of GST ledgers
    """
    data = {'is_error': False, 'error_message': ""}

    ledger_id = request.GET.get('ledger_id', None)
    if not ledger_id:
        data['is_error'] = True
        data['error_message'] = "Ledger ID is not supplied"
        return JsonResponse(data)

    ledger_master = LedgerMaster.objects.filter(pk=ledger_id).first()
    if not ledger_master:
        data['is_error'] = True
        data['error_message'] = "No Ledger found with the ID supplied"
        return JsonResponse(data)

    data['tax_type'] = ledger_master.tax_type

    return JsonResponse(data)

######################################## AJAX CALLS FOR PURCHASE ACCOUNTS ONLY VOUCHERS ################################


@login_required
@product_1_activation
def is_ledger_gst_reg_type_registered_purchase_json(request):
    """
    View to handle AJAX call to return Unregistered Party during purchase invoice creation
    """
    data = {'is_error': False, 'error_message': ""}

    ledger_id = request.GET.get('ledger_id', None)
    if not ledger_id:
        data['is_error'] = True
        data['error_message'] = "Ledger ID is not supplied"
        return JsonResponse(data)

    ledger_master = LedgerMaster.objects.filter(pk=ledger_id).first()
    if not ledger_master:
        data['is_error'] = True
        data['error_message'] = "No Ledger found with the ID supplied"
        return JsonResponse(data)

    data['is_registered'] = ledger_master.registration_type == 'Regular' or ledger_master.registration_type == 'Composition'

    return JsonResponse(data)

@login_required
@product_1_activation
def is_ledger_nature_same_purchase_json(request):
    """
    View to handle AJAX call to return the nature of transactions of additional ledgers
    """
    data = {'is_error': False, 'error_message': ""}

    ledger_id = request.GET.get('ledger_id', None)
    if not ledger_id:
        data['is_error'] = True
        data['error_message'] = "Ledger ID is not supplied"
        return JsonResponse(data)

    ledger_master = LedgerMaster.objects.filter(pk=ledger_id).first()
    if not ledger_master:
        data['is_error'] = True
        data['error_message'] = "No Ledger found with the ID supplied"
        return JsonResponse(data)

    data['nature_purchase'] = ledger_master.nature_transactions_purchase

    return JsonResponse(data)


@login_required
@product_1_activation
def is_ledger_nature_purchase_with_gst_json(request):
    """
    View to handle AJAX call to return the tax_type of GST ledgers
    """
    data = {'is_error': False, 'error_message': ""}

    ledger_id = request.GET.get('ledger_id', None)
    if not ledger_id:
        data['is_error'] = True
        data['error_message'] = "Ledger ID is not supplied"
        return JsonResponse(data)

    ledger_master = LedgerMaster.objects.filter(pk=ledger_id).first()
    if not ledger_master:
        data['is_error'] = True
        data['error_message'] = "No Ledger found with the ID supplied"
        return JsonResponse(data)

    data['tax_type'] = ledger_master.tax_type

    return JsonResponse(data)

######################################## AJAX CALLS FOR DEBIT NOTE ACCOUNTS ONLY VOUCHERS ################################

@login_required
@product_1_activation
def is_ledger_nature_same_debitnote_json(request):
    """
    View to handle AJAX call to return the nature of transactions of additional ledgers in debit note voucher
    """
    data = {'is_error': False, 'error_message': ""}

    ledger_id = request.GET.get('ledger_id', None)
    if not ledger_id:
        data['is_error'] = True
        data['error_message'] = "Ledger ID is not supplied"
        return JsonResponse(data)

    ledger_master = LedgerMaster.objects.filter(pk=ledger_id).first()
    if not ledger_master:
        data['is_error'] = True
        data['error_message'] = "No Ledger found with the ID supplied"
        return JsonResponse(data)

    data['nature_purchase'] = ledger_master.nature_transactions_purchase

    return JsonResponse(data)

######################################## AJAX CALLS FOR CREDIT NOTE ACCOUNTS ONLY VOUCHERS ################################

@login_required
@product_1_activation
def is_ledger_nature_same_creditnote_json(request):
    """
    View to handle AJAX call to return the nature of transactions of additional ledgers in credit note voucher
    """
    data = {'is_error': False, 'error_message': ""}

    ledger_id = request.GET.get('ledger_id', None)
    if not ledger_id:
        data['is_error'] = True
        data['error_message'] = "Ledger ID is not supplied"
        return JsonResponse(data)

    ledger_master = LedgerMaster.objects.filter(pk=ledger_id).first()
    if not ledger_master:
        data['is_error'] = True
        data['error_message'] = "No Ledger found with the ID supplied"
        return JsonResponse(data)

    data['nature_sales'] = ledger_master.nature_transactions_sales

    return JsonResponse(data)