"""
URLs
"""
from django.conf.urls import url
from . import views, views_ajax, views_purchase, views_sales, views_debit_note, views_credit_note, views_stock, views_units

app_name = 'stock_keeping'

urlpatterns = [

    ################################### AJAX Url #######################################

    url(r'^company/(?P<company_pk>\d+)/ajax/is_stock_group_name_taken_json$',
        views_ajax.is_stock_group_name_taken_json, name='is_stock_group_name_taken_json'),


    url(r'^ajax/alteration_gst/$', views_ajax.get_stock_gst_set_json,
        name='get_stock_gst_set_json'),

    url(r'^ajax/stock_group_value/$', views_ajax.get_stock_group_value, name='get_stock_group_value'),

    ################################### Sales AJAX Urls #######################################

    url(r'^ajax/reg_ledger_value/$', views_ajax.is_ledger_gst_reg_type_registered_json,
        name='is_ledger_gst_reg_type_registered_json'),

    url(r'^ajax/reg_stock_value/$', views_ajax.is_exempt_type_stock_json,
        name='is_exempt_type_stock_json'),

    url(r'^ajax/nongst_stock_value/$', views_ajax.is_non_gst_type_stock_json,
        name='is_non_gst_type_stock_json'),

    url(r'^ajax/registered_stock_value/$',
        views_ajax.is_taxable_or_non_gst_type_stock_json, name='is_taxable_or_non_gst_type_stock_json'),

    url(r'^ajax/nilrated_stock_value/$', views_ajax.is_nil_rate_type_stock_json,
        name='is_nil_rate_type_stock_json'),

    url(r'^ajax/sales/reg_ledger_value/$', views_ajax.is_ledger_nature_same_json,
        name='is_ledger_nature_same_json'),

    url(r'^ajax/sales/gst_ledger_value/$', views_ajax.is_ledger_nature_with_gst_json,
        name='is_ledger_nature_with_gst_json'),

    ################################### Purchase AJAX Urls #######################################

    url(r'^ajax/reg_stock_value/purchase/$', views_ajax.is_exempt_type_stock_purchase_json,
        name='is_exempt_type_stock_purchase_json'),

    url(r'^ajax/reg_gst_value/purchase/$', views_ajax.is_ledger_gst_reg_type_registered_purchase_json,
        name='is_ledger_gst_reg_type_registered_purchase_json'),

    url(r'^ajax/nongst_stock_value/purchase/$', views_ajax.is_non_gst_type_stock_purchase_json,
        name='is_non_gst_type_stock_purchase_json'),

    url(r'^ajax/registered_stock_value/purchase/$',
        views_ajax.is_taxable_or_non_gst_type_stock_purchase_json, name='is_taxable_or_non_gst_type_stock_purchase_json'),

    url(r'^ajax/nilrated_stock_value//purchase/$', views_ajax.is_nil_rate_type_stock_purchase_json,
        name='is_nil_rate_type_stock_purchase_json'),

    url(r'^ajax/purchase/reg_ledger_value/$', views_ajax.is_ledger_nature_same_purchase_json,
        name='is_ledger_nature_same_purchase_json'),

    url(r'^ajax/purchase/gst_ledger_value/$', views_ajax.is_ledger_nature_purchase_with_gst_json,
        name='is_ledger_nature_purchase_with_gst_json'),

    ################################### Debit Note AJAX Urls #######################################

    url(r'^ajax/reg_stock_value/debitnote/$', views_ajax.is_exempt_type_stock_debitnote_json,
        name='is_exempt_type_stock_debitnote_json'),

    url(r'^ajax/nongst_stock_value/debitnote/$', views_ajax.is_non_gst_type_stock_debitnote_json,
        name='is_non_gst_type_stock_debitnote_json'),

    url(r'^ajax/registered_stock_value/debitnote/$',
        views_ajax.is_taxable_or_non_gst_type_stock_debitnote_json, name='is_taxable_or_non_gst_type_stock_debitnote_json'),

    url(r'^ajax/nilrated_stock_value//debitnote/$', views_ajax.is_nil_rate_type_stock_debitnote_json,
        name='is_nil_rate_type_stock_debitnote_json'),

    url(r'^ajax/purchase/reg_ledger_value/$', views_ajax.is_ledger_nature_same_debitnote_json,
        name='is_ledger_nature_same_debitnote_json'),

    ################################### Credit Note AJAX Urls #######################################

    url(r'^ajax/reg_stock_value/creditnote/$', views_ajax.is_exempt_type_stock_creditnote_json,
        name='is_exempt_type_stock_creditnote_json'),

    url(r'^ajax/nongst_stock_value/creditnote/$', views_ajax.is_non_gst_type_stock_creditnote_json,
        name='is_non_gst_type_stock_creditnote_json'),

    url(r'^ajax/registered_stock_value/creditnote/$',
        views_ajax.is_taxable_or_non_gst_type_stock_creditnote_json, name='is_taxable_or_non_gst_type_stock_creditnote_json'),

    url(r'^ajax/nilrated_stock_value//creditnote/$', views_ajax.is_nil_rate_type_stock_creditnote_json,
        name='is_nil_rate_type_stock_creditnote_json'),

    url(r'^ajax/purchase/reg_ledger_value/$', views_ajax.is_ledger_nature_same_creditnote_json,
        name='is_ledger_nature_same_creditnote_json'),


    ################################### Simple Units Url #######################################

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/simpleunitlist$',
        views_units.SimpleUnitListView.as_view(), name='simplelist'),

    url(r'^company/(?P<company_pk>\d+)/simpleunitdetail/(?P<simpleunit_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_units.SimpleUnitDetailView.as_view(), name='simpledetail'),

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/simpleunitcreate/$',
        views_units.SimpleUnitCreateView.as_view(), name='simplecreate'),

    url(r'^company/(?P<company_pk>\d+)/simpleunitupdate/(?P<simpleunit_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_units.SimpleUnitUpdateView.as_view(), name='simpleupdate'),

    url(r'^company/(?P<company_pk>\d+)/simpleunitdelete/(?P<simpleunit_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_units.SimpleUnitDeleteView.as_view(), name='simpledelete'),

    ################################### Compound Units Url #######################################

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/compoundunitlist$',
        views_units.CompoundUnitListView.as_view(), name='compoundlist'),

    url(r'^company/(?P<company_pk>\d+)/compoundunitdetail/(?P<compound_unit_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_units.CompoundUnitDetailView.as_view(), name='compounddetail'),

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/compoundunitcreate/$',
        views_units.CompoundUnitCreateView.as_view(), name='compoundcreate'),

    url(r'^company/(?P<company_pk>\d+)/compoundunitupdate/(?P<compound_unit_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_units.CompoundUnitUpdateView.as_view(), name='compoundupdate'),

    url(r'^company/(?P<company_pk>\d+)/compoundunitdelete/(?P<compound_unit_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_units.CompoundUnitDeleteView.as_view(), name='compounddelete'),

    ################################### Stock Group Url #######################################

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/stockgrouplist$',
        views_stock.StockGroupListView.as_view(), name='stockgrouplist'),

    url(r'^company/(?P<company_pk>\d+)/stockgroupdetail/(?P<stock_group_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_stock.StockGroupDetailView.as_view(), name='stockgroupdetail'),

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/stockgroupcreate/$',
        views_stock.StockGroupCreateView.as_view(), name='stockgroupcreate'),

    url(r'^company/(?P<company_pk>\d+)/stockgroupupdate/(?P<stock_group_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_stock.StockGroupUpdateView.as_view(), name='stockgroupupdate'),

    url(r'^company/(?P<company_pk>\d+)/stockgroupdelete/(?P<stock_group_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_stock.StockGroupDeleteView.as_view(), name='stockgroupdelete'),


    ################################### Stock Item Monthly Url ######################################

    url(r'^company/(?P<company_pk>\d+)/stockmonthly/(?P<stock_item_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_stock.stock_item_month_view, name='stockmonthly'),

    url(r'^company/(?P<company_pk>\d+)/stockrdatewise/month/(?P<month>\d+)/year/(?P<year>\d+)/(?P<stock_item_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_stock.StockSummaryDatewise, name='stockdatewise'),

    ################################### Stock Item Url #######################################

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/stockdata/$',
        views_stock.StockItemListview.as_view(), name='stockdatalist'),

    url(r'^company/(?P<company_pk>\d+)/stockdatadetail/(?P<stock_item_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_stock.StockItemDetailView.as_view(), name='stockdatadetail'),

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/stockdatacreate/$',
        views_stock.StockItemCreateview.as_view(), name='stockdatacreate'),

    url(r'^company/(?P<company_pk>\d+)/stockdataupdate/(?P<stock_item_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_stock.StockItemUpdateview.as_view(), name='stockdataupdate'),

    url(r'^company/(?P<company_pk>\d+)/stockdatadelete/(?P<stock_item_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_stock.StockItemDeleteview.as_view(), name='stockdatadelete'),

    ################################### Closing Stock Url #######################################

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_stock.ClosingListView.as_view(), name='closingstock'),


    ################################### PurchaseVoucher Url #######################################

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/purchase/$',
        views_purchase.PurchaseListView.as_view(), name='purchaselist'),

    url(r'^company/(?P<company_pk>\d+)/purchasedetail/(?P<purchase_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_purchase.PurchaseDetailsView.as_view(), name='purchasedetail'),

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/purchasecreate/$',
        views_purchase.PurchaseCreateView.as_view(), name='purchasecreate'),

    url(r'^company/(?P<company_pk>\d+)/purchaseupdate/(?P<purchase_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_purchase.PurchaseUpdateView.as_view(), name='purchaseupdate'),

    url(r'^company/(?P<company_pk>\d+)/purchasedelete/(?P<purchase_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_purchase.PurchaseDeleteView.as_view(), name='purchasedelete'),

    ################################### Purchase Register Url #######################################

    url(r'^company/(?P<company_pk>\d+)/Purchase_Register/date/(?P<period_selected_pk>\d+)/$',
        views_purchase.PurchaseRegisterView.as_view(), name='purchase_register'),

    url(r'^company/(?P<company_pk>\d+)/purchasedatewise/month/(?P<month>\d+)/year/(?P<year>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_purchase.purchase_register_datewise, name='purchase_datewise'),

    ################################### Sales Url #######################################

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/sales$',
        views_sales.SalesListView.as_view(), name='saleslist'),

    url(r'^company/(?P<company_pk>\d+)/salesdetail/(?P<sales_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_sales.SalesDetailsView.as_view(), name='salesdetail'),

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/salescreate/$',
        views_sales.SalesCreateView.as_view(), name='salescreate'),

    url(r'^company/(?P<company_pk>\d+)/salesupdate/(?P<sales_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_sales.SalesUpdateView.as_view(), name='salesupdate'),

    url(r'^company/(?P<company_pk>\d+)/salesdelete/(?P<sales_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_sales.SalesDeleteView.as_view(), name='salesdelete'),


    ################################### Sale Register Url #######################################

    url(r'^company/(?P<company_pk>\d+)/Sale_Register/date/(?P<period_selected_pk>\d+)/$',
        views_sales.SalesRegisterView.as_view(), name='sale_register'),

    url(r'^company/(?P<company_pk>\d+)/salesdatewise/month/(?P<month>\d+)/year/(?P<year>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_sales.SalesRegisterDatewise, name='sales_datewise'),


    ################################### DEBIT Note Url #######################################

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/debit_note/$',
        views_debit_note.DebitNoteListview.as_view(), name='debitlist'),

    url(r'^company/(?P<company_pk>\d+)/debit_notedetail/(?P<debit_note_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_debit_note.DebitNoteDetailsView.as_view(), name='debitdetail'),

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/debit_notecreate/$',
        views_debit_note.DebitNoteCreateview.as_view(), name='debitcreate'),

    url(r'^company/(?P<company_pk>\d+)/debit_noteupdate/(?P<debit_note_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_debit_note.DebitNoteUpdateView.as_view(), name='debitupdate'),

    url(r'^company/(?P<company_pk>\d+)/debit_notedelete/(?P<debit_note_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_debit_note.DebitNoteDeleteView.as_view(), name='debitdelete'),


    ################################### CREDIT Note Url #######################################

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/credit_note/$',
        views_credit_note.CreditNoteListview.as_view(), name='creditlist'),

    url(r'^company/(?P<company_pk>\d+)/credit_note/detail/(?P<credit_note_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_credit_note.CreditNoteDetailsView.as_view(), name='creditdetail'),

    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/credit_note/create/$',
        views_credit_note.CreditNoteCreateView.as_view(), name='creditcreate'),

    url(r'^company/(?P<company_pk>\d+)/credit_note/update/(?P<credit_note_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_credit_note.CreditNoteUpdateView.as_view(), name='creditupdate'),

    url(r'^company/(?P<company_pk>\d+)/credit_note/delete/(?P<credit_note_pk>\d+)/date/(?P<period_selected_pk>\d+)/$',
        views_credit_note.CreditNoteDeleteView.as_view(), name='creditdelete'),

    ################################### Profit & Loss Url #######################################

    url(r'^company/(?P<company_pk>\d+)/Profitloss/date/(?P<period_selected_pk>\d+)/$',
        views.profit_and_loss_view, name='profitloss'),

    ################################### Trial Balance Url #######################################

    url(r'^company/(?P<company_pk>\d+)/trialbalance/date/(?P<period_selected_pk>\d+)/$',
        views.trial_balance_view, name='trialbal'),

    ################################### Balance Sheet Url #######################################


    url(r'^company/(?P<company_pk>\d+)/balancesheet/date/(?P<period_selected_pk>\d+)/$',
        views.balance_sheet_view, name='balsht'),

]
