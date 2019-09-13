"""
View
"""
import calendar
import dateutil
import collections
import json
import decimal
import datetime
from datetime import datetime as dte, timedelta
from dateutil import relativedelta
from tablib import Dataset
import xlwt
from itertools import zip_longest
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.management import call_command
from django.db import IntegrityError
from django.db.models import Case, When, Value, Sum, Count, F, Q, ExpressionWrapper, Subquery, OuterRef, FloatField
from django.db.models.functions import Coalesce
from django.db.models.fields import DecimalField
from django.db.models.signals import pre_save, post_save, post_delete
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.views.generic import View, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.edit import FormMixin
from blog.models import Blog, BlogCategories, BlogComments
from consultancy.models import Consultancy, Answer
from ecommerce_integration.models import Product, ProductReview, Services, API, RoleBasedProduct
from ecommerce_integration.decorators import product_1_activation
from user_profile.models import Profile, ProductActivated, RoleBasedProductActivated
from messaging.models import Message
from accounting_entry.forms import DateRangeForm
from accounting_entry.models import JournalVoucher, LedgerGroup, LedgerMaster, PeriodSelected, PaymentVoucher,\
    PaymentVoucherRows, ReceiptVoucher, ReceiptVoucherRows, ContraVoucher, ContraVoucherRows, \
    MultiJournalVoucherDrRows, MultiJournalVoucher
from stock_keeping.models import StockGroup, SimpleUnit, CompoundUnit, StockItem, StockBalance
from stock_keeping.models_purchase import PurchaseVoucher, PurchaseStock
from stock_keeping.models_sale import SaleVoucher, SaleStock
from .models import Company, Organisation
from .forms import *
from .resources import CompanyResource
from django.db import transaction
from accounts_mode_voucher.model_purchase_accounts import PurchaseVoucherAccounts
from stock_keeping.models_purchase import PurchaseVoucher, PurchaseStock
from accounts_mode_voucher.models_sale_accounts import SaleVoucherAccounts
from stock_keeping.models_sale import SaleVoucher, SaleStock
from stock_keeping.models_debit_note import DebitNoteStock
from stock_keeping.models_credit_note import CreditNoteStock
from stock_keeping.models import StockItem


class ProductExistsRequiredMixin:
    """
    Validate if Bracket-Book product activated or role based privilege exists
    """

    def dispatch(self, request, *args, **kwargs):
        """
        Dispatch response
        """
        if ProductActivated.objects.filter(user=self.request.user, product__id=1, is_active=True) or \
           RoleBasedProductActivated.objects.filter(user=request.user, product__id=1, is_active=True):
            return super().dispatch(request, *args, **kwargs)
        raise PermissionDenied


class NormalProductExistsRequiredMixin:
    """
    Validate if Bracket-Book product activated
    """

    def dispatch(self, request, *args, **kwargs):
        """
        Dispatch response
        """
        if ProductActivated.objects.filter(user=self.request.user, product__id=1, is_active=True):
            return super().dispatch(request, *args, **kwargs)
        raise PermissionDenied


@login_required
@product_1_activation
def get_company_object(request, company_pk):
    """
    Get the company object
    """
    company = get_object_or_404(Company, pk=company_pk)

    all_objects = list(Company.objects.filter(pk=company_pk)) + \
        list(LedgerGroup.objects.filter(company=company)) + \
        list(LedgerMaster.objects.filter(company=company)) + \
        list(JournalVoucher.objects.filter(company=company)) + \
        list(PaymentVoucher.objects.filter(company=company)) + \
        list(PaymentVoucherRows.objects.filter(payment__company=company.pk)) + \
        list(ReceiptVoucher.objects.filter(company=company)) + \
        list(ReceiptVoucherRows.objects.filter(receipt__company=company.pk)) + \
        list(ContraVoucher.objects.filter(company=company)) + \
        list(ContraVoucherRows.objects.filter(contra__company=company.pk)) + \
        list(StockGroup.objects.filter(company=company)) + \
        list(SimpleUnit.objects.filter(company=company)) + \
        list(CompoundUnit.objects.filter(company=company)) + \
        list(StockItem.objects.filter(company=company)) + \
        list(PurchaseVoucher.objects.filter(company=company)) + \
        list(PurchaseStock.objects.filter(purchases__company=company.pk)) + \
        list(SaleVoucher.objects.filter(company=company)) + \
        list(SaleStock.objects.filter(sales__company=company.pk)) + \
        list(StockBalance.objects.filter(company=company))

    data = serializers.serialize('json', all_objects)
    data = json.dumps(json.loads(data), indent=4)
    response = HttpResponse(data, content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename={}-{}.json'.format(
        company.name, dte.now())
    return response


@login_required
@product_1_activation
def get_company_excel(request, company_pk):
    company = get_object_or_404(Company, pk=company_pk)
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename={}.xls'.format(
        company.name)

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Company')
    wg = wb.add_sheet('Ledger_Groups')
    wl = wb.add_sheet('Ledgers')
    wj = wb.add_sheet('Journals')
    wp = wb.add_sheet('Payments')
    wr = wb.add_sheet('Receipts')
    wc = wb.add_sheet('Contra')
    wsg = wb.add_sheet('Stock_Groups')
    wsm = wb.add_sheet('SimpleUnits')
    wcu = wb.add_sheet('CompoundUnits')
    wst = wb.add_sheet('StockItems')
    wpu = wb.add_sheet('Purchases')
    wps = wb.add_sheet('Purchase_Stock')
    wsa = wb.add_sheet('SaleVoucher')
    wss = wb.add_sheet('Sales_Stock')
    wsc = wb.add_sheet('Stock_Closing')

    # Sheet header, first row
    row_num = 0
    row_num1 = 0
    row_num2 = 0
    row_num3 = 0
    row_num4 = 0
    row_num5 = 0
    row_num6 = 0
    row_num7 = 0
    row_num8 = 0
    row_num9 = 0
    row_num10 = 0
    row_num11 = 0
    row_num12 = 0
    row_num13 = 0
    row_num14 = 0
    row_num15 = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    font_style.num_format_str = 'MM/dd/yyyy'

    columns = ['user', 'id', 'created_date', 'modified_date', 'name', 'bussiness_nature', 'maintain', 'type_of_company',
               'address', 'country', 'state', 'financial_year_from', 'books_begining_from', 'GST_enabled', 'gst_registration_type', ]
    columns_g = ['Group_Name', 'Voucher_Id',
                 'Parent', 'Nature', 'Balance_Nature']
    columns_l = ['Group_Name', 'Voucher_Id', 'Ledger_Name', 'Opening', 'Balance_Nature', 'Contact_Name', 'address', 'state',
                 'PIN', 'PAN', 'GST_No']
    columns_j = ['Date', 'Voucher_Id',
                 'Voucher_Type', 'By', 'To', 'Debit', 'Credit']
    columns_p = ['Date', 'Voucher_Id', 'Payment_Account',
                 'Payment_Particular', 'Payment_Amount']
    columns_r = ['Date', 'Voucher_Id', 'Receipt_Account',
                 'Receipt_Particular', 'Receipt_Amount']
    columns_c = ['Date', 'Voucher_Id', 'Contra_Account',
                 'Contra_Particular', 'Contra_Amount']
    columns_sg = ['Group_Name', 'Voucher_Id', 'Parent', ]
    columns_sm = ['Symbol', 'Voucher_Id', 'Formal_Name', ]
    columns_cu = ['First_Unit', 'Voucher_Id', 'Conversion', 'Seconds_Unit']
    columns_st = ['Stock_Name', 'Voucher_Id', 'GST_Rate',
                  'Quantity', 'Rate', 'Opening', 'Group_Name', 'HSN', 'Unit']
    columns_pu = ['Date', 'Voucher_Id', 'Invoice_No', 'Party_Account', 'Purchase_Account', 'Party_Name', 'address',
                  'state', 'PAN', 'GST_No', 'Sub_Total', 'CGST_Total', 'SGST_IGST_Total', 'Composite_Tax', 'Total']
    columns_ps = ['Voucher_Id', 'Stock_Name', 'Simple_Unit', 'Quantity', 'Rate', 'Discount', 'GST_Rate', 'Master_GST_Rate',
                  'Sub_Total', 'CGST_Total', 'SGST_IGST_Total', 'Composite_Tax', 'Total']
    columns_sa = ['Date', 'Voucher_Id', 'Invoice_No', 'Party_Account', 'Sales_Account', 'Party_Name', 'address',
                  'state', 'PAN', 'GST_No', 'Sub_Total', 'CGST_Total', 'SGST_IGST_Total', 'Composite_Tax', 'Total']
    columns_ss = ['Voucher_Id', 'Stock_Name', 'Simple_Unit', 'Quantity', 'Rate', 'Discount', 'GST_Rate', 'Master_GST_Rate',
                  'Sub_Total', 'CGST_Total', 'SGST_IGST_Total', 'Composite_Tax', 'Total']
    columns_sc = ['Stock_Name', 'Voucher_Id', 'Opening_Stock',
                  'Closing_Quantity', 'Closing_Stock', ]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    for col_num_g in range(len(columns_g)):
        wg.write(row_num, col_num_g, columns_g[col_num_g], font_style)

    for col_num_l in range(len(columns_l)):
        wl.write(row_num, col_num_l, columns_l[col_num_l], font_style)

    for col_num_j in range(len(columns_j)):
        wj.write(row_num, col_num_j, columns_j[col_num_j], font_style)

    for col_num_p in range(len(columns_p)):
        wp.write(row_num, col_num_p, columns_p[col_num_p], font_style)

    for col_num_r in range(len(columns_r)):
        wr.write(row_num, col_num_r, columns_r[col_num_r], font_style)

    for col_num_c in range(len(columns_c)):
        wc.write(row_num, col_num_c, columns_c[col_num_c], font_style)

    for col_num_sg in range(len(columns_sg)):
        wsg.write(row_num, col_num_sg, columns_sg[col_num_sg], font_style)

    for col_num_sm in range(len(columns_sm)):
        wsm.write(row_num, col_num_sm, columns_sm[col_num_sm], font_style)

    for col_num_cu in range(len(columns_cu)):
        wcu.write(row_num, col_num_cu, columns_cu[col_num_cu], font_style)

    for col_num_st in range(len(columns_st)):
        wst.write(row_num, col_num_st, columns_st[col_num_st], font_style)

    for col_num_pu in range(len(columns_pu)):
        wpu.write(row_num, col_num_pu, columns_pu[col_num_pu], font_style)

    for col_num_ps in range(len(columns_ps)):
        wps.write(row_num, col_num_ps, columns_ps[col_num_ps], font_style)

    for col_num_sa in range(len(columns_sa)):
        wsa.write(row_num, col_num_sa, columns_sa[col_num_sa], font_style)

    for col_num_ss in range(len(columns_ss)):
        wss.write(row_num, col_num_ss, columns_ss[col_num_ss], font_style)

    for col_num_sc in range(len(columns_sc)):
        wsc.write(row_num, col_num_sc, columns_sc[col_num_sc], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    companys = Company.objects.filter(pk=company_pk)
    companys = companys.extra(select={
                              'datestr': "to_char(created_date, 'DD-MM-YYYY')", 'datestr1': "to_char(modified_date, 'DD-MM-YYYY')"})
    rows = companys.values_list('User__username', 'id', 'datestr', 'datestr1', 'name', 'bussiness_nature', 'maintain', 'type_of_company',
                                'address', 'country', 'state', 'financial_year_from', 'books_begining_from', 'gst_enabled', 'gst_registration_type')

    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    rows_g = LedgerGroup.objects.filter(company=company).exclude(group_base__name__contains='Primary').values_list(
        'group_name', 'id', 'Master__group_Name', 'base__name', 'base__is_debit')

    for row in rows_g:
        row_num1 += 1
        for col_num in range(len(row)):
            wg.write(row_num1, col_num, row[col_num], font_style)

    rows_l = LedgerMaster.objects.filter(company=company).values_list('LedgerGroup_Name__group_Name', 'id', 'ledger_name', 'Balance_opening',
                                                                      'LedgerGroup_Name__base__is_debit', 'user_name', 'address', 'state', 'Pin_Code', 'PanIt_No', 'GST_No')

    for row in rows_l:
        row_num2 += 1
        for col_num in range(len(row)):
            wl.write(row_num2, col_num, row[col_num], font_style)

    rows_j = JournalVoucher.objects.filter(company=company).values_list(
        'Date', 'voucher_id', 'voucher_type', 'By__ledger_name', 'To__ledger_name', 'Debit', 'Credit')

    for row in rows_j:
        row_num3 += 1
        for col_num in range(len(row)):
            wj.write(row_num3, col_num, row[col_num], font_style)

    rows_p = PaymentVoucherRows.objects.filter(payment__company=company.pk).values_list(
        'payment__date', 'payment__id', 'payment__account__ledger_name', 'particular__ledger_name', 'amount')

    for row in rows_p:
        row_num4 += 1
        for col_num in range(len(row)):
            wp.write(row_num4, col_num, row[col_num], font_style)

    rows_r = ReceiptVoucherRows.objects.filter(receipt__company=company.pk).values_list(
        'receipt__date', 'receipt__id', 'receipt__account__ledger_name', 'particular__ledger_name', 'amount')

    for row in rows_r:
        row_num5 += 1
        for col_num in range(len(row)):
            wr.write(row_num5, col_num, row[col_num], font_style)

    rows_c = ContraVoucherRows.objects.filter(contra__company=company.pk).values_list(
        'contra__date', 'contra__id', 'contra__account__ledger_name', 'particular__ledger_name', 'amount')

    for row in rows_c:
        row_num6 += 1
        for col_num in range(len(row)):
            wc.write(row_num6, col_num, row[col_num], font_style)

    rows_sg = StockGroup.objects.filter(
        company=company).values_list('name', 'id', 'under__name')

    for row in rows_sg:
        row_num7 += 1
        for col_num in range(len(row)):
            wsg.write(row_num7, col_num, row[col_num], font_style)

    rows_sm = SimpleUnit.objects.filter(
        company=company).values_list('symbol', 'id', 'formal')

    for row in rows_sm:
        row_num8 += 1
        for col_num in range(len(row)):
            wsm.write(row_num8, col_num, row[col_num], font_style)

    rows_cu = CompoundUnit.objects.filter(company=company).values_list(
        'firstunit', 'id', 'conversion', 'seconds_unit')

    for row in rows_cu:
        row_num9 += 1
        for col_num in range(len(row)):
            wcu.write(row_num9, col_num, row[col_num], font_style)

    rows_st = StockItem.objects.filter(company=company).values_list(
        'stock_name', 'id', 'gst_rate', 'Quantity', 'rate', 'opening', 'under__name', 'hsn', 'simple_unit__symbol')

    for row in rows_st:
        row_num10 += 1
        for col_num in range(len(row)):
            wst.write(row_num10, col_num, row[col_num], font_style)

    rows_pu = PurchaseVoucher.objects.filter(company=company).values_list('date', 'id', 'ref_no', 'Party_ac__ledger_name', 'purchase__ledger_name', 'billname',
                                                                          'address', 'state', 'PAN', 'GSTIN', 'sub_total', 'cgst_total', 'gst_alltotal', 'tax_total', 'Total')

    for row in rows_pu:
        row_num11 += 1
        for col_num in range(len(row)):
            wpu.write(row_num11, col_num, row[col_num], font_style)

    rows_ps = PurchaseStock.objects.filter(purchases__company=company.pk).values_list('purchases__id', 'stockitem__stock_name', 'stockitem__simple_unit__symbol',
                                                                                      'Quantity_p', 'rate_p', 'Disc_p', 'gst_rate', 'stockitem__gst_rate', 'Total_p', 'cgst_total', 'gst_total', 'tax_total', 'grand_total')

    for row in rows_ps:
        row_num12 += 1
        for col_num in range(len(row)):
            wps.write(row_num12, col_num, row[col_num], font_style)

    rows_sa = SaleVoucher.objects.filter(company=company).values_list('date', 'id', 'ref_no', 'Party_ac__ledger_name', 'sales__ledger_name', 'billname',
                                                                      'address', 'state', 'PAN', 'GSTIN', 'sub_total', 'cgst_total', 'gst_alltotal', 'tax_total', 'Total')

    for row in rows_sa:
        row_num13 += 1
        for col_num in range(len(row)):
            wsa.write(row_num13, col_num, row[col_num], font_style)

    rows_ss = SaleStock.objects.filter(sales__company=company.pk).values_list('sales__id', 'stockitem__stock_name', 'stockitem__simple_unit__symbol', 'Quantity',
                                                                              'rate', 'Disc', 'gst_rate', 'stockitem__gst_rate', 'Total', 'cgst_total', 'gst_total', 'tax_total', 'grand_total')

    for row in rows_ss:
        row_num14 += 1
        for col_num in range(len(row)):
            wss.write(row_num14, col_num, row[col_num], font_style)

    rows_ss = StockBalance.objects.filter(company=company).values_list(
        'stockitem__stock_name', 'stockitem__id', 'opening_stock', 'closing_quantity', 'closing_stock')

    for row in rows_ss:
        row_num15 += 1
        for col_num in range(len(row)):
            wsc.write(row_num15, col_num, row[col_num], font_style)

    wb.save(response)

    return response


@login_required
def company_upload(request):
    if request.method == 'POST':
        new_company = request.FILES['myfile']

        # call_command('loaddata', new_company)

        obj_generator = serializers.json.Deserializer(new_company)

        for obj in obj_generator:
            obj.save()

    return render(request, 'company/import.html')


class OrganisationCreateView(LoginRequiredMixin, CreateView):
    """
    Organisation Create View
    """
    form_class = OrganisationForm
    template_name = "organisation/organisation_form.html"

    def get_success_url(self, **kwargs):
        return reverse('company:list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        counter = Organisation.objects.filter(
            user=self.request.user).count() + 1
        form.instance.counter = counter
        return super(OrganisationCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(OrganisationCreateView,
                        self).get_context_data(**kwargs)
        context['products_aggrement'] = ProductActivated.objects.filter(
            user=self.request.user, product__id=9, is_active=True)
        context['active_product_1'] = ProductActivated.objects.filter(
            user=self.request.user, product__id=1, is_active=True)
        context['role_product_1'] = RoleBasedProductActivated.objects.filter(
            user=self.request.user, product__id=1, is_active=True)
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['legal_product'] = ProductActivated.objects.filter(
            user=self.request.user, product__id=10, is_active=True)
        return context


class OrganisationUpdateView(LoginRequiredMixin, UpdateView):
    """
    Organisation Update View
    """
    model = Organisation
    form_class = OrganisationForm
    template_name = "organisation/organisation_form.html"

    def get_object(self):
        return get_object_or_404(Organisation, pk=self.kwargs['organisation_pk'])

    def get_success_url(self, **kwargs):
        period_selected = get_object_or_404(
            PeriodSelected, user=self.request.user)
        organisation = self.get_object()
        return reverse('company:CommonDashboard', kwargs={'organisation_pk': organisation.pk, 'period_selected_pk': period_selected.pk})

    def get_context_data(self, **kwargs):
        context = super(OrganisationUpdateView,
                        self).get_context_data(**kwargs)
        period_selected = get_object_or_404(
            PeriodSelected, user=self.request.user)
        context['period_selected'] = period_selected
        context['products_aggrement'] = ProductActivated.objects.filter(
            user=self.request.user, product__id=9, is_active=True)
        context['active_product_1'] = ProductActivated.objects.filter(
            user=self.request.user, product__id=1, is_active=True)
        context['role_product_1'] = RoleBasedProductActivated.objects.filter(
            user=self.request.user, product__id=1, is_active=True)
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['legal_product'] = ProductActivated.objects.filter(
            user=self.request.user, product__id=10, is_active=True)
        return context


class OrganisationListView(LoginRequiredMixin, ListView):
    """
    Organisation List View
    """
    context_object_name = 'organisation_list'
    model = Organisation
    template_name = "organisation/organisation_list.html"
    paginate_by = 10

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Organisation.objects.filter(user=self.request.user).order_by('id')
        else:
            return Organisation.objects.none()

    def get_context_data(self, **kwargs):
        context = super(OrganisationListView, self).get_context_data(**kwargs)

        context['period_selected'], created = PeriodSelected.objects.get_or_create(  # get_or_create returns tuple of instance, created
            user=self.request.user,
            defaults={
                'start_date': datetime.date((dte.now().year), 4, 1),
                'end_date': datetime.date((dte.now().year) + 1, 3, 31)
            }
        )

        if self.request.user.is_authenticated:
            context['products_aggrement'] = ProductActivated.objects.filter(
                user=self.request.user, product__id=9, is_active=True)
            context['Products'] = ProductActivated.objects.filter(
                user=self.request.user, product__id=1, is_active=True)

            context['Products_QR'] = ProductActivated.objects.filter(
                user=self.request.user, product__id=3, is_active=True)
            
           

            context['active_product_1'] = ProductActivated.objects.filter(
                user=self.request.user, product__id=1, is_active=True)
            context['role_product_1'] = RoleBasedProductActivated.objects.filter(
                user=self.request.user, product__id=1, is_active=True)

            context['inbox'] = Message.objects.filter(
                reciever=self.request.user)
            context['inbox_count'] = context['inbox'].aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
                the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

            context['auditor_company'] = Company.objects.filter(
                auditor=self.request.user).order_by('id')
            context['accountant_company'] = Company.objects.filter(
                accountant=self.request.user).order_by('id')
            context['purchase_company'] = Company.objects.filter(
                purchase_personel=self.request.user).order_by('id')
            context['sales_company'] = Company.objects.filter(
                sale_personel=self.request.user).order_by('id')
            context['cb_company'] = Company.objects.filter(
                cb_personal=self.request.user).order_by('id')
            context['shared_companys'] = zip_longest(
                context['auditor_company'], context['accountant_company'], context['purchase_company'], context['sales_company'], context['cb_company'])
            context['legal_product'] = ProductActivated.objects.filter(
                user=self.request.user, product__id=10, is_active=True)
        return context


class OrganisationDetailsView(LoginRequiredMixin, DetailView):
    """
    Common Dashboard for Specific Company View
    """
    context_object_name = 'organisation'
    model = Organisation
    template_name = 'company/CommonDashboard.html'

    def get_object(self):
        return get_object_or_404(Organisation, pk=self.kwargs['organisation_pk'])

    def get_context_data(self, **kwargs):
        context = super(OrganisationDetailsView,
                        self).get_context_data(**kwargs)
        company = self.get_object()
        context['static_page_details'] = StaticPage.objects.filter(
            organisation=company.pk).first()
        context['Products_legal'] = ProductActivated.objects.filter(
            user=self.request.user, product__id=10, is_active=True)
        context['company'] = company
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        context['Products'] = ProductActivated.objects.filter(
            user=self.request.user, product__id=1, is_active=True)
        context['Products_QR'] = ProductActivated.objects.filter(
            user=self.request.user, product__id=3, is_active=True)
        context['inbox'] = Message.objects.filter(
            reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        return context


class CompanyDetailView(DetailView, ProductExistsRequiredMixin, LoginRequiredMixin):
    """
    Company Detail View
    """
    context_object_name = 'company'
    model = Company
    template_name = 'company/Dashboard.html'

    def get_object(self):
        return get_object_or_404(Company, pk=self.kwargs['company_pk'])

    def get_context_data(self, **kwargs):
        context = super(CompanyDetailView, self).get_context_data(**kwargs)

        # get_object_or_404(Company, pk=self.kwargs['company_pk'])
        company = self.get_object()
        context['legal_product'] = ProductActivated.objects.filter(
            user=self.request.user, product__id=10, is_active=True)
        context['company'] = company
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        context['active_product_1'] = ProductActivated.objects.filter(
            user=self.request.user, product__id=1, is_active=True)
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['blogs'] = Blog.objects.all().order_by('-id')
        context['consultancies'] = Consultancy.objects.all().order_by('-id')

        # Graphs FIlter of Total Values
        results = collections.OrderedDict()
        sales_inventory_result = SaleVoucher.objects.filter(company=company.pk, voucher_date__gte=period_selected.start_date, voucher_date__lt=period_selected.end_date).annotate(
            real_total=Case(When(total__isnull=True, then=0), default=F('total')))

        sales_accounts_result = SaleVoucherAccounts.objects.filter(company=company.pk, voucher_date__gte=period_selected.start_date, voucher_date__lt=period_selected.end_date).annotate(
            real_total=Case(When(total__isnull=True, then=0), default=F('total')))

        purchase_inventory_result = PurchaseVoucher.objects.filter(company=company.pk, voucher_date__gte=period_selected.start_date, voucher_date__lt=period_selected.end_date).annotate(
            real_total=Case(When(total__isnull=True, then=0), default=F('total')))

        purchase_accounts_result = PurchaseVoucherAccounts.objects.filter(company=company.pk, voucher_date__gte=period_selected.start_date, voucher_date__lt=period_selected.end_date).annotate(
            real_total=Case(When(total__isnull=True, then=0), default=F('total')))

        date_cursor = period_selected.start_date

        while date_cursor < period_selected.end_date:

            month_partial_sales_inventory = sales_inventory_result.filter(voucher_date__month=date_cursor.month, voucher_date__year=date_cursor.year).aggregate(
                partial_total=Coalesce(Sum('real_total'), Value(0)))['partial_total']

            month_partial_sales_accounts = sales_accounts_result.filter(voucher_date__month=date_cursor.month, voucher_date__year=date_cursor.year).aggregate(
                partial_total=Coalesce(Sum('real_total'), Value(0)))['partial_total']

            month_partial_purchase_inventory = purchase_inventory_result.filter(voucher_date__month=date_cursor.month, voucher_date__year=date_cursor.year).aggregate(
                partial_total=Coalesce(Sum('real_total'), Value(0)))['partial_total']

            month_partial_purchase_accounts = purchase_accounts_result.filter(voucher_date__month=date_cursor.month, voucher_date__year=date_cursor.year).aggregate(
                partial_total=Coalesce(Sum('real_total'), Value(0)))['partial_total']

            total_sales = month_partial_sales_inventory + month_partial_sales_accounts

            total_purchase = month_partial_purchase_inventory + month_partial_purchase_accounts

            results[(date_cursor.month, date_cursor.year)] = [
                total_sales, total_purchase]

            date_cursor += dateutil.relativedelta.relativedelta(months=1)

        context['results'] = results.items()

        # Opening Stock Calculations

        # Opening Stock
        Stock_item_list = StockItem.objects.filter(company=company)
        total_purchase_stock_in_range = PurchaseStock.objects.filter(
            purchase_voucher__voucher_date__lt=period_selected.start_date).values('stock_item')
        total_sales_stock_in_range = SaleStock.objects.filter(
            sale_voucher__voucher_date__lt=period_selected.start_date).values('stock_item')
        total_debit_note_stock_in_range = DebitNoteStock.objects.filter(
            debit_note__voucher_date__lt=period_selected.start_date).values('stock_item')
        total_credit_note_stock_in_range = CreditNoteStock.objects.filter(
            credit_note__voucher_date__lt=period_selected.start_date).values('stock_item')

        stock_item_quantity = Stock_item_list.aggregate(
            the_sum=Coalesce(Sum('quantity'), Value(0)))['the_sum']

        stock_item_opening = Stock_item_list.aggregate(
            the_sum=Coalesce(Sum('opening'), Value(0)))['the_sum']

        total_purchase_quantity = total_purchase_stock_in_range.aggregate(
            the_sum=Coalesce(Sum('quantity'), Value(0)))['the_sum']

        total_purchase_stock = total_purchase_stock_in_range.aggregate(
            the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']

        total_sales_quantity = total_sales_stock_in_range.aggregate(
            the_sum=Coalesce(Sum('quantity'), Value(0)))['the_sum']

        total_debitnote_quantity = total_debit_note_stock_in_range.aggregate(
            the_sum=Coalesce(Sum('quantity'), Value(0)))['the_sum']

        total_debit_note = total_debit_note_stock_in_range.aggregate(
            the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']

        total_creditnote_quantity = total_credit_note_stock_in_range.aggregate(
            the_sum=Coalesce(Sum('quantity'), Value(0)))['the_sum']

        if not total_purchase_quantity:
            total_purchase_quantity = 0

        if not total_purchase_stock:
            total_purchase_stock = 0

        if not total_sales_quantity:
            total_sales_quantity = 0

        if not total_debitnote_quantity:
            total_debitnote_quantity = 0

        if not total_debit_note:
            total_debit_note = 0

        if not total_debit_note:
            total_debit_note = 0

        if not total_creditnote_quantity:
            total_creditnote_quantity = 0

        total_purchase_quantity_os = total_purchase_quantity - total_debitnote_quantity
        total_purchase_os = total_purchase_stock - total_debit_note

        total_sales_quantity_os = total_sales_quantity - total_creditnote_quantity

        if not stock_item_quantity:
            opening_quantity = (
                total_purchase_quantity - (total_debitnote_quantity + total_sales_quantity_os))
        else:
            opening_quantity = stock_item_quantity + \
                (total_purchase_quantity -
                 (total_debitnote_quantity + total_sales_quantity_os))

        if total_purchase_quantity_os != 0 and opening_quantity != 0 and total_purchase_os != 0:
            opening_stock = stock_item_opening + \
                (((total_purchase_os) / (total_purchase_quantity_os))
                 * opening_quantity)  # for weighted average
        else:
            # opening_stock = stock_item_opening + (((total_purchase_os) / (total_purchase_quantity_os)) * opening_quantity)  # for weighted average
            opening_stock = stock_item_opening

        if not opening_stock:
            opening_stock = 0

        # Closing Stock Calculation
        purchase_stock = PurchaseStock.objects.filter(purchase_voucher__company=company, stock_item=OuterRef(
            'pk'), purchase_voucher__voucher_date__gte=period_selected.start_date, purchase_voucher__voucher_date__lte=period_selected.end_date).values('stock_item')
        purchase_stock_total = PurchaseStock.objects.filter(purchase_voucher__company=company, stock_item=OuterRef(
            'pk'), purchase_voucher__voucher_date__gte=period_selected.start_date, purchase_voucher__voucher_date__lte=period_selected.end_date).values('stock_item')
        sales_stock = SaleStock.objects.filter(sale_voucher__company=company, stock_item=OuterRef(
            'pk'), sale_voucher__voucher_date__gte=period_selected.start_date, sale_voucher__voucher_date__lte=period_selected.end_date).values('stock_item')
        debit_note_stock = DebitNoteStock.objects.filter(debit_note__company=company, stock_item=OuterRef(
            'pk'), debit_note__voucher_date__gte=period_selected.start_date, debit_note__voucher_date__lte=period_selected.end_date).values('stock_item')
        credit_note_stock = CreditNoteStock.objects.filter(credit_note__company=company, stock_item=OuterRef(
            'pk'), credit_note__voucher_date__gte=period_selected.start_date, credit_note__voucher_date__lte=period_selected.end_date).values('stock_item')

        total_purchase_quantity = purchase_stock.annotate(
            quantity_total=Coalesce(Sum('quantity'), Value(0))).values('quantity_total')

        total_purchase_value = purchase_stock_total.annotate(
            total=Coalesce(Sum('total'), Value(0))).values('total')

        total_sales_quantity = sales_stock.annotate(
            quantity_total=Coalesce(Sum('quantity'), Value(0))).values('quantity_total')

        total_debit_note_quantity = debit_note_stock.annotate(
            quantity_total=Coalesce(Sum('quantity'), Value(0))).values('quantity_total')

        total_credit_note_quantity = credit_note_stock.annotate(
            quantity_total=Coalesce(Sum('quantity'), Value(0))).values('quantity_total')

        stock_list = StockItem.objects.filter(company=company).annotate(
            purchase_quantity=Coalesce(
                Subquery(total_purchase_quantity, output_field=FloatField()), Value(0)),
            sales_quantity=Coalesce(
                Subquery(total_sales_quantity, output_field=FloatField()), Value(0)),
            debit_note_quantity=Coalesce(
                Subquery(total_debit_note_quantity, output_field=FloatField()), Value(0)),
            credit_note_quantity=Coalesce(
                Subquery(total_credit_note_quantity, output_field=FloatField()), Value(0)),
            purchase_value=Coalesce(
                Subquery(total_purchase_value, output_field=FloatField()), Value(0)),
        )

        stock_quantities = stock_list.annotate(
            total_purchase_quantity_final=ExpressionWrapper(
                F('purchase_quantity') - F('debit_note_quantity'), output_field=FloatField()),
            total_sales_quantity_final=ExpressionWrapper(
                F('sales_quantity') - F('credit_note_quantity'), output_field=FloatField()),
        )

        stock_closing_quantity = stock_quantities.annotate(
            closing_quantity=ExpressionWrapper(F('quantity') + F('total_purchase_quantity_final') - F(
                'total_sales_quantity_final'), output_field=FloatField()),
            grand_total_purchase_quantity=ExpressionWrapper(
                F('quantity') + F('total_purchase_quantity_final'), output_field=FloatField()),
            grand_total_purchase=ExpressionWrapper(
                F('purchase_value') + F('opening'), output_field=FloatField()),
        )

        closing_balance_only_purchase = stock_closing_quantity.annotate(
            purchase_closing_balance=Case(
                When(grand_total_purchase_quantity__gt=0, then=F(
                    'grand_total_purchase') / F('grand_total_purchase_quantity')),
                default=0,
                output_field=FloatField()
            )
        )

        closing_balance_final = closing_balance_only_purchase.annotate(
            closing_balance=ExpressionWrapper(
                F('purchase_closing_balance') * F('closing_quantity'), output_field=FloatField()),
        )

        total_closing_stock = closing_balance_final.aggregate(
            the_sum=Coalesce(Sum('closing_balance'), Value(0)))['the_sum']

        # Journal queries to get the debit and credit balances of all ledgers
        Journal_debit = JournalVoucher.objects.filter(company=company, dr_ledger=OuterRef(
            'pk'), voucher_date__gte=period_selected.start_date, voucher_date__lte=period_selected.end_date).values('dr_ledger')

        Journal_credit = JournalVoucher.objects.filter(company=company, cr_ledger=OuterRef(
            'pk'), voucher_date__gte=period_selected.start_date, voucher_date__lte=period_selected.end_date).values('cr_ledger')

        Journal_debit_opening = JournalVoucher.objects.filter(company=company, dr_ledger=OuterRef(
            'pk'), voucher_date__lt=period_selected.start_date).values('dr_ledger')

        Journal_credit_opening = JournalVoucher.objects.filter(company=company, cr_ledger=OuterRef(
            'pk'), voucher_date__lt=period_selected.start_date).values('cr_ledger')

        total_debit = Journal_debit.annotate(
            total=Coalesce(Sum('amount'), Value(0))).values('total')

        total_credit = Journal_credit.annotate(
            total=Coalesce(Sum('amount'), Value(0))).values('total')

        total_debit_opening = Journal_debit_opening.annotate(
            total=Coalesce(Sum('amount'), Value(0))).values('total')

        total_credit_opening = Journal_credit_opening.annotate(
            total=Coalesce(Sum('amount'), Value(0))).values('total')

        ledgers = LedgerMaster.objects.filter(company=company).annotate(
            debit_balance_opening=Coalesce(
                Subquery(total_debit_opening, output_field=FloatField()), Value(0)),
            credit_balance_opening=Coalesce(
                Subquery(total_credit_opening, output_field=FloatField()), Value(0)),
            debit_balance=Coalesce(
                Subquery(total_debit, output_field=FloatField()), Value(0)),
            credit_balance=Coalesce(
                Subquery(total_credit, output_field=FloatField()), Value(0))
        )

        ledger_list = ledgers.annotate(
            opening_balance_generated=Case(
                When(ledger_group__group_base__is_debit='Yes', then=F(
                    'opening_balance') + F('debit_balance_opening') - F('credit_balance_opening')),
                When(ledger_group__group_base__is_debit='No', then=F(
                    'opening_balance') + F('credit_balance_opening') - F('debit_balance_opening')),
                default=None,
                output_field=FloatField()
            ),
        )

        ledger_final_list = ledger_list.annotate(
            closing_balance_generated=Case(
                When(ledger_group__group_base__is_debit='Yes', then=F(
                    'opening_balance_generated') + F('debit_balance') - F('credit_balance')),
                When(ledger_group__group_base__is_debit='No', then=F(
                    'opening_balance_generated') + F('credit_balance') - F('debit_balance')),
                default=None,
                output_field=FloatField()
            ),
        )

        total_capital = ledger_final_list.filter(ledger_group__group_base__name__contains='Capital Account').aggregate(
            the_sum=Coalesce(Sum('closing_balance_generated'), Value(0)))['the_sum']
        context['capital_ac_total'] = round(total_capital, 2)

        total_sundry_debtor = ledger_final_list.filter(ledger_group__group_base__name__contains='Sundry Debtors').aggregate(
            the_sum=Coalesce(Sum('closing_balance_generated'), Value(0)))['the_sum']
        context['total_dues_to_collect'] = round(total_sundry_debtor, 2)

        total_sundry_creditor = ledger_final_list.filter(ledger_group__group_base__name__contains='Sundry Creditors').aggregate(
            the_sum=Coalesce(Sum('closing_balance_generated'), Value(0)))['the_sum']
        context['total_dues_to_pay'] = round(total_sundry_creditor, 2)

        total_fixed_asset = ledger_final_list.filter(ledger_group__group_base__name__contains='Fixed Assets').aggregate(
            the_sum=Coalesce(Sum('closing_balance_generated'), Value(0)))['the_sum']

        total_current_asset = ledger_final_list.filter(ledger_group__group_base__name__contains='Current Assets').aggregate(
            the_sum=Coalesce(Sum('closing_balance_generated'), Value(0)))['the_sum']

        context['total_current_asset'] = round(
            total_current_asset, 2) + round(total_closing_stock, 2)

        total_asset = round(total_fixed_asset, 2) + \
            context['total_current_asset']
        context['total_asset'] = round(total_asset, 2)

        total_current_liabilities = ledger_final_list.filter(ledger_group__group_base__name__contains='Current Liabilities').aggregate(
            the_sum=Coalesce(Sum('closing_balance_generated'), Value(0)))['the_sum']
        context['total_current_liabilities'] = round(
            total_current_liabilities, 2)

        context['working_capital'] = context['total_current_asset'] - \
            context['total_current_liabilities']

        month_diff_q = period_selected.end_date - period_selected.start_date
        month_diff = (int(month_diff_q.days/30))

        total_purchase = ledger_final_list.filter(ledger_group__group_base__name__contains='Purchase Accounts').aggregate(
            the_sum=Coalesce(Sum('closing_balance_generated'), Value(0)))['the_sum']
        total_sales = ledger_final_list.filter(ledger_group__group_base__name__contains='Sales Account').aggregate(
            the_sum=Coalesce(Sum('closing_balance_generated'), Value(0)))['the_sum']
        total_directexp = ledger_final_list.filter(ledger_group__group_base__name__contains='Direct Expenses').aggregate(
            the_sum=Coalesce(Sum('closing_balance_generated'), Value(0)))['the_sum']
        total_directinc = ledger_final_list.filter(ledger_group__group_base__name__contains='Direct Incomes').aggregate(
            the_sum=Coalesce(Sum('closing_balance_generated'), Value(0)))['the_sum']
        total_indirectexp = ledger_final_list.filter(ledger_group__group_base__name__contains='Indirect Expense').aggregate(
            the_sum=Coalesce(Sum('closing_balance_generated'), Value(0)))['the_sum']
        total_indirectinc = ledger_final_list.filter(ledger_group__group_base__name__contains='Indirect Income').aggregate(
            the_sum=Coalesce(Sum('closing_balance_generated'), Value(0)))['the_sum']

        if month_diff != 0:
            context['sales_per_month'] = round(total_sales, 2) / month_diff
        else:
            context['sales_per_month'] = 0

        if int(month_diff_q.days) != 0:
            context['sales_per_day'] = round(
                total_sales, 2) / int(month_diff_q.days)
        else:
            context['sales_per_day'] = 0

        context['sales_next_day'] = (context['sales_per_day'] * 25) / 100

        if total_closing_stock != 0:
            context['inventory_turnover'] = float(
                round(total_sales, 2)) / float(total_closing_stock)
        else:
            context['inventory_turnover'] = 0

        if total_directinc < 0 and total_directexp < 0:
            gp = abs(decimal.Decimal(total_sales)) + abs(decimal.Decimal(total_closing_stock)) + abs(decimal.Decimal(total_directexp)) - \
                abs(decimal.Decimal(opening_stock)) - abs(decimal.Decimal(total_purchase)
                                                          ) - abs(decimal.Decimal(total_directinc))
        elif total_directexp < 0:
            gp = abs(decimal.Decimal(total_sales)) + abs(decimal.Decimal(total_closing_stock)) + abs(decimal.Decimal(total_directinc)) + \
                abs(decimal.Decimal(total_directexp)) - \
                abs(decimal.Decimal(opening_stock)) - \
                abs(decimal.Decimal(total_purchase))
        elif total_directinc < 0:
            gp = abs(decimal.Decimal(total_sales)) + abs(decimal.Decimal(total_closing_stock)) - abs(decimal.Decimal(total_directinc)) - \
                abs(decimal.Decimal(opening_stock)) - abs(decimal.Decimal(total_purchase)
                                                          ) - abs(decimal.Decimal(total_directexp))
        else:
            gp = abs(decimal.Decimal(total_sales)) + abs(decimal.Decimal(total_closing_stock)) + abs(decimal.Decimal(total_directinc)) - \
                abs(decimal.Decimal(opening_stock)) - abs(decimal.Decimal(total_purchase)
                                                          ) - abs(decimal.Decimal(total_directexp))

        # nett profit/loss calculation

        if gp >= 0:
            if total_indirectinc < 0 and total_indirectexp < 0:
                np = (gp) + abs(decimal.Decimal(total_indirectexp)) - \
                    abs(decimal.Decimal(total_indirectinc))
            elif total_indirectexp < 0:
                np = (gp) + abs(decimal.Decimal(total_indirectinc)) + \
                    abs(decimal.Decimal(total_indirectexp))
            elif total_indirectinc < 0:
                np = (gp) - abs(decimal.Decimal(total_indirectinc)) - \
                    abs(decimal.Decimal(total_indirectexp))
            else:
                np = (gp) + abs(decimal.Decimal(total_indirectinc)) - \
                    abs(decimal.Decimal(total_indirectexp))
        else:
            if total_indirectinc < 0 and total_indirectexp < 0:
                np = abs(decimal.Decimal(total_indirectexp)) - \
                    abs(decimal.Decimal(total_indirectinc)) - abs(gp)
            elif total_indirectinc < 0:
                np = abs(decimal.Decimal(total_indirectinc)) + \
                    abs(decimal.Decimal(total_indirectexp)) + abs(gp)
            elif total_indirectexp < 0:
                np = abs(decimal.Decimal(total_indirectinc)) + \
                    abs(decimal.Decimal(total_indirectexp)) - abs(gp)
            else:
                np = abs(decimal.Decimal(total_indirectinc)) - \
                    abs(decimal.Decimal(total_indirectexp)) - abs(gp)

        if total_sales or total_sales != 0:
            context['gross_profit'] = (gp / decimal.Decimal(total_sales)) * 100
            context['nett_profit'] = (
                round(np, 2) / decimal.Decimal(total_sales)) * 100
        else:
            context['gross_profit'] = 0
            context['nett_profit'] = 0

        context['nett_profit_total'] = round(np, 2)

        context['cost_goods_sold'] = decimal.Decimal(opening_stock) + decimal.Decimal(total_purchase) + decimal.Decimal(
            total_directexp) - decimal.Decimal(total_closing_stock) - decimal.Decimal(total_directinc)

        context['operating_cost'] = round(
            context['cost_goods_sold'], 2) + decimal.Decimal(round(total_directexp, 2))

        investment = decimal.Decimal(
            round(context['capital_ac_total'], 2)) + decimal.Decimal(round(np, 2))

        if investment or investment != 0:
            context['roi'] = (round(np, 2) / round(investment, 2)) * 100
        else:
            context['roi'] = 0

        if context['working_capital'] or context['working_capital'] != 0:
            context['return_working_capital'] = (
                round(np, 2) / decimal.Decimal(round(context['working_capital'], 2))) * 100
        else:
            context['return_working_capital'] = 0

        # Business decision Analysis
        top_ledgers_deb = ledger_final_list.filter(
            ledger_group__group_base__name__exact='Sundry Debtors')
        context['top_ledger_sales'] = top_ledgers_deb.annotate(total=Coalesce(Sum(
            'party_ledger_sales__sub_total'), 0)).order_by('-total')[:10]  # all ledger sales total
        context['total_ledger'] = context['top_ledger_sales'].aggregate(
            partial_total=Sum('total'))['partial_total']

        top_ledgers_cre = ledger_final_list.filter(
            ledger_group__group_base__name__exact='Sundry Creditors')
        context['top_ledger_purchase'] = top_ledgers_cre.annotate(total=Coalesce(Sum(
            'party_ledger_purchase__sub_total'), 0)).order_by('-total')[:10]  # all ledger purchase total
        context['total_ledger_purchase'] = context['top_ledger_purchase'].aggregate(
            partial_total=Sum('total'))['partial_total']

        context['top_stock'] = company.company_stock_items.annotate(
            total_sales=Coalesce(Sum('sale_stock__total'), 0),
            quantity_sales=Coalesce(Sum('sale_stock__quantity'), 0),
            total_puchase=Coalesce(Sum('purchase_stock__total'), 0),
            quantity_purchase=Coalesce(Sum('purchase_stock__quantity'), 0)).order_by('-total_sales')[:10]
        # all stock sales and purchase total and Quantity
        context['top_stock_total'] = context['top_stock'].aggregate(
            partial_total=Sum('total_sales'))['partial_total']

        context['stock_margin'] = context['top_stock'].annotate(
            Avg_purchase=Case(
                When(quantity_purchase__gt=0, then=F(
                    'total_puchase') / F('quantity_purchase')),
                default=None,
                output_field=FloatField()
            ),
            Avg_sales=Case(
                When(quantity_sales__gt=0, then=F(
                    'total_sales') / F('quantity_sales')),
                default=None,
                output_field=FloatField()
            )
        )

        return context


def validate_gst_billing(request):

    data = {
        'is_enable': Company.objects.filter(gst_enabled='No', gst_registration_type=True).exists()
    }
    if data['is_enable']:
        data['error_message'] = 'To enable composite billing GST should be enabled'
    return JsonResponse(data)


class CompanyCreateView(CreateView, ProductExistsRequiredMixin, LoginRequiredMixin):
    """
    Company Create View
    """
    form_class = CompanyForm
    template_name = 'company/company_form.html'

    def get_success_url(self, **kwargs):
        organisation = get_object_or_404(
            Organisation, pk=self.kwargs['organisation_pk'])
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        company = Company.objects.filter(
            organisation=organisation)
        for company_obj in company:
            return reverse('company:Dashboard', kwargs={'company_pk': company_obj.pk, 'period_selected_pk': period_selected.pk})

    def form_valid(self, form):
        form.instance.user = self.request.user
        organisation = Organisation.objects.get(
            pk=self.kwargs['organisation_pk'])
        form.instance.organisation = organisation
        counter = Organisation.objects.filter(
            user=self.request.user).count() + 1
        form.instance.counter = counter
        return super(CompanyCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(CompanyCreateView, self).get_context_data(**kwargs)
        organisation = get_object_or_404(
            Organisation, pk=self.kwargs['organisation_pk'])
        context['organisation'] = organisation
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        context['products_aggrement'] = ProductActivated.objects.filter(
            user=self.request.user, product__id=9, is_active=True)
        context['active_product_1'] = ProductActivated.objects.filter(
            user=self.request.user, product__id=1, is_active=True)
        context['role_product_1'] = RoleBasedProductActivated.objects.filter(
            user=self.request.user, product__id=1, is_active=True)
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['legal_product'] = ProductActivated.objects.filter(
            user=self.request.user, product__id=10, is_active=True)
        return context


class CompanyUpdateView(NormalProductExistsRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Company
    form_class = CompanyForm
    template_name = "company/company_form.html"

    def get_object(self):
        return get_object_or_404(Company, pk=self.kwargs['company_pk'])

    def get_success_url(self, **kwargs):
        period_selected = get_object_or_404(
            PeriodSelected, user=self.request.user)
        company = self.get_object()
        return reverse('company:Dashboard', kwargs={'company_pk': company.pk, 'period_selected_pk': period_selected.pk})

    def get_context_data(self, **kwargs):
        context = super(CompanyUpdateView, self).get_context_data(**kwargs)

        context['products_aggrement'] = ProductActivated.objects.filter(
            user=self.request.user, product__id=9, is_active=True)
        context['active_product_1'] = ProductActivated.objects.filter(
            user=self.request.user, product__id=1, is_active=True)
        context['role_product_1'] = RoleBasedProductActivated.objects.filter(
            user=self.request.user, product__id=1, is_active=True)
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['legal_product'] = ProductActivated.objects.filter(
            user=self.request.user, product__id=10, is_active=True)
        return context


def save_all(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            company_list = Company.objects.all().order_by('-id')
            data['companies'] = render_to_string(
                'company/companies.html', {'company_list': company_list})
        else:
            data['form_is_valid'] = False
    context = {
        'form': form
    }
    data['html_form'] = render_to_string(
        template_name, context, request=request)
    return JsonResponse(data)


@login_required
@product_1_activation
def organisation_delete_ajax(request, organisation_pk):
    data = {'is_error': False, 'error_message': ""}

    # data['is_error'] = True
    # data['error_message'] = "Not allowed!"
    # return JsonResponse(data)

    organisation = Organisation.objects.filter(pk=organisation_pk).first()
    if not organisation:
        data['is_error'] = True
        data['error_message'] = "No Company found with the ID supplied"
        return JsonResponse(data)

    if request.method == "POST":
        try:
            organisation.delete()
        except IntegrityError:
            data['is_error'] = True
            data['error_message'] = "Cannot delete the company it has reference!"
            return JsonResponse(data)

        period_selected = PeriodSelected.objects.filter(
            user=request.user).first()
        if not period_selected:
            data['is_error'] = True
            data['error_message'] = "Period selection information unavailable; please refresh page"
            return JsonResponse(data)

        context = {
            'organisation_list': Organisation.objects.filter(user=request.user).order_by('name'),
            'period_selected': period_selected,
            'Products': ProductActivated.objects.filter(user=request.user, product__id=1, is_active=True),
            'Products_QR': ProductActivated.objects.filter(user=request.user, product__id=3, is_active=True),
        }
        data['organisation_list'] = render_to_string(
            'organisation/organisation_list_2.html', context)
    else:
        context = {'organisation': organisation}
        data['html_form'] = render_to_string(
            'organisation/organisation_confirm_delete.html', context, request=request)

    return JsonResponse(data)


@login_required
@product_1_activation
def specific_company_details(request, company_pk):
    company = get_object_or_404(Company, pk=company_pk)

    if not request.user.is_authenticated:
        products_aggrement = ProductActivated.objects.filter(
            user=request.user, product__id=9, is_active=True)
        product = ProductActivated.objects.filter(
            product__id=1, is_active=True)
        role_product = RoleBasedProductActivated.objects.filter(
            product__id=1, is_active=True)
        inbox = Message.objects.all()
        inbox_count = inbox.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.all().aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        legal_product = ProductActivated.objects.filter(
            product__id=10, is_active=True)
    else:
        products_aggrement = ProductActivated.objects.filter(
            product__id=9, is_active=True)
        product = ProductActivated.objects.filter(
            user=request.user, product__id=1, is_active=True)
        role_product = RoleBasedProductActivated.objects.filter(
            user=request.user, product__id=1, is_active=True)
        inbox = Message.objects.filter(reciever=request.user)
        inbox_count = inbox.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.filter(sender=request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        legal_product = ProductActivated.objects.filter(
            user=request.user, product__id=10, is_active=True)

    context = {
        'company': company,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
        'product': product,
        'role_product': role_product,
        'products_aggrement': products_aggrement,
        'legal_product': legal_product

    }
    return render(request, 'Company/company_details.html', context)


######################################## Auditor Views #############################################

@login_required
@product_1_activation
def auditor_list(request, company_pk):
    company = get_object_or_404(Company, pk=company_pk)

    if not request.user.is_authenticated:
        products_aggrement = ProductActivated.objects.filter(
            user=request.user, product__id=9, is_active=True)
        product = ProductActivated.objects.filter(
            product__id=1, is_active=True)
        role_product = RoleBasedProductActivated.objects.filter(
            product__id=1, is_active=True)
        inbox = Message.objects.all()
        inbox_count = inbox.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.all().aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        legal_product = ProductActivated.objects.filter(
            product__id=10, is_active=True)
    else:
        products_aggrement = ProductActivated.objects.filter(
            product__id=9, is_active=True)
        product = ProductActivated.objects.filter(
            user=request.user, product__id=1, is_active=True)
        role_product = RoleBasedProductActivated.objects.filter(
            user=request.user, product__id=1, is_active=True)
        inbox = Message.objects.filter(reciever=request.user)
        inbox_count = inbox.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.filter(sender=request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        legal_product = ProductActivated.objects.filter(
            user=request.user, product__id=10, is_active=True)

    context = {
        'company': company,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
        'product': product,
        'role_product': role_product,
        'products_aggrement': products_aggrement,
        'legal_product': legal_product

    }
    return render(request, 'auditor/auditor_list.html', context)


@login_required
@product_1_activation
def search_auditors(request, company_pk):
    """
    Search Auditors
    """
    company = get_object_or_404(Company, pk=company_pk)

    template = 'auditor/search_auditor.html'

    user_profile = Profile.objects.filter(user_type__icontains='Professional')

    query = request.GET.get('q')

    if query:
        result = user_profile.filter(Q(user__username__icontains=query) | Q(
            email__icontains=query) | Q(full_name__icontains=query)).exclude(name=request.user)
    else:
        result = Profile.objects.none()

    professional_count = result.count()

    page = request.GET.get('page', 1)
    paginator = Paginator(result, 9)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)

    if not request.user.is_authenticated:
        products_aggrement = ProductActivated.objects.filter(
            user=request.user, product__id=9, is_active=True)
        product = ProductActivated.objects.filter(
            product__id=1, is_active=True)
        role_product = RoleBasedProductActivated.objects.filter(
            product__id=1, is_active=True)
        inbox = Message.objects.all()
        inbox_count = inbox.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.all().aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        legal_product = ProductActivated.objects.filter(
            product__id=10, is_active=True)
    else:
        products_aggrement = ProductActivated.objects.filter(
            product__id=9, is_active=True)
        product = ProductActivated.objects.filter(
            user=request.user, product__id=1, is_active=True)
        role_product = RoleBasedProductActivated.objects.filter(
            user=request.user, product__id=1, is_active=True)
        inbox = Message.objects.filter(reciever=request.user)
        inbox_count = inbox.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.filter(sender=request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        legal_product = ProductActivated.objects.filter(
            user=request.user, product__id=10, is_active=True)

    context = {
        'professionals': result,
        'users': users,
        'professional_count': professional_count,
        'product': product,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
        'company': company,
        'role_product': role_product,
        'products_aggrement': products_aggrement,
        'legal_product': legal_product

    }

    return render(request, template, context)


@login_required
@product_1_activation
def add_auditor(request, company_pk, profile_pk):
    """
    Add Autidor
    """
    role_products = get_object_or_404(RoleBasedProduct, pk=1)
    company = get_object_or_404(Company, pk=company_pk)
    user_profile = get_object_or_404(Profile, pk=profile_pk)

    company.auditor.add(user_profile.name)
    company.save()
    user_profile.subscribed_role_products.add(role_products)
    user_profile.save()

    return redirect(reverse('Company:search_auditors', kwargs={"company_pk": company.pk}))


@login_required
@product_1_activation
def delete_auditors(request, company_pk, profile_pk):
    """
    Delete Autidor
    """
    company = get_object_or_404(Company, pk=company_pk)
    user_profile = get_object_or_404(Profile, pk=profile_pk)

    company.auditor.remove(user_profile.name)

    return redirect(reverse('Company:auditor_list', kwargs={"company_pk": company.pk}))

######################################## Accountant Views #############################################


@login_required
@product_1_activation
def accountant_list(request, company_pk):
    company = get_object_or_404(Company, pk=company_pk)

    if not request.user.is_authenticated:
        products_aggrement = ProductActivated.objects.filter(
            user=request.user, product__id=9, is_active=True)
        product = ProductActivated.objects.filter(
            product__id=1, is_active=True)
        role_product = RoleBasedProductActivated.objects.filter(
            product__id=1, is_active=True)
        inbox = Message.objects.all()
        inbox_count = inbox.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.all().aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        legal_product = ProductActivated.objects.filter(
            product__id=10, is_active=True)
    else:
        products_aggrement = ProductActivated.objects.filter(
            product__id=9, is_active=True)
        product = ProductActivated.objects.filter(
            user=request.user, product__id=1, is_active=True)
        role_product = RoleBasedProductActivated.objects.filter(
            user=request.user, product__id=1, is_active=True)
        inbox = Message.objects.filter(reciever=request.user)
        inbox_count = inbox.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.filter(sender=request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        legal_product = ProductActivated.objects.filter(
            user=request.user, product__id=10, is_active=True)

    context = {
        'company': company,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
        'product': product,
        'role_product': role_product,
        'products_aggrement': products_aggrement,
        'legal_product': legal_product

    }
    return render(request, 'accountant/accountant_list.html', context)


@login_required
@product_1_activation
def search_accountant(request, company_pk):

    company = get_object_or_404(Company, pk=company_pk)

    template = 'accountant/search_accountant.html'

    query = request.GET.get('q')

    if query:
        result = Profile.objects.filter(Q(user__username__icontains=query) | Q(
            email__icontains=query) | Q(full_name__icontains=query)).exclude(name=request.user)
    else:
        result = Profile.objects.none()

    professional_count = result.count()

    page = request.GET.get('page', 1)
    paginator = Paginator(result, 9)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)

    if not request.user.is_authenticated:
        products_aggrement = ProductActivated.objects.filter(
            user=request.user, product__id=9, is_active=True)
        product = ProductActivated.objects.filter(
            product__id=1, is_active=True)
        role_product = RoleBasedProductActivated.objects.filter(
            product__id=1, is_active=True)
        inbox = Message.objects.all()
        inbox_count = inbox.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.all().aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        legal_product = ProductActivated.objects.filter(
            product__id=10, is_active=True)
    else:
        products_aggrement = ProductActivated.objects.filter(
            product__id=9, is_active=True)
        product = ProductActivated.objects.filter(
            user=request.user, product__id=1, is_active=True)
        role_product = RoleBasedProductActivated.objects.filter(
            user=request.user, product__id=1, is_active=True)
        inbox = Message.objects.filter(reciever=request.user)
        inbox_count = inbox.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.filter(sender=request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        legal_product = ProductActivated.objects.filter(
            user=request.user, product__id=10, is_active=True)

    context = {
        'professionals': result,
        'users': users,
        'professional_count': professional_count,
        'product': product,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
        'company': company,
        'role_product': role_product,
        'products_aggrement': products_aggrement,
        'legal_product': legal_product
    }

    return render(request, template, context)


@login_required
@product_1_activation
def add_accountant(request, company_pk, profile_pk):
    role_products = get_object_or_404(RoleBasedProduct, pk=1)
    company = get_object_or_404(Company, pk=company_pk)
    user_profile = get_object_or_404(Profile, pk=profile_pk)

    company.accountant.add(user_profile.name)
    company.save()
    user_profile.subscribed_role_products.add(role_products)
    user_profile.save()

    return redirect(reverse('Company:search_accountant', kwargs={"company_pk": company.pk}))


@login_required
@product_1_activation
def delete_accountant(request, company_pk, profile_pk):
    company = get_object_or_404(Company, pk=company_pk)
    user_profile = get_object_or_404(Profile, pk=profile_pk)

    company.accountant.remove(user_profile.name)

    return redirect(reverse('Company:accountant_list', kwargs={"company_pk": company.pk}))

######################################## PurchaseVoucher Personnel Views #############################################


@login_required
@product_1_activation
def purchase_personel_list(request, company_pk):
    company = get_object_or_404(Company, pk=company_pk)

    if not request.user.is_authenticated:
        products_aggrement = ProductActivated.objects.filter(
            user=request.user, product__id=9, is_active=True)
        product = ProductActivated.objects.filter(
            product__id=1, is_active=True)
        role_product = RoleBasedProductActivated.objects.filter(
            product__id=1, is_active=True)
        inbox = Message.objects.all()
        inbox_count = inbox.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.all().aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        legal_product = ProductActivated.objects.filter(
            product__id=10, is_active=True)
    else:
        products_aggrement = ProductActivated.objects.filter(
            product__id=9, is_active=True)
        product = ProductActivated.objects.filter(
            user=request.user, product__id=1, is_active=True)
        role_product = RoleBasedProductActivated.objects.filter(
            user=request.user, product__id=1, is_active=True)
        inbox = Message.objects.filter(reciever=request.user)
        inbox_count = inbox.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.filter(sender=request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        legal_product = ProductActivated.objects.filter(
            user=request.user, product__id=10, is_active=True)

    context = {
        'company': company,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
        'product': product,
        'role_product': role_product,
        'products_aggrement': products_aggrement,
        'legal_product': legal_product
    }

    return render(request, 'purchase_personel/purchase_personnel_list.html', context)


@login_required
@product_1_activation
def search_purchase_personel(request, company_pk):
    company = get_object_or_404(Company, pk=company_pk)

    template = 'purchase_personel/search_purchase_personnel.html'

    query = request.GET.get('q')

    if query:
        result = Profile.objects.filter(Q(user__username__icontains=query) | Q(
            email__icontains=query) | Q(full_name__icontains=query)).exclude(name=request.user)
    else:
        result = Profile.objects.none()

    professional_count = result.count()

    page = request.GET.get('page', 1)
    paginator = Paginator(result, 9)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)

    if not request.user.is_authenticated:
        products_aggrement = ProductActivated.objects.filter(
            user=request.user, product__id=9, is_active=True)
        product = ProductActivated.objects.filter(
            product__id=1, is_active=True)
        role_product = RoleBasedProductActivated.objects.filter(
            product__id=1, is_active=True)
        inbox = Message.objects.all()
        inbox_count = inbox.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.all().aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        legal_product = ProductActivated.objects.filter(
            product__id=10, is_active=True)
    else:
        products_aggrement = ProductActivated.objects.filter(
            product__id=9, is_active=True)
        product = ProductActivated.objects.filter(
            user=request.user, product__id=1, is_active=True)
        role_product = RoleBasedProductActivated.objects.filter(
            user=request.user, product__id=1, is_active=True)
        inbox = Message.objects.filter(reciever=request.user)
        inbox_count = inbox.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.filter(sender=request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        legal_product = ProductActivated.objects.filter(
            user=request.user, product__id=10, is_active=True)

    context = {
        'professionals': result,
        'users': users,
        'professional_count': professional_count,
        'product': product,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
        'company': company,
        'role_product': role_product,
        'products_aggrement': products_aggrement,
        'legal_product': legal_product,
    }

    return render(request, template, context)


@login_required
@product_1_activation
def add_purchase_personel(request, company_pk, profile_pk):
    role_products = get_object_or_404(RoleBasedProduct, pk=1)
    company = get_object_or_404(Company, pk=company_pk)
    user_profile = get_object_or_404(Profile, pk=profile_pk)

    company.purchase_personel.add(user_profile.name)
    company.save()
    user_profile.subscribed_role_products.add(role_products)
    user_profile.save()

    return redirect(reverse('Company:search_purchase_personel', kwargs={"company_pk": company.pk}))


@login_required
@product_1_activation
def delete_purchase_personel(request, company_pk, profile_pk):
    company = get_object_or_404(Company, pk=company_pk)
    user_profile = get_object_or_404(Profile, pk=profile_pk)

    company.purchase_personel.remove(user_profile.name)

    return redirect(reverse('Company:purchase_personel_list', kwargs={"company_pk": company.pk}))


######################################## Sales Personnel Views #############################################

@login_required
@product_1_activation
def sale_personel_list(request, company_pk):

    company = get_object_or_404(Company, pk=company_pk)

    if not request.user.is_authenticated:
        products_aggrement = ProductActivated.objects.filter(
            user=request.user, product__id=9, is_active=True)
        product = ProductActivated.objects.filter(
            product__id=1, is_active=True)
        role_product = RoleBasedProductActivated.objects.filter(
            product__id=1, is_active=True)
        inbox = Message.objects.all()
        inbox_count = inbox.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.all().aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        legal_product = ProductActivated.objects.filter(
            product__id=10, is_active=True)
    else:
        products_aggrement = ProductActivated.objects.filter(
            product__id=9, is_active=True)
        product = ProductActivated.objects.filter(
            user=request.user, product__id=1, is_active=True)
        role_product = RoleBasedProductActivated.objects.filter(
            user=request.user, product__id=1, is_active=True)
        inbox = Message.objects.filter(reciever=request.user)
        inbox_count = inbox.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.filter(sender=request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        legal_product = ProductActivated.objects.filter(
            user=request.user, product__id=10, is_active=True)

    context = {
        'company': company,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
        'product': product,
        'role_product': role_product,
        'products_aggrement': products_aggrement,
        'legal_product': legal_product,

    }
    return render(request, 'sales_personnel/sales_personnel_list.html', context)


@login_required
@product_1_activation
def search_sale_personel(request, pk):
    company = get_object_or_404(Company, pk=company_pk)
    template = 'sales_personnel/search_sales_personnel.html'

    query = request.GET.get('q')

    if query:
        result = Profile.objects.filter(Q(user__username__icontains=query) | Q(
            email__icontains=query) | Q(full_name__icontains=query)).exclude(name=request.user)
    else:
        result = Profile.objects.none()

    professional_count = result.count()

    page = request.GET.get('page', 1)
    paginator = Paginator(result, 9)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)

    if not request.user.is_authenticated:
        products_aggrement = ProductActivated.objects.filter(
            user=request.user, product__id=9, is_active=True)
        product = ProductActivated.objects.filter(
            product__id=1, is_active=True)
        role_product = RoleBasedProductActivated.objects.filter(
            product__id=1, is_active=True)
        inbox = Message.objects.all()
        inbox_count = inbox.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.all().aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        legal_product = ProductActivated.objects.filter(
            product__id=10, is_active=True)
    else:
        products_aggrement = ProductActivated.objects.filter(
            product__id=9, is_active=True)
        product = ProductActivated.objects.filter(
            user=request.user, product__id=1, is_active=True)
        role_product = RoleBasedProductActivated.objects.filter(
            user=request.user, product__id=1, is_active=True)
        inbox = Message.objects.filter(reciever=request.user)
        inbox_count = inbox.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.filter(sender=request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        legal_product = ProductActivated.objects.filter(
            user=request.user, product__id=10, is_active=True)

    context = {
        'professionals': result,
        'users': users,
        'professional_count': professional_count,
        'product': product,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
        'company': company,
        'role_product': role_product,
        'products_aggrement': products_aggrement,
        'legal_product': legal_product,
    }

    return render(request, template, context)


@login_required
@product_1_activation
def add_sale_personel(request, company_pk, profile_pk):
    role_products = get_object_or_404(RoleBasedProduct, pk=1)
    company = get_object_or_404(Company, pk=company_pk)
    user_profile = get_object_or_404(Profile, pk=profile_pk)

    company.sale_personel.add(user_profile.name)
    company.save()
    user_profile.subscribed_role_products.add(role_products)
    user_profile.save()

    return redirect(reverse('Company:search_sale_personel', kwargs={"company_pk": company.pk}))


@login_required
@product_1_activation
def delete_sale_personel(request, company_pk, profile_pk):
    company = get_object_or_404(Company, pk=company_pk)
    user_profile = get_object_or_404(Profile, pk=profile_pk)

    company.sale_personel.remove(user_profile.name)

    return redirect(reverse('Company:sale_personel_list', kwargs={"company_pk": company.pk}))


######################################## Cash/Bank Personnel Views #############################################

@login_required
@product_1_activation
def cb_personal_list(request, pk):
    company = get_object_or_404(Company, pk=company_pk)

    if not request.user.is_authenticated:
        products_aggrement = ProductActivated.objects.filter(
            user=request.user, product__id=9, is_active=True)
        product = ProductActivated.objects.filter(
            product__id=1, is_active=True)
        role_product = RoleBasedProductActivated.objects.filter(
            product__id=1, is_active=True)
        inbox = Message.objects.all()
        inbox_count = inbox.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.all().aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        legal_product = ProductActivated.objects.filter(
            product__id=10, is_active=True)
    else:
        products_aggrement = ProductActivated.objects.filter(
            product__id=9, is_active=True)
        product = ProductActivated.objects.filter(
            user=request.user, product__id=1, is_active=True)
        role_product = RoleBasedProductActivated.objects.filter(
            user=request.user, product__id=1, is_active=True)
        inbox = Message.objects.filter(reciever=request.user)
        inbox_count = inbox.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.filter(sender=request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        legal_product = ProductActivated.objects.filter(
            user=request.user, product__id=10, is_active=True)

    context = {
        'company': company,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
        'product': product,
        'role_product': role_product,
        'products_aggrement': products_aggrement,
        'legal_product': legal_product

    }
    return render(request, 'cb_personnal/cb_personnal_list.html', context)


@login_required
@product_1_activation
def search_cb_personal(request, pk):
    company = get_object_or_404(Company, pk=company_pk)
    template = 'cb_personnal/search_cb_personnal.html'

    query = request.GET.get('q')

    if query:
        result = Profile.objects.filter(Q(user__username__icontains=query) | Q(
            email__icontains=query) | Q(full_name__icontains=query)).exclude(name=request.user)
    else:
        result = Profile.objects.none()

    professional_count = result.count()

    page = request.GET.get('page', 1)
    paginator = Paginator(result, 9)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)

    if not request.user.is_authenticated:
        products_aggrement = ProductActivated.objects.filter(
            user=request.user, product__id=9, is_active=True)
        product = ProductActivated.objects.filter(
            product__id=1, is_active=True)
        role_product = RoleBasedProductActivated.objects.filter(
            product__id=1, is_active=True)
        inbox = Message.objects.all()
        inbox_count = inbox.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.all().aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        legal_product = ProductActivated.objects.filter(
            product__id=10, is_active=True)
    else:
        products_aggrement = ProductActivated.objects.filter(
            product__id=9, is_active=True)
        product = ProductActivated.objects.filter(
            user=request.user, product__id=1, is_active=True)
        role_product = RoleBasedProductActivated.objects.filter(
            user=request.user, product__id=1, is_active=True)
        inbox = Message.objects.filter(reciever=request.user)
        inbox_count = inbox.aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        send_count = Message.objects.filter(sender=request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        legal_product = ProductActivated.objects.filter(
            user=request.user, product__id=10, is_active=True)

    context = {
        'professionals': result,
        'users': users,
        'professional_count': professional_count,
        'product': product,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
        'company': company,
        'role_product': role_product,
        'products_aggrement': products_aggrement,
        'legal_product': legal_product

    }

    return render(request, template, context)


@login_required
@product_1_activation
def add_cb_personal(request, company_pk, profile_pk):
    role_products = get_object_or_404(RoleBasedProduct, pk=1)
    company = get_object_or_404(Company, pk=company_pk)
    user_profile = get_object_or_404(Profile, pk=profile_pk)

    company.cb_personal.add(user_profile.name)
    company.save()
    user_profile.subscribed_role_products.add(role_products)
    user_profile.save()

    return redirect(reverse('Company:search_cb_personal', kwargs={"company_pk": company.pk}))


@login_required
@product_1_activation
def delete_cb_personal(request, company_pk, profile_pk):
    company = get_object_or_404(Company, pk=company_pk)
    user_profile = get_object_or_404(Profile, pk=profile_pk)

    company.cb_personal.remove(user_profile.name)

    return redirect(reverse('Company:cb_personal_list', kwargs={"company_pk": company.pk}))


##########################################     Static Page View     ########################################

def static_page(request, organisation_pk, period_selected_pk):
    '''
    static page demo view
    '''

    organisation = get_object_or_404(Organisation, pk=organisation_pk)
    context = {
        'organisation': organisation
    }

    return render(request, 'static_page/staticpage_demo.html', context)


class StaticPageCreateView(CreateView):
    form_class = StaticPageForm
    template_name = "static_page/static_page_form.html"

    def get_success_url(self, **kwargs):
        organisation = get_object_or_404(
            Organisation, pk=self.kwargs['organisation_pk'])
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        return reverse('company:live-page', kwargs={'organisation_pk': organisation.pk, 'period_selected_pk': period_selected.pk})

    def form_valid(self, form):

        o = Organisation.objects.get(pk=self.kwargs['organisation_pk'])
        form.instance.organisation = o
        context = self.get_context_data()
        services_form = context['services']
        with transaction.atomic():
            self.object = form.save()
            if services_form.is_valid():
                services_form.instance = self.object
                services_form.save()
        portfolios_form = context['portfolios']
        with transaction.atomic():
            self.object = form.save()
            if portfolios_form.is_valid():
                portfolios_form.instance = self.object
                portfolios_form.save()
        team_form = context['teams']
        with transaction.atomic():
            self.object = form.save()
            if team_form.is_valid():
                team_form.instance = self.object
                team_form.save()
        return super(StaticPageCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(StaticPageCreateView, self).get_context_data(**kwargs)
        organisation = get_object_or_404(
            Organisation, pk=self.kwargs['organisation_pk'])
        context['organisation'] = organisation
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        if self.request.POST:
            context['services'] = ServiceForm_formset(self.request.POST)
            context['portfolios'] = PortfolioForm_formset(
                self.request.POST, self.request.FILES)
            context['teams'] = TeamForm_formset(
                self.request.POST, self.request.FILES)
        else:
            context['services'] = ServiceForm_formset()
            context['portfolios'] = PortfolioForm_formset()
            context['teams'] = TeamForm_formset()

        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        return context


@login_required
def live_page(request, organisation_pk, period_selected_pk):
    '''
    static page demo view
    '''

    organisation = get_object_or_404(Organisation, pk=organisation_pk)
    static_page_details = get_object_or_404(
        StaticPage, organisation=organisation)
    service_details = Service.objects.filter(staticpage=static_page_details.pk)
    portfolio_details = Portfolio.objects.filter(
        staticpage=static_page_details.pk)
    team_details = TeamMember.objects.filter(staticpage=static_page_details.pk)

    context = {
        'organisation': organisation,
        'static_page_details': static_page_details,
        'service_details': service_details,
        'portfolio_details': portfolio_details,
        'team_details': team_details


    }

    return render(request, 'static_page/static_page.html', context)


class StaticPageUpdateView(UpdateView):
    model = StaticPage
    form_class = StaticPageForm
    template_name = "static_page/static_page_form.html"

    def get_object(self):
        pk = self.kwargs['organisation_pk']
        organisation = get_object_or_404(Organisation, pk=pk)
        static_page_return = get_object_or_404(
            StaticPage, organisation=organisation)
        return static_page_return

    def get_success_url(self, **kwargs):
        organisation = get_object_or_404(
            Organisation, pk=self.kwargs['organisation_pk'])
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])
        return reverse('company:live-page', kwargs={'organisation_pk': organisation.pk, 'period_selected_pk': period_selected.pk})

    def get_context_data(self, **kwargs):
        context = super(StaticPageUpdateView, self).get_context_data(**kwargs)
        organisation = get_object_or_404(
            Organisation, pk=self.kwargs['organisation_pk'])
        context['organisation'] = organisation
        period_selected = get_object_or_404(
            PeriodSelected, pk=self.kwargs['period_selected_pk'])

        context['period_selected'] = period_selected
        static_page_details = get_object_or_404(StaticPage, pk=organisation.pk)
        static_page = StaticPage.objects.get(pk=static_page_details.pk)
        if self.request.POST or self.request.FILES:
            context['services'] = ServiceForm_formset(
                self.request.POST, instance=static_page)
            context['portfolios'] = PortfolioForm_formset(
                self.request.POST, self.request.FILES, instance=static_page)
            context['teams'] = TeamForm_formset(
                self.request.POST, self.request.FILES, instance=static_page)
        else:
            context['services'] = ServiceForm_formset(instance=static_page)
            context['portfolios'] = PortfolioForm_formset(instance=static_page)
            context['teams'] = TeamForm_formset(instance=static_page)

        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(
            the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        return context

    def form_valid(self, form):

        form.instance.User = self.request.user
        o = Organisation.objects.get(pk=self.kwargs['organisation_pk'])
        form.instance.organisation = o
        context = self.get_context_data()
        services_form = context['services']
        services_form.save()

        portfolios_form = context['portfolios']
        portfolios_form.save()

        team_form = context['teams']
        team_form.save()

        return super(StaticPageUpdateView, self).form_valid(form)
