from django.contrib import admin
from .models_sale_accounts import SaleVoucherAccounts, SaleTermAccounts, SaleTaxAccounts
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

admin.site.register(SaleVoucherAccounts, SalesAdmin)
