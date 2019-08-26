"""
Views for AJAX
"""
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from ecommerce_integration.decorators import product_1_activation
from company.models import Company
from accounting_entry.models import LedgerMaster



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
    data['nature_purchase'] = ledger_master.nature_transactions_purchase

    return JsonResponse(data)

