"""
Views for AJAX
"""
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from ecommerce_integration.decorators import product_1_activation
from company.models import Company
from accounting_entry.models import LedgerMaster
from .models import StockItem, StockGroup


@login_required
@product_1_activation
def is_stock_group_name_taken_json(request, company_pk):
    """
    Checks if the stock name is already exists in a Company
    """
    data = {'is_error': False, 'error_message': ""}

    company = Company.objects.filter(pk=company_pk).first()  # returns the object if exists else None
    if not company:
        data['is_error'] = True
        data['error_message'] = "No Company found with the ID supplied"
        return JsonResponse(data)

    stock_name = request.GET.get('stock_name', None)
    if stock_name:
        data['is_taken'] = StockItem.objects.filter(
            company=company,
            stock_name__iexact=stock_name).exists()
        data['error_message'] = 'This Stock name is already exists!'
    else:
        data['is_taken'] = False

    return JsonResponse(data)


@login_required
@product_1_activation
def get_stock_gst_set_json(request):
    """
    View to handle AJAX call to check the alteration or changebility of GST in Stock Group
    """
    data = {'is_error': False, 'error_message': ""}

    stock_group_id = request.GET.get('stock_group_id', None)
    if not stock_group_id:
        data['is_error'] = True
        data['error_message'] = "Group ID is not supplied"
        return JsonResponse(data)

    stock_group = StockGroup.objects.filter(pk=stock_group_id).first()
    if not stock_group:
        data['is_error'] = True
        data['error_message'] = "No Group found with the ID supplied"
        return JsonResponse(data)

    data['is_stock_gst_set'] = stock_group.set_or_alter_gst == 'Yes'

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

    data['is_registered'] = ledger_master.registration_type == 'Registered'

    return JsonResponse(data)


@login_required
@product_1_activation
def is_non_gst_type_stock_json(request):
    """
    View to handle AJAX call to return non-gst Stock during sales invoice creation
    """
    data = {'is_error': False, 'error_message': ""}

    stock_id = request.GET.get('stock_id', None)
    if not stock_id:
        data['is_error'] = True
        data['error_message'] = "Ledger ID is not supplied"
        return JsonResponse(data)

    stock_details = StockItem.objects.get(pk=stock_id)
    if not stock_details:
        data['is_error'] = True
        data['error_message'] = "Ledger ID is not supplied"
        return JsonResponse(data)

    data['is_non_gst'] = stock_details.is_non_gst == 'Yes'

    return JsonResponse(data)


@login_required
@product_1_activation
def is_exempt_type_stock_json(request):
    """
    View to handle AJAX call to return Unregistered Stock during sales invoice creation
    """
    data = {'is_error': False, 'error_message': ""}

    stock_id = request.GET.get('stock_id', None)
    if not stock_id:
        data['is_error'] = True
        data['error_message'] = "Ledger ID is not supplied"
        return JsonResponse(data)

    stock_details = StockItem.objects.get(pk=stock_id)
    if not stock_details:
        data['is_error'] = True
        data['error_message'] = "Ledger ID is not supplied"
        return JsonResponse(data)

    data['is_exempt_stock'] = stock_details.taxability == 'Exempt'

    return JsonResponse(data)


@login_required
@product_1_activation
def is_nil_rate_type_stock_json(request):
    """
    View to handle AJAX call to return Unregistered Stock during sales invoice creation
    """
    data = {'is_error': False, 'error_message': ""}

    stock_id = request.GET.get('stock_id', None)
    if not stock_id:
        data['is_error'] = True
        data['error_message'] = "Ledger ID is not supplied"
        return JsonResponse(data)

    stock_details = StockItem.objects.get(pk=stock_id)
    if not stock_details:
        data['is_error'] = True
        data['error_message'] = "Ledger ID is not supplied"
        return JsonResponse(data)

    data['is_nil_rated_stock'] = stock_details.taxability == 'Nil Rated'

    return JsonResponse(data)


@login_required
@product_1_activation
def is_taxable_or_non_gst_type_stock_json(request):
    """
    View to handle AJAX call to return Taxable Stock during sales invoice creation
    """
    data = {'is_error': False, 'error_message': ""}

    stock_id = request.GET.get('stock_id', None)
    if not stock_id:
        data['is_error'] = True
        data['error_message'] = "Ledger ID is not supplied"
        return JsonResponse(data)

    stock_details = StockItem.objects.get(pk=stock_id)
    if not stock_details:
        data['is_error'] = True
        data['error_message'] = "Ledger ID is not supplied"
        return JsonResponse(data)

    data['is_taxable_or_non_gst'] = stock_details.taxability == 'Taxable' or stock_details.is_non_gst == 'Yes'

    return JsonResponse(data)
