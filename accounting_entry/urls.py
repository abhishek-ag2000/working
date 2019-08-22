"""
Urls
"""
from django.conf.urls import url
from . import views_ajax, views_brs, views_contra, views_final_ac, views_group, \
    views_journal, views_ledger, views_payment, views_receipt, views_daybook

app_name = 'accounting_entry'

urlpatterns = [
    ####### Export and Import Urls ########################################

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/journal_export_view/$',
        views_journal.journal_export_view, name='journal_export_view'),
    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/import_journal/$',
        views_journal.journal_import_view, name='import_journal'),
    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)//export_ledger/$',
        views_ledger.get_ledger_master_excel, name='export_ledger'),

    ####### Groups Urls ########################################

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/grouplist/$',
        views_group.LedgerGroupListView.as_view(), name='grouplist'),

    url(r'^company/(?P<company_pk>\d+)/groupdetail/(?P<ledger_group_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_group.LedgerGroupDetailView.as_view(), name='groupdetail'),

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/groupcreate/$',
        views_group.LedgerGroupCreateView.as_view(), name='groupcreate'),

    url(r'^company/(?P<company_pk>\d+)/groupupdate/(?P<ledger_group_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_group.LedgerGroupUpdateView.as_view(), name='groupupdate'),

    url(r'^company/(?P<company_pk>\d+)/groupdelete/(?P<ledger_group_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_ajax.delete_ledger_group_json, name='groupdelete'),

    url(r'^company/(?P<company_pk>\d+)/ajax/is_ledger_group_name_taken_json$',
        views_ajax.is_ledger_group_name_taken_json, name='is_ledger_group_name_taken_json'),

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/groupsummary/$',
        views_group.LedgerGroupSummaryListView.as_view(), name='groupsummary'),
        
    url(r'^company/(?P<company_pk>\d+)/groupdetailsummary/(?P<ledger_group_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_group.ledger_group_detail_view, name='groupdetailsummary'),

    ####### Ledger Monthly Url ########################################

    url(r'^company/(?P<company_pk>\d+)/ledgermonthly/(?P<ledger_master_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_ledger.ledger_monthly_detail_view, name='ledgerdetailmonthly'),
    url(r'^company/(?P<company_pk>\d+)/ledgerdatewise/month/(?P<month>\d+)/year/(?P<year>\d+)/(?P<ledger_master_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_ledger.ledger_register_datewise, name='ledgerdatewise'),
    url(r'^company/(?P<company_pk>\d+)/ledgermonthly_2/(?P<ledger_master_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_ledger.ledger_monthly_detail_view_2, name='ledgerdetailmonthly_2'),
    url(r'^company/(?P<company_pk>\d+)/ledgerdatewise_2/month/(?P<month>\d+)/year/(?P<year>\d+)/(?P<ledger_master_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_ledger.ledger_register_datewise_2, name='ledgerdatewise_2'),

    url(r'^ajax/ledger_groups/$', views_ajax.get_group_base_name_json, name='get_group_base_name_json'),

    ####### Ledger Urls ########################################

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/ledgerlist/$',
        views_ledger.LedgerMasterListView.as_view(), name='ledgerlist'),
    url(r'^company/(?P<company_pk>\d+)/ledgerdetail/(?P<ledger_master_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_ledger.ledger_master_detail_view, name='ledgerdetail'),
    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/ledgercreate/$',
        views_ledger.LedgerMasterCreateView.as_view(), name='ledgercreate'),
    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/ledgerupdate/(?P<ledger_master_pk>\d+)/$',
        views_ledger.LedgerMasterUpdateView.as_view(), name='ledgerupdate'),
    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/ledgerdelete/(?P<ledger_master_pk>\d+)/$',
        views_ajax.delete_ledger_master_json, name='ledgerdelete'),
    url(r'^company/(?P<company_pk>\d+)/ajax/is_ledger_name_taken_json$',
        views_ajax.is_ledger_name_taken_json, name='is_ledger_name_taken_json'),

    ####### Bank Ledger Urls ########################################

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/bankledgerlist/$',
        views_brs.BankLedgerListView.as_view(), name='bankledgerlist'),
    url(r'^company/(?P<company_pk>\d+)/bankledgerdetail/(?P<ledger_master_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_brs.bank_ledger_details_view, name='bankledgerdetail'),
    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/bankjournallist/(?P<bank_reconciliation_pk>\d+)/$',
        views_brs.bank_journal_detail, name='bankdetail'),
    url(r'^bankjournalupdate/(?P<bank_reconciliation_pk>\d+)/$',
        views_ajax.update_bank_journal_json, name='bankupdate'),

    ####### Journal Register Urls ########################################

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/journalregister/$',
        views_journal.JournalRegisterView.as_view(), name='journalregister'),
    url(r'^company/(?P<company_pk>\d+)/journaldatewise/(?P<month>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_journal.journal_register_view, name='journal_datewise'),

    ####### Journal Urls ########################################

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/journallist/$',
        views_journal.JournalVoucherListView.as_view(), name='list'),

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/journallist/(?P<journal_voucher_pk>\d+)/$',
        views_journal.journal_voucher_detail_view, name='detail'),

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/journal/create/$',
        views_journal.JournalVoucherCreateView.as_view(), name='create'),

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/journal/update/(?P<journal_voucher_pk>\d+)/$',
        views_journal.JournalVoucherUpdateView.as_view(), name='update'),

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/journal/delete/(?P<journal_voucher_pk>\d+)/$',
        views_ajax.delete_journal_voucher_json, name='delete'),

    ####### Multijournal Urls ########################################

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/multijournallist/$',
        views_journal.MultiJournalListView.as_view(), name='multijournallist'),

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/multijournaldetails/(?P<multi_journal_voucher_pk>\d+)/$',
        views_journal.multi_journal_deail_view, name='multijournaldetail'),

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/multijournal/create/$',
        views_journal.MultiJournalCreateView.as_view(), name='multijournalcreate'),

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/multijournalupdate/(?P<multi_journal_voucher_pk>\d+)/$',
        views_journal.MultiJournalUpdateView.as_view(), name='multijournalupdate'),

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/multijournal/delete/(?P<multi_journal_voucher_pk>\d+)/$',
        views_journal.MultiJournalDeleteView.as_view(), name='multijournaldelete'),

    ####### Period Selected Urls ########################################

    url(r'^daterangeupdate/(?P<period_selected_pk>\d+)/$', views_ajax.period_selected_update, name='dateupdate'),

    ####### Payment Urls ########################################

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/payment/list/$',
        views_payment.PaymentVoucherListView.as_view(), name='paymentlist'),

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/paymentdetails/(?P<payment_voucher_pk>\d+)/$',
        views_payment.PaymentVoucherDetailView.as_view(), name='paymentdetail'),

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/payment/create/$',
        views_payment.PaymentVoucherCreateView.as_view(), name='paymentcreate'),

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/paymentupdate/(?P<payment_voucher_pk>\d+)/$',
        views_payment.PaymentVoucherUpdateView.as_view(), name='paymentupdate'),

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/payment/delete/(?P<payment_voucher_pk>\d+)/$',
        views_payment.PaymentVoucherDeleteView.as_view(), name='paymentdelete'),

    ####### Receipt Urls ########################################

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/receipt/list/$',
        views_receipt.ReceiptVoucherListView.as_view(), name='receiptlist'),
    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/receipt/details/(?P<receipt_voucher_pk>\d+)/$',
        views_receipt.ReceiptVoucherDetailView.as_view(), name='receiptdetail'),
    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/receipt/create/$',
        views_receipt.ReceiptVoucherCreateView.as_view(), name='receiptcreate'),
    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/receipt/update/(?P<receipt_voucher_pk>\d+)/$',
        views_receipt.ReceiptVoucherUpdateView.as_view(), name='receiptupdate'),
    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/receipt/delete/(?P<receipt_voucher_pk>\d+)/$',
        views_receipt.ReceiptVoucherDeleteView.as_view(), name='receiptdelete'),

    ####### Contra Urls ########################################

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/contra/list/$',
        views_contra.ContraVoucherListView.as_view(), name='contralist'),
    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/contra/details/(?P<contra_voucher_pk>\d+)/$',
        views_contra.ContraVoucherDetailView.as_view(), name='contradetail'),
    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/contra/create/$',
        views_contra.ContraVoucherCreateView.as_view(), name='contracreate'),
    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/contra/update/(?P<contra_voucher_pk>\d+)/$',
        views_contra.ContraVoucherUpdateView.as_view(), name='contraupdate'),
    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/contra/delete/(?P<contra_voucher_pk>\d+)/$',
        views_contra.ContraVoucherDeleteView.as_view(), name='contradelete'),

    ####### Daybook Urls #######################################

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/daybook/$',
        views_daybook.DayBookListView.as_view(), name='daybook'),

    url(r'^company/(?P<company_pk>\d+)/trialbalance/date/(?P<period_selected_pk>\d+)/$',
        views_final_ac.trial_balance_condensed_view, name='trialbalcond'),
    url(r'^company/(?P<company_pk>\d+)/PL/date/(?P<period_selected_pk>\d+)/$',
        views_final_ac.profit_and_loss_condensed_view, name='PandLcond'),
    url(r'^company/(?P<company_pk>\d+)/balancesheet/date/(?P<period_selected_pk>\d+)/$',
        views_final_ac.balance_sheet_condensed_view, name='blsht'),
    url(r'^company/(?P<company_pk>\d+)/cashbankbook/date/(?P<period_selected_pk>\d+)/$',
        views_daybook.cash_and_bank_view, name='cash_and_bank'),
]
