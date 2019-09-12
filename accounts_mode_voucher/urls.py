"""
URLs
"""
from django.conf.urls import url
from . import views_sales_account,views_ajax,views_purchase_accounts,views_debit_note_accounts,views_credit_note

app_name = 'accounts_mode_voucher'

urlpatterns = [

    ################################### AJAX Url #######################################


    url(r'^ajax/reg_ledger_value/$', views_ajax.is_ledger_nature_same_json,
        name='is_ledger_nature_same_json'),

    url(r'^ajax/reg_gst_value/$', views_ajax.is_ledger_gst_reg_type_registered_json,
        name='is_ledger_gst_reg_type_registered_json'),

    url(r'^ajax/reg_ledger_value/purchase/$', views_ajax.is_ledger_nature_same_purchase_json,
        name='is_ledger_nature_same_purchase_json'),

    url(r'^ajax/reg_gst_value/purchase/$', views_ajax.is_ledger_gst_reg_type_registered_purchase_json,
        name='is_ledger_gst_reg_type_registered_purchase_json'),

    url(r'^ajax/reg_ledger_value/debitnote/$', views_ajax.is_ledger_nature_same_debitnote_json,
        name='is_ledger_nature_same_debitnote_json'),

    url(r'^ajax/reg_ledger_value/creditnote/$', views_ajax.is_ledger_nature_same_creditnote_json,
        name='is_ledger_nature_same_creditnote_json'),

    url(r'^ajax/sales/gst_accounts_ledger_value/$', views_ajax.is_ledger_nature_with_gst_accounts_json,
        name='is_ledger_nature_with_gst_accounts_json'),

    url(r'^ajax/purchase/gst_accounts_ledger_value/$', views_ajax.is_ledger_nature_purchase_with_gst_json,
        name='is_ledger_nature_purchase_with_gst_json'),


    ################################### Purchase Accounts Url #######################################


    url(r'^company/(?P<company_pk>\d+)/purchasedetail/(?P<purchase_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_purchase_accounts.PurchaseDetailsView.as_view(), name='purchasedetail'),

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/purchasecreate/$',
        views_purchase_accounts.PurchaseCreateView.as_view(), name='purchasecreate'),

    url(r'^company/(?P<company_pk>\d+)/purchaseupdate/(?P<purchase_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_purchase_accounts.PurchaseUpdateView.as_view(), name='purchaseupdate'),

    url(r'^company/(?P<company_pk>\d+)/purchasedelete/(?P<purchase_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_purchase_accounts.PurchaseDeleteView.as_view(), name='purchasedelete'),


    ################################### Sales Accounts Url #######################################

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/sales$',
        views_sales_account.SalesListAccountsView.as_view(), name='saleslist'),

    url(r'^company/(?P<company_pk>\d+)/salesdetail/(?P<sales_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_sales_account.SalesDetailsView.as_view(), name='salesdetail'),

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/salescreate/$',
        views_sales_account.SalesCreateView.as_view(), name='salescreate'),

    url(r'^company/(?P<company_pk>\d+)/salesupdate/(?P<sales_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_sales_account.SalesUpdateView.as_view(), name='salesupdate'),

    url(r'^company/(?P<company_pk>\d+)/salesdelete/(?P<sales_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_sales_account.SalesDeleteView.as_view(), name='salesdelete'),

    ################################### Debit Note Accounts Url #######################################


    url(r'^company/(?P<company_pk>\d+)/debit_note_accounts_detail/(?P<debit_note_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_debit_note_accounts.DebitNoteAccountsDetailsView.as_view(), name='debitdetail'),

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/debit_note_accounts_create/$',
        views_debit_note_accounts.DebitNoteCreateview.as_view(), name='debitcreate'),

    url(r'^company/(?P<company_pk>\d+)/debit_note_accounts_update/(?P<debit_note_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_debit_note_accounts.DebitNoteUpdateView.as_view(), name='debitupdate'),

    url(r'^company/(?P<company_pk>\d+)/debit_note_accounts_delete/(?P<debit_note_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_debit_note_accounts.DebitNoteDeleteView.as_view(), name='debitdelete'),

    ################################### CREDIT Note Accounts Url #######################################


    url(r'^company/(?P<company_pk>\d+)/credit_note_accounts/detail/(?P<credit_note_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_credit_note.CreditNoteDetailsView.as_view(), name='creditdetail'),

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/credit_note_accounts/create/$',
        views_credit_note.CreditNoteCreateView.as_view(), name='creditcreate'),

    url(r'^company/(?P<company_pk>\d+)/credit_note_accounts/update/(?P<credit_note_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_credit_note.CreditNoteUpdateView.as_view(), name='creditupdate'),

    url(r'^company/(?P<company_pk>\d+)/credit_note_accounts/delete/(?P<credit_note_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_credit_note.CreditNoteDeleteView.as_view(), name='creditdelete'),


]
