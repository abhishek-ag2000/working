"""
URLs
"""
from django.conf.urls import url
from . import views

app_name = 'pdf_report'

urlpatterns = [

    ########################################### PDF URLS ############################################################################################################################
    url(r'^company/(?P<company_pk>\d+)/purchasedetailpdf/(?P<pk2>\d+)/date/(?P<period_selected_pk>\d+)/$', views.PDFGeneratorPurchase.as_view(), name='purchasedetailpdf'),
    url(r'^company/(?P<company_pk>\d+)/saledetailpdf/(?P<pk2>\d+)/date/(?P<period_selected_pk>\d+)/$', views.PDFGeneratorSale.as_view(), name='salesdetailpdf'),
    url(r'^company/(?P<company_pk>\d+)/ledgermonthlypdf/(?P<pk2>\d+)/date/(?P<period_selected_pk>\d+)/$', views.PDFGeneratorPeriodicJournal.as_view(), name='ledgerdetailmonthlypdf'),
]
