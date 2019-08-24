"""
Admin
"""
from django.contrib import admin
from .models import StockGroup, SimpleUnit, CompoundUnit, StockItem, StockBalance
from .models_sale import SaleVoucher, SaleStock, SaleTerm, SaleTax
from .models_purchase import PurchaseVoucher, PurchaseStock, PurchaseTerm, PurchaseTax
from .models_debit_note import DebitNoteVoucher, DebitNoteStock, DebitNoteTerm, DebitNoteTax
from .models_credit_note import CreditNoteVoucher, CreditNoteStock, CreditNoteTerm, CreditNoteTax


class StockGroupAdmin(admin.ModelAdmin):
    """
    Model Admin class for StockGroup Model
    """
    model = StockGroup
    list_display = ['user', 'company', 'group_name', 'self_group']
    search_fields = ['group_name']


class SimpleUnitsAdmin(admin.ModelAdmin):
    """
    Model Admin class for SimpleUnit Model
    """
    model = SimpleUnit
    list_display = ['user', 'company', 'symbol', 'formal', 'uqc']
    search_fields = ['symbol', 'formal']


class CompoundUnitAdmin(admin.ModelAdmin):
    """
    Model Admin class for CompoundUnit Model
    """
    model = CompoundUnit
    list_display = ['user', 'company', 'first_unit', 'conversion', 'seconds_unit']
    search_fields = ['first_unit', 'seconds_unit']


class StockItemAdmin(admin.ModelAdmin):
    """
    Model Admin class for stock_item Model
    """
    model = StockItem
    list_display = ['user', 'company', 'stock_name', 'hsn']
    search_fields = ['stock_name', 'hsn']


class StockTotalAdmin(admin.ModelAdmin):
    """
    Model Admin class for PurchaseStock Model
    """
    model = PurchaseStock
    list_display = ['purchase_voucher', 'stock_item', 'quantity', 'rate', 'total']
    search_fields = ['stock_item']


class SalesTermAdmin(admin.ModelAdmin):
    """
    Model Admin class for SaleTerm Model
    """
    model = SaleTerm
    list_display = ['sale_voucher', 'ledger', 'rate', 'rate', 'total']
    search_fields = ['stock_item']


class StockTotalSalesAdmin(admin.ModelAdmin):
    """
    Model Admin class for SaleStock Model
    """
    model = SaleStock
    list_display = ['sale_voucher', 'stock_item', 'quantity', 'total']
    search_fields = ['stock_item']


class StockTotalInline(admin.TabularInline):
    """
    Tabular Inline admin class for PurchaseStock model
    """
    model = PurchaseStock


class StockTotalSalesInline(admin.TabularInline):
    """
    Tabular Inline admin class for SaleStock model
    """
    model = SaleStock


class SalesTermInline(admin.TabularInline):
    """
    Tabular Inline admin class for SaleTerm model
    """
    model = SaleTerm


class SalesTaxInline(admin.TabularInline):
    """
    Tabular Inline admin class for SaleTax model
    """
    model = SaleTax


class PurchaseTermInline(admin.TabularInline):
    """
    Tabular Inline admin class for PurchaseTerm model
    """
    model = PurchaseTerm


class PurchaseTaxInline(admin.TabularInline):
    """
    Tabular Inline admin class for PurchaseTax model
    """
    model = PurchaseTax


class PurchaseAdmin(admin.ModelAdmin):
    """
    Model Admin class for PurchaseVoucher Model
    """
    model = PurchaseVoucher
    list_display = ['user', 'company', 'ref_no', 'party_ac', 'doc_ledger', 'sub_total']
    search_fields = ['party_ac', 'ref_no']
    inlines = [
        StockTotalInline,
        PurchaseTermInline,
        PurchaseTaxInline]

    def get_form(self, request, obj=None, **kwargs):
        form = super(PurchaseAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['party_ac'].label_from_instance = lambda obj: "{} ({})".format(obj.ledger_name, obj.user)
        form.base_fields['doc_ledger'].label_from_instance = lambda obj: "{} : {}".format(obj.ledger_name, obj.user)
        return form


class SalesAdmin(admin.ModelAdmin):
    """
    Model Admin class for SaleVoucher Model
    """
    model = SaleVoucher
    list_display = ['user', 'company', 'ref_no', 'party_ac', 'doc_ledger', 'sub_total']
    search_fields = ['party_ac', 'ref_no']
    inlines = [
        StockTotalSalesInline,
        SalesTermInline,
        SalesTaxInline
    ]

    def get_form(self, request, obj=None, **kwargs):
        form = super(SalesAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['party_ac'].label_from_instance = lambda obj: "{} : {}".format(obj.ledger_name, obj.user)
        form.base_fields['doc_ledger'].label_from_instance = lambda obj: "{} : {}".format(obj.ledger_name, obj.user)
        return form


class StockTotalDebitInline(admin.TabularInline):
    """
    Tabular Inline admin class for DebitNoteStock model
    """
    model = DebitNoteStock


class DebitNoteTermInline(admin.TabularInline):
    """
    Tabular Inline admin class for DebitNoteTerm model
    """
    model = DebitNoteTerm


class DebitNoteTaxInline(admin.TabularInline):
    """
    Tabular Inline admin class for DebitNoteTax model
    """
    model = DebitNoteTax


class DebitNoteAdmin(admin.ModelAdmin):
    """
    Model Admin class for DebitNoteVoucher Model
    """
    model = DebitNoteVoucher
    list_display = ['user', 'company', 'ref_no', 'party_ac', 'doc_ledger', 'sub_total']
    search_fields = ['party_ac', 'ref_no']
    inlines = [
        StockTotalDebitInline,
        DebitNoteTermInline,
        DebitNoteTaxInline
    ]

    def get_form(self, request, obj=None, **kwargs):
        form = super(DebitNoteAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['party_ac'].label_from_instance = lambda obj: "{} : {}".format(obj.ledger_name, obj.user)
        form.base_fields['doc_ledger'].label_from_instance = lambda obj: "{} : {}".format(obj.ledger_name, obj.user)
        return form


class StockTotalCreditInline(admin.TabularInline):
    """
    Tabular Inline admin class for CreditNoteStock model
    """
    model = CreditNoteStock


class CreditNoteTermInline(admin.TabularInline):
    """
    Tabular Inline admin class for CreditNoteTerm model
    """
    model = CreditNoteTerm


class CreditNoteTaxInline(admin.TabularInline):
    """
    Tabular Inline admin class for CreditNoteTax model
    """
    model = CreditNoteTax


class CreditNoteAdmin(admin.ModelAdmin):
    """
    Model Admin class for CreditNoteVoucher Model
    """
    model = CreditNoteVoucher
    list_display = ['user', 'id', 'company', 'ref_no', 'party_ac', 'doc_ledger', 'sub_total']
    search_fields = ['party_ac', 'ref_no']
    inlines = [
        StockTotalCreditInline,
        CreditNoteTermInline,
        CreditNoteTaxInline
    ]

    def get_form(self, request, obj=None, **kwargs):
        form = super(CreditNoteAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['party_ac'].label_from_instance = lambda obj: "{} : {}".format(obj.ledger_name, obj.user)
        form.base_fields['doc_ledger'].label_from_instance = lambda obj: "{} : {}".format(obj.ledger_name, obj.user)
        return form


admin.site.register(StockGroup, StockGroupAdmin)
admin.site.register(SimpleUnit, SimpleUnitsAdmin)
admin.site.register(CompoundUnit, CompoundUnitAdmin)
admin.site.register(StockItem, StockItemAdmin)
admin.site.register(PurchaseVoucher, PurchaseAdmin)
admin.site.register(SaleVoucher, SalesAdmin)
admin.site.register(PurchaseStock, StockTotalAdmin)
admin.site.register(PurchaseTerm)
admin.site.register(SaleStock, StockTotalSalesAdmin)
admin.site.register(SaleTerm, SalesTermAdmin)
admin.site.register(SaleTax)
admin.site.register(StockBalance)
admin.site.register(DebitNoteVoucher, DebitNoteAdmin)
admin.site.register(CreditNoteVoucher, CreditNoteAdmin)
