from django.conf.urls import url
from accounting_double_entry import views

app_name = 'accounting_double_entry'

urlpatterns = [

####### Export and Import Urls ########################################

    url(r'^company/(?P<pk>\d+)/date/(?P<pk3>\d+)/export_journal/$',views.export_journal,name='export_journal'), 
    url(r'^company/(?P<pk>\d+)/date/(?P<pk3>\d+)/import_journal/$',views.journal_upload,name='import_journal'), 
    url(r'^company/(?P<pk>\d+)/date/(?P<pk3>\d+)//export_ledger/$',views.getledgerObject_in_excel,name='export_ledger'),


####### Groups Urls ########################################

    url(r'^company/(?P<pk>\d+)/date/(?P<pk3>\d+)/grouplist/$',views.group1ListView.as_view(),name='grouplist'),    
    url(r'^company/(?P<pk1>\d+)/groupdetail/(?P<pk2>\d+)/date/(?P<pk3>\d+)/$',views.group1DetailView.as_view(),name='groupdetail'),
    url(r'^company/(?P<pk>\d+)/date/(?P<pk3>\d+)/groupcreate/$',views.group1CreateView.as_view(),name='groupcreate'),
    url(r'^company/(?P<pk1>\d+)/groupupdate/(?P<pk2>\d+)/date/(?P<pk3>\d+)/$',views.group1UpdateView.as_view(),name='groupupdate'),
    url(r'^company/(?P<pk>\d+)/groupdelete/(?P<pk2>\d+)/date/(?P<pk3>\d+)/$',views.group_delete_view,name='groupdelete'),

####### Group Summary Urls ########################################

    url(r'^company/(?P<pk>\d+)/date/(?P<pk3>\d+)/groupsummary/$',views.groupsummaryListView.as_view(),name='groupsummary'),    
    url(r'^company/(?P<pk>\d+)/groupdetailsummary/(?P<pk2>\d+)/date/(?P<pk3>\d+)/$',views.groupsummary_detail_view,name='groupdetailsummary'),


####### Ledger Monthly Url ########################################

    url(r'^company/(?P<pk>\d+)/ledgermonthly/(?P<pk2>\d+)/date/(?P<pk3>\d+)/$',views.ledger_monthly_detail_view,name='ledgerdetailmonthly'),
    url(r'^company/(?P<pk>\d+)/ledgerdatewise/(?P<month>\d+)/(?P<pk2>\d+)/date/(?P<pk3>\d+)/$',views.ledger_register_datewise,name='ledgerdatewise'),

    url(r'^company/(?P<pk>\d+)/ledgermonthly_2/(?P<pk2>\d+)/date/(?P<pk3>\d+)/$',views.ledger_monthly_detail_view_2,name='ledgerdetailmonthly_2'),
    url(r'^company/(?P<pk>\d+)/ledgerdatewise_2/(?P<month>\d+)/(?P<pk2>\d+)/date/(?P<pk3>\d+)/$',views.ledger_register_datewise_2,name='ledgerdatewise_2'),


####### Ledger Urls ########################################


    url(r'^company/(?P<pk>\d+)/date/(?P<pk3>\d+)/ledgerlist/$',views.ledger1ListView.as_view(),name='ledgerlist'),
    url(r'^company/(?P<pk>\d+)/ledgerdetail/(?P<pk2>\d+)/date/(?P<pk3>\d+)/$',views.ledger1_detail_view,name='ledgerdetail'),
    url(r'^company/(?P<pk>\d+)/date/(?P<pk3>\d+)/ledgercreate/$',views.ledger1CreateView.as_view(),name='ledgercreate'),
    url(r'^company/(?P<pk>\d+)/date/(?P<pk3>\d+)/ledgerupdate/(?P<pk2>\d+)/$',views.ledger1UpdateView.as_view(),name='ledgerupdate'),
    url(r'^company/(?P<pk>\d+)/date/(?P<pk3>\d+)/ledgerdelete/(?P<pk2>\d+)/$',views.ledger_delete_view,name='ledgerdelete'),


####### Bank Ledger Urls ########################################

    url(r'^company/(?P<pk>\d+)/date/(?P<pk3>\d+)/bankledgerlist/$',views.Bank_ledgerlistview.as_view(),name='bankledgerlist'),
    url(r'^company/(?P<pk>\d+)/bankledgerdetail/(?P<pk2>\d+)/date/(?P<pk3>\d+)/$',views.Bank_ledger1_detail_view,name='bankledgerdetail'),
    url(r'^company/(?P<pk1>\d+)/date/(?P<pk3>\d+)/bankjournallist/(?P<pk2>\d+)/$',views.bank_journal_detail,name='bankdetail'),
    url(r'^bankjournalupdate/(?P<id>\d+)/$',views.bank_journal_update,name='bankupdate'),

####### Journal Register Urls ########################################  

    url(r'^company/(?P<pk>\d+)/date/(?P<pk3>\d+)/journalregister/$',views.Journal_Register_view.as_view(),name='journalregister'),
    url(r'^company/(?P<pk>\d+)/journaldatewise/(?P<month>\d+)/date/(?P<pk3>\d+)/$',views.journal_register_datewise,name='journal_datewise'),

####### Journal Urls ########################################  

    url(r'^company/(?P<pk>\d+)/date/(?P<pk3>\d+)/journallist/$',views.journalListView.as_view(),name='list'),
    url(r'^company/(?P<pk1>\d+)/date/(?P<pk3>\d+)/journallist/(?P<pk2>\d+)/$',views.journal_detail,name='detail'),
    url(r'^company/(?P<pk>\d+)/date/(?P<pk3>\d+)/journal/create/$',views.journalCreateView.as_view(),name='create'),
    url(r'^company/(?P<pk1>\d+)/date/(?P<pk3>\d+)/journal/update/(?P<pk2>\d+)/$',views.journalUpdateView.as_view(),name='update'),
    url(r'^company/(?P<pk>\d+)/date/(?P<pk3>\d+)/journal/delete/(?P<pk2>\d+)/$',views.journal_delete_view,name='delete'),



####### Multijournal Urls ######################################## 

    url(r'^company/(?P<pk>\d+)/date/(?P<pk3>\d+)/multijournallist/$',views.Multijournal_listview.as_view(),name='multijournallist'),
    url(r'^company/(?P<pk>\d+)/date/(?P<pk3>\d+)/multijournaldetails/(?P<pk2>\d+)/$',views.multijournal_detail,name='multijournaldetail'),   
    url(r'^company/(?P<pk>\d+)/date/(?P<pk3>\d+)/multijournal/create/$',views.Multijournal_createview.as_view(),name='multijournalcreate'),
    url(r'^company/(?P<pk>\d+)/date/(?P<pk3>\d+)/multijournalupdate/(?P<pk2>\d+)/$',views.Multijournal_updateview.as_view(),name='multijournalupdate'),
    url(r'^company/(?P<pk>\d+)/date/(?P<pk3>\d+)/multijournal/delete/(?P<pk2>\d+)/$',views.multijournal_deleteview.as_view(),name='multijournaldelete'),


####### Daterange Urls ########################################  
  
    url(r'^daterangecreate/$',views.selectdate_create,name='datecreate'),
    url(r'^daterangeupdate/(?P<pk>\d+)/$',views.selectdate_update,name='dateupdate'),

####### Payment Urls ######################################## 

    url(r'^company/(?P<pk>\d+)/date/(?P<pk3>\d+)/payment/list/$',views.Payment_listview.as_view(),name='paymentlist'),
    url(r'^company/(?P<pk1>\d+)/date/(?P<pk3>\d+)/paymentdetails/(?P<pk2>\d+)/$',views.Payment_detailsview.as_view(),name='paymentdetail'),   
    url(r'^company/(?P<pk>\d+)/date/(?P<pk3>\d+)/payment/create/$',views.Payment_createview.as_view(),name='paymentcreate'),
    url(r'^company/(?P<pk1>\d+)/date/(?P<pk3>\d+)/paymentupdate/(?P<pk2>\d+)/$',views.Payment_updateview.as_view(),name='paymentupdate'),
    url(r'^company/(?P<pk>\d+)/date/(?P<pk3>\d+)/payment/delete/(?P<pk2>\d+)/$',views.Payment_deleteview.as_view(),name='paymentdelete'),

####### Receipt Urls ######################################## 

    url(r'^company/(?P<pk>\d+)/date/(?P<pk3>\d+)/receipt/list/$',views.Receipt_listview.as_view(),name='receiptlist'),
    url(r'^company/(?P<pk1>\d+)/date/(?P<pk3>\d+)/receipt/details/(?P<pk2>\d+)/$',views.Receipt_detailsview.as_view(),name='receiptdetail'), 
    url(r'^company/(?P<pk>\d+)/date/(?P<pk3>\d+)/receipt/create/$',views.Receipt_createview.as_view(),name='receiptcreate'),
    url(r'^company/(?P<pk1>\d+)/date/(?P<pk3>\d+)/receipt/update/(?P<pk2>\d+)/$',views.Receipt_updateview.as_view(),name='receiptupdate'),
    url(r'^company/(?P<pk>\d+)/date/(?P<pk3>\d+)/receipt/delete/(?P<pk2>\d+)/$',views.Receipt_deleteview.as_view(),name='receiptdelete'),


####### Contra Urls ######################################## 

    url(r'^company/(?P<pk>\d+)/date/(?P<pk3>\d+)/contra/list/$',views.Contra_listview.as_view(),name='contralist'),
    url(r'^company/(?P<pk1>\d+)/date/(?P<pk3>\d+)/contra/details/(?P<pk2>\d+)/$',views.Contra_detailsview.as_view(),name='contradetail'), 
    url(r'^company/(?P<pk>\d+)/date/(?P<pk3>\d+)/contra/create/$',views.Contra_createview.as_view(),name='contracreate'),
    url(r'^company/(?P<pk1>\d+)/date/(?P<pk3>\d+)/contra/update/(?P<pk2>\d+)/$',views.Contra_updateview.as_view(),name='contraupdate'),
    url(r'^company/(?P<pk>\d+)/date/(?P<pk3>\d+)/contra/delete/(?P<pk2>\d+)/$',views.Contra_deleteview.as_view(),name='contradelete'),

####### Daybook Urls ########################################

    url(r'^company/(?P<pk>\d+)/date/(?P<pk3>\d+)/daybook/$',views.DaybookListView.as_view(),name='daybook'),




    url(r'^company/(?P<pk>\d+)/trialbalance/date/(?P<pk3>\d+)/$',views.trial_balance_condensed_view,name='trialbalcond'),

    url(r'^company/(?P<pk>\d+)/PL/date/(?P<pk3>\d+)/$',views.profit_and_loss_condensed_view,name='PandLcond'),

    url(r'^company/(?P<pk>\d+)/balancesheet/date/(?P<pk3>\d+)/$',views.balance_sheet_condensed_view,name='blsht'),


    url(r'^company/(?P<pk>\d+)/cashbankbook/date/(?P<pk3>\d+)/$',views.cash_and_bank_view,name='cash_and_bank'),


]