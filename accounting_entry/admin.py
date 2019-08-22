"""
Admin
"""
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import JournalVoucher, LedgerGroup, LedgerMaster, PeriodSelected
from .models import PaymentVoucher, PaymentVoucherRows, ReceiptVoucher, ReceiptVoucherRows, ContraVoucher, ContraVoucherRows
from .models import MultiJournalVoucher, MultiJournalVoucherDrRows, MultiJournalVoucherCrRows, BankReconciliation


class LedgerGroupAdmin(admin.ModelAdmin):
    """
    Admin for Ledger Group
    """
    model = LedgerGroup
    list_display = ['group_name', 'company', 'url_hash', 'self_group']
    search_fields = ['group_name', 'url_hash']
    #readonly_fields = ('user',)


class JournalVoucherAdmin(ImportExportModelAdmin):
    """
    Admin for Journal Voucher
    """
    model = JournalVoucher
    list_display = ['dr_ledger', 'cr_ledger', 'amount', 'company']
    search_fields = ['dr_ledger', 'cr_ledger']
    readonly_fields = ('user',)


class LedgerMasterAdminDrJournal(admin.TabularInline):
    """
    Dr Journal
    """
    model = JournalVoucher
    fk_name = 'dr_ledger'
    #exclude = ['Credit', 'Total_Debit', 'Total_Credit']


class LedgerMasterAdminCrJournal(admin.TabularInline):
    """
    Cr Journal
    """
    model = JournalVoucher
    fk_name = 'cr_ledger'
    #exclude = ['Debit', 'Total_Credit', 'Total_Debit']


class LedgerMasterAdmin(admin.ModelAdmin):
    """
    Admin for Ledger self_group
    """
    model = LedgerMaster
    list_display = ['company', 'ledger_name', 'opening_balance']
    search_fields = ['ledger_name']
    # readonly_fields = ('user',)
    # inlines = [
    #     LedgerMasterAdminDrJournal,
    #     LedgerMasterAdminCrJournal,
    # ]


class PaymentVoucherAdminRows(admin.TabularInline):
    """
    Payment rows
    """
    model = PaymentVoucherRows
    fk_name = 'payment'


class PaymentVoucherAdmin(admin.ModelAdmin):
    """
    Admin for Payment Voucher
    """
    model = PaymentVoucher
    list_display = ['voucher_date', 'account', 'total_amt']
    search_fields = ['account']
    inlines = [
        PaymentVoucherAdminRows,
    ]


class ReceiptVoucherAdminRows(admin.TabularInline):
    """
    Receipt rows
    """
    model = ReceiptVoucherRows
    fk_name = 'receipt'


class ReceiptVoucherAdmin(admin.ModelAdmin):
    """
    Admin for Receipt Voucher
    """
    model = ReceiptVoucher
    list_display = ['voucher_date', 'account', 'total_amt']
    search_fields = ['account']
    inlines = [
        ReceiptVoucherAdminRows,
    ]


class ContraVoucherAdminRows(admin.TabularInline):
    """
    Contra rows
    """
    model = ContraVoucherRows
    fk_name = 'contra'


class ContraVoucherAdmin(admin.ModelAdmin):
    """
    Admin for Contra Voucher
    """
    model = ContraVoucher
    list_display = ['voucher_date', 'account', 'total_amt']
    search_fields = ['account']
    inlines = [
        ContraVoucherAdminRows,
    ]


class MultiJournalVoucherDrRowsAdmin(admin.TabularInline):
    """
    Multi Journal Dr Rows
    """
    model = MultiJournalVoucherDrRows
    fk_name = 'multi_journal'

class MultiJournalVoucherCrRowsAdmin(admin.TabularInline):
    """
    Multi Journal Cr Rows
    """
    model = MultiJournalVoucherCrRows
    fk_name = 'multi_journal'

class MultiJournalVoucherAdmin(admin.ModelAdmin):
    """
    Admin for Multi-Journal Voucher
    """
    model = MultiJournalVoucher
    list_display = ['voucher_date', 'amount']
    inlines = [
        MultiJournalVoucherDrRowsAdmin, MultiJournalVoucherCrRowsAdmin
    ]


admin.site.register(JournalVoucher, JournalVoucherAdmin)
admin.site.register(LedgerMaster, LedgerMasterAdmin)
admin.site.register(LedgerGroup, LedgerGroupAdmin)
admin.site.register(PeriodSelected)
admin.site.register(PaymentVoucher, PaymentVoucherAdmin)
admin.site.register(PaymentVoucherRows)
admin.site.register(ReceiptVoucher, ReceiptVoucherAdmin)
admin.site.register(ReceiptVoucherRows)
admin.site.register(ContraVoucher, ContraVoucherAdmin)
admin.site.register(ContraVoucherRows)
admin.site.register(MultiJournalVoucher, MultiJournalVoucherAdmin)
admin.site.register(MultiJournalVoucherDrRows)
admin.site.register(MultiJournalVoucherCrRows)
admin.site.register(BankReconciliation)
