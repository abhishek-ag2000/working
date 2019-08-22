"""
Views for AJAX
"""
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from ecommerce_integration.decorators import product_1_activation
from company.models import Company
from accounting_entry.models import LedgerMaster
from .models import StockItem,StockGroup


def validate_stock_name(request, company_pk):
    """
    Checks if the stock name is already exists in a Company
    """
    company = Company.objects.get(pk=company_pk)
    stock_name = request.GET.get('stock_name', None)

    if company and stock_name:
        data = {
            'is_taken': StockItem.objects.filter(company=company.pk, stock_name__iexact=stock_name).exists()
        }
    else:
        data = {
            'is_taken': False
        }
    if data['is_taken']:
        data['error_message'] = 'This stock name already exists!'

    return JsonResponse(data)

@login_required
@product_1_activation
def get_alteration_gst_value(request):
    """
    View to handle AJAX call to check the alteration or changebility of GST in Stock Group
    """
    stock_group__id = request.GET.get('stock_group__id', None)

    stock_group_details = get_object_or_404(StockGroup, pk=stock_group__id)

    if stock_group_details.set_or_alter_gst == 'Yes':
    	registered = True
    else:
    	registered = False


    data = {
        'is_registered': registered
    }
    return JsonResponse(data)


@login_required
@product_1_activation
def get_registered_ledger_value(request):
    """
    View to handle AJAX call to return Unregistered Party during sales invoice creation
    """
    ledger_id = request.GET.get('ledger_id', None)

    ledger_master = LedgerMaster.objects.get(pk=ledger_id)

    data = {
        'is_unregistered': ledger_master and ledger_master.registration_type == 'Unregistered' or ledger_master.registration_type == 'Consumer'
    }
    return JsonResponse(data)


@login_required
@product_1_activation
def get_nongst_stock_value(request):
    """
    View to handle AJAX call to return non-gst Stock during sales invoice creation
    """
    stock_id = request.GET.get('stock_id', None)

    stock_details = StockItem.objects.get(pk=stock_id)

    data = {
        'is_unregistered': stock_details and stock_details.is_non_gst == 'Yes'
    }
    return JsonResponse(data)


@login_required
@product_1_activation
def get_exempt_stock_value(request):
    """
    View to handle AJAX call to return Unregistered Stock during sales invoice creation
    """
    stock_id = request.GET.get('stock_id', None)

    stock_details = StockItem.objects.get(pk=stock_id)

    data = {
        'is_unregistered': stock_details and stock_details.taxability == 'Exempt'
    }
    return JsonResponse(data)


@login_required
@product_1_activation
def get_nilrated_stock_value(request):
    """
    View to handle AJAX call to return Unregistered Stock during sales invoice creation
    """
    stock_id = request.GET.get('stock_id', None)

    stock_details = StockItem.objects.get(pk=stock_id)

    data = {
        'is_unregistered': stock_details and stock_details.taxability == 'Nil Rated'
    }
    return JsonResponse(data)


@login_required
@product_1_activation
def get_taxable_stock_value(request):
    """
    View to handle AJAX call to return Taxable Stock during sales invoice creation
    """
    stock_id = request.GET.get('stock_id', None)

    stock_details = StockItem.objects.get(pk=stock_id)

    data = {
        'is_registered': stock_details and stock_details.taxability == 'Taxable' or stock_details.is_non_gst == 'Yes'
    }
    return JsonResponse(data)
