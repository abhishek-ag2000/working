from django.contrib import admin
from .models_sale_accounts import SaleVoucherAccounts, SaleTermAccounts, SaleTaxAccounts
from .models_debit_note import DebitNoteAccountsVoucher, DebitNoteAccountsTerm, DebitNoteTax
from .model_purchase_accounts import PurchaseVoucherAccounts, PurchaseTermAccounts, PurchaseTaxAccounts
from .model_credit_note_accounts import CreditNoteAccountsVoucher, CreditNoteAccountsTerm, CreditNoteAccountTax
# Register your models here.


class SalesTermInline(admin.TabularInline):
    """
    Tabular Inline admin class for SaleTerm model
    """
    model = SaleTermAccounts


class SalesTaxInline(admin.TabularInline):
    """
    Tabular Inline admin class for SaleTax model
    """
    model = SaleTaxAccounts


class SalesAdmin(admin.ModelAdmin):
    """
    Model Admin class for SaleVoucher Model
    """
    model = SaleVoucherAccounts
    list_display = ['user', 'company', 'ref_no', 'party_ac', 'total']
    search_fields = ['party_ac', 'ref_no', 'url_hash']
    inlines = [
        SalesTermInline,
        SalesTaxInline
    ]

    def get_form(self, request, obj=None, **kwargs):
        form = super(SalesAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['party_ac'].label_from_instance = lambda obj: "{} : {}".format(obj.ledger_name, obj.user)
        return form

class DebitNoteTermInline(admin.TabularInline):
    """
    Tabular Inline admin class for DebitNoteAccountsTerm model 
    """
    model = DebitNoteAccountsTerm


class DebitNoteTaxInline(admin.TabularInline):
    """
    Tabular Inline admin class for DebitNoteTax model
    """
    model = DebitNoteTax


class DebitNoteAdmin(admin.ModelAdmin):
    """
    Model Admin class for DebitNoteVoucher Model
    """
    model = DebitNoteAccountsVoucher
    list_display = ['user', 'company', 'ref_no', 'party_ac', 'total']
    search_fields = ['party_ac', 'ref_no', 'url_hash']
    inlines = [
        DebitNoteTermInline,
        DebitNoteTaxInline
    ]

    def get_form(self, request, obj=None, **kwargs):
        form = super(DebitNoteAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['party_ac'].label_from_instance = lambda obj: "{} : {}".format(obj.ledger_name, obj.user)
        return form

class PurchaseTermInline(admin.TabularInline):
    """
    Tabular Inline admin class for PurchaseTermAccounts model 
    """
    model = PurchaseTermAccounts


class PurchaseTaxInline(admin.TabularInline):
    """
    Tabular Inline admin class for PurchaseTaxAccounts model
    """
    model = PurchaseTaxAccounts


class PurchaseAccountsAdmin(admin.ModelAdmin):
    """
    Model Admin class for PurchaseVoucherAccounts Model
    """
    model = PurchaseVoucherAccounts
    list_display = ['ref_no', 'total']
    search_fields = ['ref_no', 'url_hash']
    inlines = [
        PurchaseTermInline,
        PurchaseTaxInline
    ]



class CreditNoteTermInline(admin.TabularInline):
    """
    Tabular Inline admin class for CreditNoteAccountsTerm model 
    """
    model = CreditNoteAccountsTerm


class CreditNoteTaxInline(admin.TabularInline):
    """
    Tabular Inline admin class for CreditNoteAccountTax model
    """
    model = CreditNoteAccountTax


class CreditNoteAccountsAdmin(admin.ModelAdmin):
    """
    Model Admin class for CreditNoteAccountsVoucher Model
    """
    model = CreditNoteAccountsVoucher
    list_display = ['user', 'company', 'ref_no', 'party_ac', 'total']
    search_fields = ['party_ac', 'ref_no', 'url_hash']
    inlines = [
        CreditNoteTermInline,
        CreditNoteTaxInline
    ]

    def get_form(self, request, obj=None, **kwargs):
        form = super(CreditNoteAccountsAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['party_ac'].label_from_instance = lambda obj: "{} : {}".format(obj.ledger_name, obj.user)
        return form

admin.site.register(SaleVoucherAccounts, SalesAdmin)
admin.site.register(PurchaseVoucherAccounts, PurchaseAccountsAdmin)
admin.site.register(DebitNoteAccountsVoucher, DebitNoteAdmin)
admin.site.register(CreditNoteAccountsVoucher, CreditNoteAccountsAdmin)