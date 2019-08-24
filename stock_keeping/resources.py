"""
Resources
"""
from import_export import resources
from .models_purchase import PurchaseVoucher
from .models_sale import SaleVoucher


class PurchaseResource(resources.ModelResource):
    """
    Purchase Voucher Resource
    """
    class Meta:
        model = PurchaseVoucher


class SalesResource(resources.ModelResource):
    """
    Sale Voucher Resource
    """
    class Meta:
        model = SaleVoucher
