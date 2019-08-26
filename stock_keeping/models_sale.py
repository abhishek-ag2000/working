"""
Models
"""
import datetime
from django.conf import settings
from django.db.models import Value, Sum
from django.db.models.functions import Coalesce
from django.core.exceptions import ValidationError
from django.db import models
from bracketline.models import StateMaster, CountryMaster
from company.models import Company
from accounting_entry.models import LedgerMaster
from .models import StockItem


class SaleVoucher(models.Model):
    """
    Sale Voucher Model
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, blank=True, null=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='company_sales', blank=True, null=True)
    counter = models.IntegerField()
    url_hash = models.CharField(max_length=100)
    ref_no = models.CharField(max_length=100)
    party_ac = models.ForeignKey(
        LedgerMaster, on_delete=models.DO_NOTHING, related_name='party_ledger_sales')
    doc_ledger = models.ForeignKey(
        LedgerMaster, on_delete=models.DO_NOTHING, related_name='sale_ledger',blank=True,null=True)
    consignee_name = models.CharField(
        max_length=200, default='Customer', blank=True)
    consignee_address = models.TextField(blank=True)
    consignee_gstin = models.CharField(max_length=15, blank=True)
    consignee_pan = models.CharField(max_length=15, blank=True)
    consignee_contact = models.CharField(max_length=15, blank=True)
    voucher_date = models.DateField(default=datetime.date.today)
    supply_place = models.ForeignKey(
        StateMaster, related_name="sales_supply_state", on_delete=models.DO_NOTHING, blank=True, null=True)
    consignee_state = models.ForeignKey(
        StateMaster, related_name="sales_consignee_state", on_delete=models.DO_NOTHING, blank=True, null=True)
    consignee_country = models.ForeignKey(
        CountryMaster, default=12, related_name="sales_consignee_country", on_delete=models.DO_NOTHING, blank=True)
    other_details = models.CharField(max_length=20, null=True, blank=True)

    transaction_types_sales = (
        ('Not Applicable', 'Not Applicable'),
        ('Branch Transfer outward', 'Branch Transfer outward'),
        ('Deemed Exports Exempt', 'Deemed Exports Exempt'),
        ('Deemed Exports Nil Rated', 'Deemed Exports Nil Rated'),
        ('Deemed Exports Taxable', 'Deemed Exports Taxable'),
        ('Exports Exempt', 'Exports Exempt'),
        ('Exports LUT/Bond', 'Exports LUT/Bond'),
        ('Exports Nil Rated', 'Exports Nil Rated'),
        ('Exports Taxable', 'Exports Taxable'),
        ('Interstate Sales Exempt', 'Interstate Sales Exempt'),
        ('Interstate Sales Nil Rated', 'Interstate Sales Nil Rated '),
        ('Interstate Sales - Taxable', 'Interstate Sales   - Taxable'),
        ('Interstate Sales to Embassy / UN Body Exempt',
         'Interstate Sales to Embassy / UN Body Exempt'),
        ('Interstate Sales to Embassy / UN Body Nil Rated',
         'Interstate Sales to Embassy / UN Body Nil Rated'),
        ('Interstate Sales to Embassy / UN Body Taxable',
         'Interstate Sales to Embassy / UN Body Taxable'),
        ('Intrastate Deemed Exports Exempt', 'Intrastate Deemed Exports Exempt'),
        ('Intrastate Deemed Exports Nil Rated',
         'Intrastate Deemed Exports Nil Rated'),
        ('Intrastate Deemed Exports Taxable',
         'Intrastate Deemed Exports Taxable'),
        ('Sales Exempt', 'Sales Exempt'),
        ('Sales Nil Rated', 'Sales Nil Rated'),
        ('Intrastate Sales Taxable', 'Intrastate Sales Taxable'),
        ('Sales to Consumer - Exempt', 'Sales to Consumer - Exempt'),
        ('Sales to Consumer - Nil Rated', 'Sales to Consumer - Nil Rated'),
        ('Sales to Consumer - Taxable', 'Sales to Consumer - Taxable'),
        ('Sales to SEZ - Exempt', 'Sales to SEZ - Exempt'),
        ('Sales to SEZ - LUT/Bond', 'Sales to SEZ - LUT/Bond'),
        ('Sales to SEZ - Nil Rated', 'Sales to SEZ - Nil Rated'),
        ('Sales to SEZ - Taxable', 'Sales to SEZ - Taxable'),
    )
    nature_transactions_sales = models.CharField(
        max_length=100, choices=transaction_types_sales, default='Not Applicable')

    despatch_no = models.CharField(max_length=132, blank=True)
    despatch_info = models.CharField(max_length=132, blank=True)
    destination = models.CharField(max_length=132, blank=True)
    landing_bill = models.CharField(max_length=132, blank=True)
    landing_date = models.DateField(default=datetime.date.today)
    vechicle_no = models.CharField(max_length=132, blank=True)

    supplier_ref = models.CharField(max_length=32, blank=True)
    sub_total = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    cgst_total = models.DecimalField(
        default=0, max_digits=20, decimal_places=2)
    sgst_total = models.DecimalField(
        default=0, max_digits=20, decimal_places=2)
    igst_total = models.DecimalField(
        default=0, max_digits=20, decimal_places=2)
    cess_total = models.DecimalField(
        default=0, max_digits=20, decimal_places=2)
    tax_total = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    total = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    boolean_values = (
        ('Yes', 'Yes'),
        ('No', 'No'),
    )
    gst_details = models.CharField(
        max_length=5, choices=boolean_values, default='No')

    bill_no = models.CharField(max_length=10, blank=True)
    bill_date = models.DateField(
        default=datetime.date.today, blank=True, null=True)
    port_code = models.CharField(max_length=10, blank=True)
    delivery_terms = models.TextField(blank=True)

    shipper_place = models.TextField(blank=True)
    flight_no = models.CharField(max_length=20, blank=True)
    loading_port = models.CharField(max_length=50, blank=True)
    discharge_port = models.CharField(max_length=50, blank=True)
    supply_country = models.ForeignKey(
        CountryMaster, default=12, related_name="sales_supply_country", on_delete=models.DO_NOTHING, blank=True)

    def __str__(self):
        return str(self.ref_no)

    def clean(self):
        if self.nature_transactions_sales == 'Exports Exempt' and (not self.consignee_country.country_name or self.consignee_country.country_name == self.company.country.country_name):
            raise ValidationError({'consignee_country': [
                                  "Invalid Country selected for the nature of transactions provided"]})
        if self.nature_transactions_sales == 'Exports LUT/Bond' and (not self.consignee_country.country_name or self.consignee_country.country_name == self.company.country.country_name):
            raise ValidationError({'consignee_country': [
                                  "Invalid Country selected for this nature of transactions"]})
        if self.nature_transactions_sales == 'Exports Nil Rated' and (not self.consignee_country.country_name or self.consignee_country.country_name == self.company.country.country_name):
            raise ValidationError({'consignee_country': [
                                  "Invalid Country selected for this nature of transactions"]})
        if self.nature_transactions_sales == 'Exports Taxable' and (not self.consignee_country.country_name or self.consignee_country.country_name == self.company.country.country_name):
            raise ValidationError({'consignee_country': [
                                  "Invalid Country selected for this nature of transactions"]})
        # if self.nature_transactions_sales != 'Exports Taxable' and not self.supply_place:
        #     raise ValidationError({'supply_place': ["Please provide a place of supply"]})

    def save(self, **kwargs):
        tax_invoice_total = self.sale_voucher_tax.aggregate(
            the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']
        extra_total = self.sale_voucher_term.aggregate(
            the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']
        stock_total = self.sale_voucher_stock.aggregate(
            the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']
        if tax_invoice_total or extra_total or stock_total:
            self.total = tax_invoice_total + extra_total + stock_total

        if not self.url_hash:
            if self.user.profile.user_type == 'Bussiness user':
                self.url_hash = 'BU' + '-' + str(self.user.id) + '-' + 'P' + '-' + '1' + '-' + 'C' + str(
                    self.company.counter) + '-' + ('SS') + str(self.counter)
            else:
                self.url_hash = 'PU' + '-' + str(self.user.id) + '-' + 'P' + '-' + '1' + '-' + 'C' + str(
                    self.company.counter) + '-' + ('SS') + str(self.counter)
        super(SaleVoucher, self).save()


class SaleStock(models.Model):
    """
    Sale Stock Model
    """
    sale_voucher = models.ForeignKey(
        SaleVoucher, on_delete=models.CASCADE, related_name='sale_voucher_stock')
    stock_item = models.ForeignKey(
        StockItem, on_delete=models.DO_NOTHING, related_name='sale_stock')
    quantity = models.DecimalField(
        max_digits=20, decimal_places=3, default=000)
    rate = models.DecimalField(max_digits=20, decimal_places=2, default=00)
    disc = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    cgst = models.DecimalField(default=00, max_digits=10, decimal_places=2)
    # composite tax percent
    tax = models.DecimalField(default=00, max_digits=10, decimal_places=2)
    sgst = models.DecimalField(default=00, max_digits=10, decimal_places=2)
    igst = models.DecimalField(default=00, max_digits=10, decimal_places=2)
    cess = models.DecimalField(default=00, max_digits=10, decimal_places=2)
    cgst_total = models.DecimalField(
        max_digits=20, decimal_places=2, default=0)
    sgst_total = models.DecimalField(
        max_digits=20, decimal_places=2, default=0)
    igst_total = models.DecimalField(
        max_digits=20, decimal_places=2, default=0)
    cess_total = models.DecimalField(
        max_digits=20, decimal_places=2, default=0)
    tax_total = models.DecimalField(
        max_digits=20, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=20, decimal_places=2, default=00)

    def __str__(self):
        return str(self.sale_voucher)

    def save(self, **kwargs):
        """
        Save method to overide the Sub_total and the tax total of every stock in sales voucher
        """
        if self.rate != None and self.quantity != None and self.disc != None:
            self.total = self.rate * self.quantity * (1 - (self.disc/100))

        if self.stock_item:
            if self.sale_voucher.company.gst_registration_type == 'Regular':
                if self.sale_voucher.company.organisation.state == self.sale_voucher.supply_place and self.sale_voucher.nature_transactions_sales == 'Not Applicable':
                    if self.sale_voucher.doc_ledger.central_tax != 0 or self.sale_voucher.doc_ledger.state_tax != 0:
                        self.cgst = self.sale_voucher.doc_ledger.central_tax
                        self.sgst = self.sale_voucher.doc_ledger.state_tax
                        self.igst = 0

                    elif self.stock_item.central_tax != 0 or self.stock_item.state_tax != 0:
                        self.cgst = self.stock_item.central_tax
                        self.sgst = self.stock_item.state_tax
                        self.igst = 0

                    elif self.stock_item.stock_group.central_tax != 0 or self.stock_item.stock_group.state_tax != 0:
                        self.cgst = self.stock_item.stock_group.central_tax
                        self.sgst = self.stock_item.stock_group.state_tax
                        self.igst = 0

                    else:
                        self.cgst = self.sale_voucher.company.central_tax
                        self.sgst = self.sale_voucher.company.state_tax
                        self.igst = 0

                elif self.sale_voucher.company.organisation.state != self.sale_voucher.supply_place and self.sale_voucher.nature_transactions_sales == 'Not Applicable':
                    if self.sale_voucher.doc_ledger.integrated_tax != 0:
                        self.cgst = 0
                        self.sgst = 0
                        self.igst = self.sale_voucher.doc_ledger.integrated_tax

                    elif self.stock_item.integrated_tax != 0:
                        self.cgst = 0
                        self.sgst = 0
                        self.igst = self.stock_item.integrated_tax

                    elif self.stock_item.stock_group.integrated_tax != 0:
                        self.cgst = 0
                        self.sgst = 0
                        self.igst = self.stock_item.stock_group.integrated_tax

                    else:
                        self.cgst = 0
                        self.sgst = 0
                        self.igst = self.sale_voucher.company.integrated_tax

                elif self.sale_voucher.nature_transactions_sales == 'Intrastate Deemed Exports Taxable':
                    if self.sale_voucher.doc_ledger.central_tax != 0 or self.sale_voucher.doc_ledger.state_tax != 0:
                        self.cgst = self.sale_voucher.doc_ledger.central_tax
                        self.sgst = self.sale_voucher.doc_ledger.state_tax
                        self.igst = 0

                    elif self.stock_item.central_tax != 0 or self.stock_item.state_tax != 0:
                        self.cgst = self.stock_item.central_tax
                        self.sgst = self.stock_item.state_tax
                        self.igst = 0

                    elif self.stock_item.stock_group.central_tax != 0 or self.stock_item.stock_group.state_tax != 0:
                        self.cgst = self.stock_item.stock_group.central_tax
                        self.sgst = self.stock_item.stock_group.state_tax
                        self.igst = 0

                    else:
                        self.cgst = self.sale_voucher.company.central_tax
                        self.sgst = self.sale_voucher.company.state_tax
                        self.igst = 0

                elif self.sale_voucher.nature_transactions_sales == 'Intrastate Sales Taxable':
                    if self.sale_voucher.doc_ledger.central_tax != 0 or self.sale_voucher.doc_ledger.state_tax != 0:
                        self.cgst = self.sale_voucher.doc_ledger.central_tax
                        self.sgst = self.sale_voucher.doc_ledger.state_tax
                        self.igst = 0

                    elif self.stock_item.central_tax != 0 or self.stock_item.state_tax != 0:
                        self.cgst = self.stock_item.central_tax
                        self.sgst = self.stock_item.state_tax
                        self.igst = 0

                    elif self.stock_item.stock_group.central_tax != 0 or self.stock_item.stock_group.state_tax != 0:
                        self.cgst = self.stock_item.stock_group.central_tax
                        self.sgst = self.stock_item.stock_group.state_tax
                        self.igst = 0

                    else:
                        self.cgst = self.sale_voucher.company.central_tax
                        self.sgst = self.sale_voucher.company.state_tax
                        self.igst = 0

                elif self.sale_voucher.nature_transactions_sales == 'sales to Consumer - Taxable':
                    if self.sale_voucher.doc_ledger.central_tax != 0 or self.sale_voucher.doc_ledger.state_tax != 0:
                        self.cgst = self.sale_voucher.doc_ledger.central_tax
                        self.sgst = self.sale_voucher.doc_ledger.state_tax
                        self.igst = 0

                    elif self.stock_item.central_tax != 0 or self.stock_item.state_tax != 0:
                        self.cgst = self.stock_item.central_tax
                        self.sgst = self.stock_item.state_tax
                        self.igst = 0

                    elif self.stock_item.stock_group.central_tax != 0 or self.stock_item.stock_group.state_tax != 0:
                        self.cgst = self.stock_item.stock_group.central_tax
                        self.sgst = self.stock_item.stock_group.state_tax
                        self.igst = 0

                    else:
                        self.cgst = self.sale_voucher.company.central_tax
                        self.sgst = self.sale_voucher.company.state_tax
                        self.igst = 0

                elif self.sale_voucher.nature_transactions_sales == 'Deemed Exports Taxable':
                    if self.sale_voucher.doc_ledger.integrated_tax != 0:
                        self.cgst = 0
                        self.sgst = 0
                        self.igst = self.sale_voucher.doc_ledger.integrated_tax

                    elif self.stock_item.integrated_tax != 0:
                        self.cgst = 0
                        self.sgst = 0
                        self.igst = self.stock_item.integrated_tax

                    elif self.stock_item.stock_group.integrated_tax != 0:
                        self.cgst = 0
                        self.sgst = 0
                        self.igst = self.stock_item.stock_group.integrated_tax

                    else:
                        self.cgst = 0
                        self.sgst = 0
                        self.igst = self.sale_voucher.company.integrated_tax

                elif self.sale_voucher.nature_transactions_sales == 'Exports Taxable':
                    if self.sale_voucher.doc_ledger.integrated_tax != 0:
                        self.cgst = 0
                        self.sgst = 0
                        self.igst = self.sale_voucher.doc_ledger.integrated_tax

                    elif self.stock_item.integrated_tax != 0:
                        self.cgst = 0
                        self.sgst = 0
                        self.igst = self.stock_item.integrated_tax

                    elif self.stock_item.stock_group.integrated_tax != 0:
                        self.cgst = 0
                        self.sgst = 0
                        self.igst = self.stock_item.stock_group.integrated_tax

                    else:
                        self.cgst = 0
                        self.sgst = 0
                        self.igst = self.sale_voucher.company.integrated_tax

                elif self.sale_voucher.nature_transactions_sales == 'Interstate Sales - Taxable':
                    if self.sale_voucher.doc_ledger.integrated_tax != 0:
                        self.cgst = 0
                        self.sgst = 0
                        self.igst = self.sale_voucher.doc_ledger.integrated_tax

                    elif self.stock_item.integrated_tax != 0:
                        self.cgst = 0
                        self.sgst = 0
                        self.igst = self.stock_item.integrated_tax
                    elif self.stock_item.stock_group.integrated_tax != 0:
                        self.cgst = 0
                        self.sgst = 0
                        self.igst = self.stock_item.stock_group.integrated_tax
                    else:
                        self.cgst = 0
                        self.sgst = 0
                        self.igst = self.sale_voucher.company.integrated_tax
                elif self.sale_voucher.nature_transactions_sales == 'Interstate Sales to Embassy / UN Body Taxable':
                    if self.sale_voucher.doc_ledger.integrated_tax != 0:
                        self.cgst = 0
                        self.sgst = 0
                        self.igst = self.sale_voucher.doc_ledger.integrated_tax

                    elif self.stock_item.integrated_tax != 0:
                        self.cgst = 0
                        self.sgst = 0
                        self.igst = self.stock_item.integrated_tax

                    elif self.stock_item.stock_group.integrated_tax != 0:
                        self.cgst = 0
                        self.sgst = 0
                        self.igst = self.stock_item.stock_group.integrated_tax

                    else:
                        self.cgst = 0
                        self.sgst = 0
                        self.igst = self.sale_voucher.company.integrated_tax

                elif self.sale_voucher.nature_transactions_sales == 'Sales to SEZ - Taxable':
                    if self.sale_voucher.doc_ledger.integrated_tax != 0:
                        self.cgst = 0
                        self.sgst = 0
                        self.igst = self.sale_voucher.doc_ledger.integrated_tax

                    elif self.stock_item.integrated_tax != 0:
                        self.cgst = 0
                        self.sgst = 0
                        self.igst = self.stock_item.integrated_tax

                    elif self.stock_item.stock_group.integrated_tax != 0:
                        self.cgst = 0
                        self.sgst = 0
                        self.igst = self.stock_item.stock_group.integrated_tax

                    else:
                        self.cgst = 0
                        self.sgst = 0
                        self.igst = self.sale_voucher.company.integrated_tax

                elif self.sale_voucher.company.organisation.state == 'Andaman & Nicobar Islands' and self.sale_voucher.party_ac.state == 'Andaman & Nicobar Islands' and self.sale_voucher.nature_transactions_sales == 'Intrastate Deemed Exports Taxable':
                    if self.sale_voucher.doc_ledger.central_tax != 0 or self.sale_voucher.doc_ledger.state_tax != 0:
                        self.cgst = self.sale_voucher.doc_ledger.central_tax
                        self.sgst = self.sale_voucher.doc_ledger.state_tax
                        self.igst = 0

                    elif self.stock_item.central_tax != 0 or self.stock_item.state_tax != 0:
                        self.cgst = self.stock_item.central_tax
                        self.sgst = self.stock_item.state_tax
                        self.igst = 0

                    elif self.stock_item.stock_group.central_tax != 0 or self.stock_item.stock_group.state_tax != 0:
                        self.cgst = self.stock_item.stock_group.central_tax
                        self.sgst = self.stock_item.stock_group.state_tax
                        self.igst = 0
                        self.sgst = 0

                    else:
                        self.cgst = self.sale_voucher.company.central_tax
                        self.sgst = self.sale_voucher.company.state_tax
                        self.igst = 0
                        self.sgst = 0

                elif self.sale_voucher.company.organisation.state == 'Andaman & Nicobar Islands' and self.sale_voucher.party_ac.state == 'Andaman & Nicobar Islands' and self.sale_voucher.nature_transactions_sales == 'Intrastate Sales Taxable':
                    if self.sale_voucher.doc_ledger.central_tax != 0 or self.sale_voucher.doc_ledger.state_tax != 0:
                        self.cgst = self.sale_voucher.doc_ledger.central_tax
                        self.sgst = self.sale_voucher.doc_ledger.state_tax
                        self.igst = 0

                    elif self.stock_item.central_tax != 0 or self.stock_item.state_tax != 0:
                        self.cgst = self.stock_item.central_tax
                        self.sgst = self.stock_item.state_tax
                        self.igst = 0

                    elif self.stock_item.stock_group.central_tax != 0 or self.stock_item.stock_group.state_tax != 0:
                        self.cgst = self.stock_item.stock_group.central_tax
                        self.sgst = self.stock_item.stock_group.state_tax
                        self.igst = 0

                    else:
                        self.cgst = self.sale_voucher.company.central_tax
                        self.sgst = self.sale_voucher.company.state_tax
                        self.igst = 0

                elif self.sale_voucher.company.organisation.state == 'Andaman & Nicobar Islands' and self.sale_voucher.party_ac.state == 'Andaman & Nicobar Islands' and self.sale_voucher.nature_transactions_sales == 'sales to Consumer - Taxable':
                    if self.sale_voucher.doc_ledger.central_tax != 0 or self.sale_voucher.doc_ledger.state_tax != 0:
                        self.cgst = self.sale_voucher.doc_ledger.central_tax
                        self.sgst = self.sale_voucher.doc_ledger.state_tax
                        self.igst = 0

                    elif self.stock_item.central_tax != 0 or self.stock_item.state_tax != 0:
                        self.cgst = self.stock_item.central_tax
                        self.sgst = self.stock_item.state_tax
                        self.igst = 0

                    elif self.stock_item.stock_group.central_tax != 0 or self.stock_item.stock_group.state_tax != 0:
                        self.cgst = self.stock_item.stock_group.central_tax
                        self.sgst = self.stock_item.stock_group.state_tax
                        self.igst = 0

                    else:
                        self.cgst = self.sale_voucher.company.central_tax
                        self.sgst = self.sale_voucher.company.state_tax
                        self.igst = 0
                elif self.sale_voucher.company.organisation.state == 'Chandigarh' and self.sale_voucher.party_ac.state == 'Chandigarh' and self.sale_voucher.nature_transactions_sales == 'Intrastate Sales Taxable':
                    if self.sale_voucher.doc_ledger.central_tax != 0 or self.sale_voucher.doc_ledger.state_tax != 0:
                        self.cgst = self.sale_voucher.doc_ledger.central_tax
                        self.sgst = self.sale_voucher.doc_ledger.state_tax
                        self.igst = 0

                    elif self.stock_item.central_tax != 0 or self.stock_item.state_tax != 0:
                        self.cgst = self.stock_item.central_tax
                        self.sgst = self.stock_item.state_tax
                        self.igst = 0

                    elif self.stock_item.stock_group.central_tax != 0 or self.stock_item.stock_group.state_tax != 0:
                        self.cgst = self.stock_item.stock_group.central_tax
                        self.sgst = self.stock_item.stock_group.state_tax
                        self.igst = 0

                    else:
                        self.cgst = self.sale_voucher.company.central_tax
                        self.sgst = self.sale_voucher.company.state_tax
                        self.igst = 0
                elif self.sale_voucher.company.organisation.state == 'Chandigarh' and self.sale_voucher.party_ac.state == 'Chandigarh' and self.sale_voucher.nature_transactions_sales == 'Intrastate Deemed Exports Taxable':
                    if self.sale_voucher.doc_ledger.central_tax != 0 or self.sale_voucher.doc_ledger.state_tax != 0:
                        self.cgst = self.sale_voucher.doc_ledger.central_tax
                        self.sgst = self.sale_voucher.doc_ledger.state_tax
                        self.igst = 0

                    elif self.stock_item.central_tax != 0 or self.stock_item.state_tax != 0:
                        self.cgst = self.stock_item.central_tax
                        self.sgst = self.stock_item.state_tax
                        self.igst = 0

                    elif self.stock_item.stock_group.central_tax != 0 or self.stock_item.stock_group.state_tax != 0:
                        self.cgst = self.stock_item.stock_group.central_tax
                        self.sgst = self.stock_item.stock_group.state_tax
                        self.igst = 0

                    else:
                        self.cgst = self.sale_voucher.company.central_tax
                        self.sgst = self.sale_voucher.company.state_tax
                        self.igst = 0
                elif self.sale_voucher.company.organisation.state == 'Chandigarh' and self.sale_voucher.party_ac.state == 'Chandigarh' and self.sale_voucher.nature_transactions_sales == 'sales to Consumer - Taxable':
                    if self.sale_voucher.doc_ledger.central_tax != 0 or self.sale_voucher.doc_ledger.state_tax != 0:
                        self.cgst = self.sale_voucher.doc_ledger.central_tax
                        self.sgst = self.sale_voucher.doc_ledger.state_tax
                        self.igst = 0

                    elif self.stock_item.central_tax != 0 or self.stock_item.state_tax != 0:
                        self.cgst = self.stock_item.central_tax
                        self.sgst = self.stock_item.state_tax
                        self.igst = 0

                    elif self.stock_item.stock_group.central_tax != 0 or self.stock_item.stock_group.state_tax != 0:
                        self.cgst = self.stock_item.stock_group.central_tax
                        self.sgst = self.stock_item.stock_group.state_tax
                        self.igst = 0

                    else:
                        self.cgst = self.sale_voucher.company.central_tax
                        self.sgst = self.sale_voucher.company.state_tax
                        self.igst = 0
                elif self.sale_voucher.company.organisation.state == 'Dadra and Nagar Haveli' and self.sale_voucher.party_ac.state == 'Dadra and Nagar Haveli' and self.sale_voucher.nature_transactions_sales == 'Intrastate Deemed Exports Taxable':
                    if self.sale_voucher.doc_ledger.central_tax != 0 or self.sale_voucher.doc_ledger.state_tax != 0:
                        self.cgst = self.sale_voucher.doc_ledger.central_tax
                        self.sgst = self.sale_voucher.doc_ledger.state_tax
                        self.igst = 0

                    elif self.stock_item.central_tax != 0 or self.stock_item.state_tax != 0:
                        self.cgst = self.stock_item.central_tax
                        self.sgst = self.stock_item.state_tax
                        self.igst = 0

                    elif self.stock_item.stock_group.central_tax != 0 or self.stock_item.stock_group.state_tax != 0:
                        self.cgst = self.stock_item.stock_group.central_tax
                        self.sgst = self.stock_item.stock_group.state_tax
                        self.igst = 0

                    else:
                        self.cgst = self.sale_voucher.company.central_tax
                        self.sgst = self.sale_voucher.company.state_tax
                        self.igst = 0
                elif self.sale_voucher.company.organisation.state == 'Dadra and Nagar Haveli' and self.sale_voucher.party_ac.state == 'Dadra and Nagar Haveli' and self.sale_voucher.nature_transactions_sales == 'Intrastate Sales Taxable':
                    if self.sale_voucher.doc_ledger.central_tax != 0 or self.sale_voucher.doc_ledger.state_tax != 0:
                        self.cgst = self.sale_voucher.doc_ledger.central_tax
                        self.sgst = self.sale_voucher.doc_ledger.state_tax
                        self.igst = 0

                    elif self.stock_item.central_tax != 0 or self.stock_item.state_tax != 0:
                        self.cgst = self.stock_item.central_tax
                        self.sgst = self.stock_item.state_tax
                        self.igst = 0

                    elif self.stock_item.stock_group.central_tax != 0 or self.stock_item.stock_group.state_tax != 0:
                        self.cgst = self.stock_item.stock_group.central_tax
                        self.sgst = self.stock_item.stock_group.state_tax
                        self.igst = 0

                    else:
                        self.cgst = self.sale_voucher.company.central_tax
                        self.sgst = self.sale_voucher.company.state_tax
                        self.igst = 0
                elif self.sale_voucher.company.organisation.state == 'Dadra and Nagar Haveli' and self.sale_voucher.party_ac.state == 'Dadra and Nagar Haveli' and self.sale_voucher.nature_transactions_sales == 'sales to Consumer - Taxable':
                    if self.sale_voucher.doc_ledger.central_tax != 0 or self.sale_voucher.doc_ledger.state_tax != 0:
                        self.cgst = self.sale_voucher.doc_ledger.central_tax
                        self.sgst = self.sale_voucher.doc_ledger.state_tax
                        self.igst = 0

                    elif self.stock_item.central_tax != 0 or self.stock_item.state_tax != 0:
                        self.cgst = self.stock_item.central_tax
                        self.sgst = self.stock_item.state_tax
                        self.igst = 0

                    elif self.stock_item.stock_group.central_tax != 0 or self.stock_item.stock_group.state_tax != 0:
                        self.cgst = self.stock_item.stock_group.central_tax
                        self.sgst = self.stock_item.stock_group.state_tax
                        self.igst = 0

                    else:
                        self.cgst = self.sale_voucher.company.central_tax
                        self.sgst = self.sale_voucher.company.state_tax
                        self.igst = 0
                elif self.sale_voucher.company.organisation.state == 'Daman and Diu' and self.sale_voucher.party_ac.state == 'Daman and Diu' and self.sale_voucher.nature_transactions_sales == 'Intrastate Deemed Exports Taxable':
                    if self.sale_voucher.doc_ledger.central_tax != 0 or self.sale_voucher.doc_ledger.state_tax != 0:
                        self.cgst = self.sale_voucher.doc_ledger.central_tax
                        self.sgst = self.sale_voucher.doc_ledger.state_tax
                        self.igst = 0

                    elif self.stock_item.central_tax != 0 or self.stock_item.state_tax != 0:
                        self.cgst = self.stock_item.central_tax
                        self.sgst = self.stock_item.state_tax
                        self.igst = 0

                    elif self.stock_item.stock_group.central_tax != 0 or self.stock_item.stock_group.state_tax != 0:
                        self.cgst = self.stock_item.stock_group.central_tax
                        self.sgst = self.stock_item.stock_group.state_tax
                        self.igst = 0

                    else:
                        self.cgst = self.sale_voucher.company.central_tax
                        self.sgst = self.sale_voucher.company.state_tax
                        self.igst = 0
                elif self.sale_voucher.company.organisation.state == 'Daman and Diu' and self.sale_voucher.party_ac.state == 'Daman and Diu' and self.sale_voucher.nature_transactions_sales == 'Intrastate Sales Taxable':
                    if self.sale_voucher.doc_ledger.central_tax != 0 or self.sale_voucher.doc_ledger.state_tax != 0:
                        self.cgst = self.sale_voucher.doc_ledger.central_tax
                        self.sgst = self.sale_voucher.doc_ledger.state_tax
                        self.igst = 0

                    elif self.stock_item.central_tax != 0 or self.stock_item.state_tax != 0:
                        self.cgst = self.stock_item.central_tax
                        self.sgst = self.stock_item.state_tax
                        self.igst = 0

                    elif self.stock_item.stock_group.central_tax != 0 or self.stock_item.stock_group.state_tax != 0:
                        self.cgst = self.stock_item.stock_group.central_tax
                        self.sgst = self.stock_item.stock_group.state_tax
                        self.igst = 0

                    else:
                        self.cgst = self.sale_voucher.company.central_tax
                        self.sgst = self.sale_voucher.company.state_tax
                        self.igst = 0
                elif self.sale_voucher.company.organisation.state == 'Daman and Diu' and self.sale_voucher.party_ac.state == 'Daman and Diu' and self.sale_voucher.nature_transactions_sales == 'sales to Consumer - Taxable':
                    if self.sale_voucher.doc_ledger.central_tax != 0 or self.sale_voucher.doc_ledger.state_tax != 0:
                        self.cgst = self.sale_voucher.doc_ledger.central_tax
                        self.sgst = self.sale_voucher.doc_ledger.state_tax
                        self.igst = 0

                    elif self.stock_item.central_tax != 0 or self.stock_item.state_tax != 0:
                        self.cgst = self.stock_item.central_tax
                        self.sgst = self.stock_item.state_tax
                        self.igst = 0

                    elif self.stock_item.stock_group.central_tax != 0 or self.stock_item.stock_group.state_tax != 0:
                        self.cgst = self.stock_item.stock_group.central_tax
                        self.sgst = self.stock_item.stock_group.state_tax
                        self.igst = 0
                    else:
                        self.cgst = self.sale_voucher.company.central_tax
                        self.sgst = self.sale_voucher.company.state_tax
                        self.igst = 0
                elif self.sale_voucher.company.organisation.state == 'Lakshadweep' and self.sale_voucher.party_ac.state == 'Lakshadweep' and self.sale_voucher.nature_transactions_sales == 'Intrastate Deemed Exports Taxable':
                    if self.sale_voucher.doc_ledger.central_tax != 0 or self.sale_voucher.doc_ledger.state_tax != 0:
                        self.cgst = self.sale_voucher.doc_ledger.central_tax
                        self.sgst = self.sale_voucher.doc_ledger.state_tax
                        self.igst = 0

                    elif self.stock_item.central_tax != 0 or self.stock_item.state_tax != 0:
                        self.cgst = self.stock_item.central_tax
                        self.sgst = self.stock_item.state_tax
                        self.igst = 0

                    elif self.stock_item.stock_group.central_tax != 0 or self.stock_item.stock_group.state_tax != 0:
                        self.cgst = self.stock_item.stock_group.central_tax
                        self.sgst = self.stock_item.stock_group.state_tax
                        self.igst = 0

                    else:
                        self.cgst = self.sale_voucher.company.central_tax
                        self.sgst = self.sale_voucher.company.state_tax
                        self.igst = 0
                elif self.sale_voucher.company.organisation.state == 'Lakshadweep' and self.sale_voucher.party_ac.state == 'Lakshadweep' and self.sale_voucher.nature_transactions_sales == 'Intrastate Sales Taxable':
                    if self.sale_voucher.doc_ledger.central_tax != 0 or self.sale_voucher.doc_ledger.state_tax != 0:
                        self.cgst = self.sale_voucher.doc_ledger.central_tax
                        self.sgst = self.sale_voucher.doc_ledger.state_tax
                        self.igst = 0

                    elif self.stock_item.central_tax != 0 or self.stock_item.state_tax != 0:
                        self.cgst = self.stock_item.central_tax
                        self.sgst = self.stock_item.state_tax
                        self.igst = 0

                    elif self.stock_item.stock_group.central_tax != 0 or self.stock_item.stock_group.state_tax != 0:
                        self.cgst = self.stock_item.stock_group.central_tax
                        self.sgst = self.stock_item.stock_group.state_tax
                        self.igst = 0

                    else:
                        self.cgst = self.sale_voucher.company.central_tax
                        self.sgst = self.sale_voucher.company.state_tax
                        self.igst = 0

                elif self.sale_voucher.company.organisation.state == 'Lakshadweep' and self.sale_voucher.party_ac.state == 'Lakshadweep' and self.sale_voucher.nature_transactions_sales == 'sales to Consumer - Taxable':
                    if self.sale_voucher.doc_ledger.central_tax != 0 or self.sale_voucher.doc_ledger.state_tax != 0:
                        self.cgst = self.sale_voucher.doc_ledger.central_tax
                        self.sgst = self.sale_voucher.doc_ledger.state_tax
                        self.igst = 0

                    elif self.stock_item.central_tax != 0 or self.stock_item.state_tax != 0:
                        self.cgst = self.stock_item.central_tax
                        self.sgst = self.stock_item.state_tax
                        self.igst = 0

                    elif self.stock_item.stock_group.central_tax != 0 or self.stock_item.stock_group.state_tax != 0:
                        self.cgst = self.stock_item.stock_group.central_tax
                        self.sgst = self.stock_item.stock_group.state_tax
                        self.igst = 0

                    else:
                        self.cgst = self.sale_voucher.company.central_tax
                        self.sgst = self.sale_voucher.company.state_tax
                        self.igst = 0

                else:
                    self.cgst = 0
                    self.sgst = 0
                    self.igst = 0
            else:
                self.tax = self.stock_item.integrated_tax

            if self.sale_voucher.company.gst_registration_type == 'Regular':
                if self.sale_voucher.nature_transactions_sales == 'Intrastate Deemed Exports Taxable':
                    self.cgst_total = self.cgst * self.total / 100
                    self.sgst_total = self.sgst * self.total / 100
                    self.igst_total = 0

                elif self.sale_voucher.nature_transactions_sales == 'Intrastate Sales Taxable':
                    self.cgst_total = self.cgst * self.total / 100
                    self.sgst_total = self.sgst * self.total / 100
                    self.igst_total = 0

                elif self.sale_voucher.nature_transactions_sales == 'sales to Consumer - Taxable':
                    self.cgst_total = self.cgst * self.total / 100
                    self.sgst_total = self.sgst * self.total / 100
                    self.igst_total = 0

                elif self.sale_voucher.nature_transactions_sales == 'Deemed Exports Taxable':
                    self.cgst_total = 0
                    self.sgst_total = 0
                    self.igst_total = self.igst * self.total / 100

                elif self.sale_voucher.nature_transactions_sales == 'Exports Taxable':
                    self.cgst_total = 0
                    self.sgst_total = 0
                    self.igst_total = self.igst * self.total / 100

                elif self.sale_voucher.nature_transactions_sales == 'Interstate Sales - Taxable':
                    self.cgst_total = 0
                    self.sgst_total = 0
                    self.igst_total = self.igst * self.total / 100

                elif self.sale_voucher.nature_transactions_sales == 'Interstate Sales to Embassy / UN Body Taxable':
                    self.cgst_total = 0
                    self.sgst_total = 0
                    self.igst_total = self.igst * self.total / 100

                elif self.sale_voucher.nature_transactions_sales == 'Sales to SEZ - Taxable':
                    self.cgst_total = 0
                    self.sgst_total = 0
                    self.igst_total = self.igst * self.total / 100

                elif self.sale_voucher.company.organisation.state == 'Andaman & Nicobar Islands' and self.sale_voucher.party_ac.state == 'Andaman & Nicobar Islands' and self.sale_voucher.nature_transactions_sales == 'Intrastate Deemed Exports Taxable':
                    self.cgst_total = self.cgst * self.total / 100
                    self.sgst_total = self.sgst * self.total / 100
                    self.igst_total = 0

                elif self.sale_voucher.company.organisation.state == 'Andaman & Nicobar Islands' and self.sale_voucher.party_ac.state == 'Andaman & Nicobar Islands' and self.sale_voucher.nature_transactions_sales == 'Intrastate Sales Taxable':
                    self.cgst_total = self.cgst * self.total / 100
                    self.sgst_total = self.sgst * self.total / 100
                    self.igst_total = 0

                elif self.sale_voucher.company.organisation.state == 'Andaman & Nicobar Islands' and self.sale_voucher.party_ac.state == 'Andaman & Nicobar Islands' and self.sale_voucher.nature_transactions_sales == 'sales to Consumer - Taxable':
                    self.cgst_total = self.cgst * self.total / 100
                    self.sgst_total = self.sgst * self.total / 100
                    self.igst_total = 0

                elif self.sale_voucher.company.organisation.state == 'Chandigarh' and self.sale_voucher.party_ac.state == 'Chandigarh' and self.sale_voucher.nature_transactions_sales == 'Intrastate Deemed Exports Taxable':
                    self.cgst_total = self.cgst * self.total / 100
                    self.sgst_total = self.sgst * self.total / 100
                    self.igst_total = 0

                elif self.sale_voucher.company.organisation.state == 'Chandigarh' and self.sale_voucher.party_ac.state == 'Chandigarh' and self.sale_voucher.nature_transactions_sales == 'Intrastate Sales Taxable':
                    self.cgst_total = self.cgst * self.total / 100
                    self.sgst_total = self.sgst * self.total / 100
                    self.igst_total = 0

                elif self.sale_voucher.company.organisation.state == 'Chandigarh' and self.sale_voucher.party_ac.state == 'Chandigarh' and self.sale_voucher.nature_transactions_sales == 'sales to Consumer - Taxable':
                    self.cgst_total = self.cgst * self.total / 100
                    self.sgst_total = self.sgst * self.total / 100
                    self.igst_total = 0

                elif self.sale_voucher.company.organisation.state == 'Dadra and Nagar Haveli' and self.sale_voucher.party_ac.state == 'Dadra and Nagar Haveli' and self.sale_voucher.nature_transactions_sales == 'Intrastate Deemed Exports Taxable':
                    self.cgst_total = self.cgst * self.total / 100
                    self.sgst_total = self.sgst * self.total / 100
                    self.igst_total = 0

                elif self.sale_voucher.company.organisation.state == 'Dadra and Nagar Haveli' and self.sale_voucher.party_ac.state == 'Dadra and Nagar Haveli' and self.sale_voucher.nature_transactions_sales == 'Intrastate Sales Taxable':
                    self.cgst_total = self.cgst * self.total / 100
                    self.sgst_total = self.sgst * self.total / 100
                    self.igst_total = 0

                elif self.sale_voucher.company.organisation.state == 'Dadra and Nagar Haveli' and self.sale_voucher.party_ac.state == 'Dadra and Nagar Haveli' and self.sale_voucher.nature_transactions_sales == 'sales to Consumer - Taxable':
                    self.cgst_total = self.cgst * self.total / 100
                    self.sgst_total = self.sgst * self.total / 100
                    self.igst_total = 0

                elif self.sale_voucher.company.organisation.state == 'Daman and Diu' and self.sale_voucher.party_ac.state == 'Daman and Diu' and self.sale_voucher.nature_transactions_sales == 'Intrastate Deemed Exports Taxable':
                    self.cgst_total = self.cgst * self.total / 100
                    self.sgst_total = self.sgst * self.total / 100
                    self.igst_total = 0

                elif self.sale_voucher.company.organisation.state == 'Daman and Diu' and self.sale_voucher.party_ac.state == 'Daman and Diu' and self.sale_voucher.nature_transactions_sales == 'Intrastate Sales Taxable':
                    self.cgst_total = self.cgst * self.total / 100
                    self.sgst_total = self.sgst * self.total / 100
                    self.igst_total = 0

                elif self.sale_voucher.company.organisation.state == 'Daman and Diu' and self.sale_voucher.party_ac.state == 'Daman and Diu' and self.sale_voucher.nature_transactions_sales == 'sales to Consumer - Taxable':
                    self.cgst_total = self.cgst * self.total / 100
                    self.sgst_total = self.sgst * self.total / 100
                    self.igst_total = 0

                elif self.sale_voucher.company.organisation.state == 'Lakshadweep' and self.sale_voucher.party_ac.state == 'Lakshadweep' and self.sale_voucher.nature_transactions_sales == 'Intrastate Deemed Exports Taxable':
                    self.cgst_total = self.cgst * self.total / 100
                    self.sgst_total = self.sgst * self.total / 100
                    self.igst_total = 0

                elif self.sale_voucher.company.organisation.state == 'Lakshadweep' and self.sale_voucher.party_ac.state == 'Lakshadweep' and self.sale_voucher.nature_transactions_sales == 'Intrastate Sales Taxable':
                    self.cgst_total = self.cgst * self.total / 100
                    self.sgst_total = self.sgst * self.total / 100
                    self.igst_total = 0

                elif self.sale_voucher.company.organisation.state == 'Lakshadweep' and self.sale_voucher.party_ac.state == 'Lakshadweep' and self.sale_voucher.nature_transactions_sales == 'sales to Consumer - Taxable':
                    self.cgst_total = self.cgst * self.total / 100
                    self.sgst_total = self.sgst * self.total / 100
                    self.igst_total = 0
                else:
                    self.igst_total = self.igst * self.total / 100
            else:
                self.sgst_total = self.tax * self.total / 100
                self.tax_total = self.tax * self.total / 100
        super(SaleStock, self).save()


class SaleTerm(models.Model):
    """
    Sale Term Model
    """
    sale_voucher = models.ForeignKey(SaleVoucher, on_delete=models.CASCADE, related_name='sale_voucher_term')
    ledger = models.ForeignKey(LedgerMaster, on_delete=models.CASCADE, related_name='sale_term_ledger')
    rate = models.DecimalField(default=00, max_digits=10, decimal_places=2)
    tax = models.DecimalField(default=00, max_digits=10, decimal_places=2)
    cgst = models.DecimalField(default=00, max_digits=10, decimal_places=2)
    sgst = models.DecimalField(default=00, max_digits=10, decimal_places=2)
    igst = models.DecimalField(default=00, max_digits=10, decimal_places=2)
    cess = models.DecimalField(default=00, max_digits=10, decimal_places=2)
    cgst_total = models.DecimalField(
        max_digits=20, decimal_places=2, default=0)
    sgst_total = models.DecimalField(
        max_digits=20, decimal_places=2, default=0)
    igst_total = models.DecimalField(
        max_digits=20, decimal_places=2, default=0)
    cess_total = models.DecimalField(
        max_digits=20, decimal_places=2, default=0)
    tax_total = models.DecimalField(
        max_digits=20, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=20, decimal_places=2, default=00)

    def __str__(self):
        return str(self.ledger)

    def save(self, **kwargs):
        # if self.total == 0:
        #     if self.rate != 0:
        #         self.total = self.sale_voucher.sub_total * (self.rate / 100)

        if self.ledger:
            if self.sale_voucher.company.gst_registration_type == 'Regular':
                if self.sale_voucher.nature_transactions_sales == 'Not Applicable':
                    if self.ledger.nature_transactions_sales == 'Intrastate Deemed Exports Taxable':
                        if self.ledger.central_tax != 0 or self.ledger.state_tax != 0:
                            self.cgst = self.ledger.central_tax
                            self.sgst = self.ledger.state_tax
                            self.igst = 0

                        else:
                            self.cgst = self.sale_voucher.company.central_tax
                            self.sgst = self.sale_voucher.company.state_tax
                            self.igst = 0

                    elif self.ledger.nature_transactions_sales == 'Intrastate Sales Taxable':
                        if self.ledger.central_tax != 0 or self.ledger.state_tax != 0:
                            self.cgst = self.ledger.central_tax
                            self.sgst = self.ledger.state_tax
                            self.igst = 0

                        else:
                            self.cgst = self.sale_voucher.company.central_tax
                            self.sgst = self.sale_voucher.company.state_tax
                            self.igst = 0

                    elif self.ledger.nature_transactions_sales == 'sales to Consumer - Taxable':
                        if self.ledger.central_tax != 0 or self.ledger.state_tax != 0:
                            self.cgst = self.ledger.central_tax
                            self.sgst = self.ledger.state_tax
                            self.igst = 0
                        else:
                            self.cgst = self.sale_voucher.company.central_tax
                            self.sgst = self.sale_voucher.company.state_tax
                            self.igst = 0
                    elif self.ledger.nature_transactions_sales == 'Deemed Exports Taxable':
                        if self.ledger.integrated_tax != 0:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = self.ledger.integrated_tax
                        else:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = self.sale_voucher.company.integrated_tax
                    elif self.ledger.nature_transactions_sales == 'Exports Taxable':
                        if self.ledger.integrated_tax != 0:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = self.ledger.integrated_tax
                        else:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = self.sale_voucher.company.integrated_tax
                    elif self.ledger.nature_transactions_sales == 'Interstate Sales - Taxable':
                        if self.ledger.integrated_tax != 0:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = self.ledger.integrated_tax
                        else:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = self.sale_voucher.company.integrated_tax
                    elif self.ledger.nature_transactions_sales == 'Interstate Sales to Embassy / UN Body Taxable':
                        if self.ledger.integrated_tax != 0:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = self.ledger.integrated_tax

                        else:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = self.sale_voucher.company.integrated_tax
                    elif self.ledger.nature_transactions_sales == 'Sales to SEZ - Taxable':
                        if self.ledger.integrated_tax != 0:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = self.ledger.integrated_tax
                        else:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = self.sale_voucher.company.integrated_tax
                    else:
                        self.cgst = 0
                        self.igst = 0
                        self.sgst = 0
                        self.sgst = 0
                else:
                    if self.sale_voucher.nature_transactions_sales == 'Intrastate Deemed Exports Taxable':
                        if self.ledger.central_tax != 0 or self.ledger.state_tax != 0:
                            self.cgst = self.ledger.central_tax
                            self.sgst = self.ledger.state_tax
                            self.igst = 0

                        else:
                            self.cgst = self.sale_voucher.company.central_tax
                            self.sgst = self.sale_voucher.company.state_tax
                            self.igst = 0

                    elif self.sale_voucher.nature_transactions_sales == 'Intrastate Sales Taxable':
                        if self.ledger.central_tax != 0 or self.ledger.state_tax != 0:
                            self.cgst = self.ledger.central_tax
                            self.sgst = self.ledger.state_tax
                            self.igst = 0

                        else:
                            self.cgst = self.sale_voucher.company.central_tax
                            self.sgst = self.sale_voucher.company.state_tax
                            self.igst = 0

                    elif self.sale_voucher.nature_transactions_sales == 'sales to Consumer - Taxable':
                        if self.ledger.central_tax != 0 or self.ledger.state_tax != 0:
                            self.cgst = self.ledger.central_tax
                            self.sgst = self.ledger.state_tax
                            self.igst = 0
                        else:
                            self.cgst = self.sale_voucher.company.central_tax
                            self.sgst = self.sale_voucher.company.state_tax
                            self.igst = 0
                    elif self.sale_voucher.nature_transactions_sales == 'Deemed Exports Taxable':
                        if self.ledger.integrated_tax != 0:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = self.ledger.integrated_tax
                        else:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = self.sale_voucher.company.integrated_tax
                    elif self.sale_voucher.nature_transactions_sales == 'Exports Taxable':
                        if self.ledger.integrated_tax != 0:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = self.ledger.integrated_tax
                        else:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = self.sale_voucher.company.integrated_tax
                    elif self.sale_voucher.nature_transactions_sales == 'Interstate Sales - Taxable':
                        if self.ledger.integrated_tax != 0:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = self.ledger.integrated_tax
                        else:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = self.sale_voucher.company.integrated_tax
                    elif self.sale_voucher.nature_transactions_sales == 'Interstate Sales to Embassy / UN Body Taxable':
                        if self.ledger.integrated_tax != 0:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = self.ledger.integrated_tax

                        else:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = self.sale_voucher.company.integrated_tax
                    elif self.sale_voucher.nature_transactions_sales == 'Sales to SEZ - Taxable':
                        if self.ledger.integrated_tax != 0:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = self.ledger.integrated_tax
                        else:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = self.sale_voucher.company.integrated_tax
                    else:
                        self.cgst = 0
                        self.igst = 0
                        self.sgst = 0
                        self.sgst = 0

            else:
                self.tax = self.ledger.integrated_tax

        if self.ledger: 
            if self.sale_voucher.company.gst_registration_type == 'Regular':
                if self.sale_voucher.nature_transactions_sales == 'Not Applicable':
                    if self.ledger.nature_transactions_sales == 'Intrastate Deemed Exports Taxable':
                        self.cgst_total = self.cgst * self.total / 100
                        self.sgst_total = self.sgst * self.total / 100

                    elif self.ledger.nature_transactions_sales == 'Intrastate Sales Taxable':
                        self.cgst_total = self.cgst * self.total / 100
                        self.sgst_total = self.sgst * self.total / 100

                    elif self.ledger.nature_transactions_sales == 'sales to Consumer - Taxable':
                        self.cgst_total = self.cgst * self.total / 100
                        self.sgst_total = self.sgst * self.total / 100

                    elif self.ledger.nature_transactions_sales == 'Deemed Exports Taxable':
                        self.cgst_total = 0
                        self.sgst_total = 0
                        self.igst_total = self.igst * self.total / 100

                    elif self.ledger.nature_transactions_sales == 'Exports Taxable':
                        self.cgst_total = 0
                        self.sgst_total = 0
                        self.igst_total = self.igst * self.total / 100

                    elif self.ledger.nature_transactions_sales == 'Interstate Sales - Taxable':
                        self.cgst_total = 0
                        self.sgst_total = 0
                        self.igst_total = self.igst * self.total / 100

                    elif self.ledger.nature_transactions_sales == 'Interstate Sales to Embassy / UN Body Taxable':
                        self.cgst_total = 0
                        self.sgst_total = 0
                        self.igst_total = self.igst * self.total / 100

                    elif self.ledger.nature_transactions_sales == 'Sales to SEZ - Taxable':
                        self.cgst_total = 0
                        self.sgst_total = 0
                        self.igst_total = self.igst * self.total / 100
                    else:
                        self.igst_total = self.igst * self.total / 100
                else:
                    if self.sale_voucher.nature_transactions_sales == 'Intrastate Deemed Exports Taxable':
                        self.cgst_total = self.cgst * self.total / 100
                        self.sgst_total = self.sgst * self.total / 100

                    elif self.sale_voucher.nature_transactions_sales == 'Intrastate Sales Taxable':
                        self.cgst_total = self.cgst * self.total / 100
                        self.sgst_total = self.sgst * self.total / 100

                    elif self.sale_voucher.nature_transactions_sales == 'sales to Consumer - Taxable':
                        self.cgst_total = self.cgst * self.total / 100
                        self.sgst_total = self.sgst * self.total / 100

                    elif self.sale_voucher.nature_transactions_sales == 'Deemed Exports Taxable':
                        self.cgst_total = 0
                        self.sgst_total = 0
                        self.igst_total = self.igst * self.total / 100

                    elif self.sale_voucher.nature_transactions_sales == 'Exports Taxable':
                        self.cgst_total = 0
                        self.sgst_total = 0
                        self.igst_total = self.igst * self.total / 100

                    elif self.sale_voucher.nature_transactions_sales == 'Interstate Sales - Taxable':
                        self.cgst_total = 0
                        self.sgst_total = 0
                        self.igst_total = self.igst * self.total / 100

                    elif self.sale_voucher.nature_transactions_sales == 'Interstate Sales to Embassy / UN Body Taxable':
                        self.cgst_total = 0
                        self.sgst_total = 0
                        self.igst_total = self.igst * self.total / 100

                    elif self.sale_voucher.nature_transactions_sales == 'Sales to SEZ - Taxable':
                        self.cgst_total = 0
                        self.sgst_total = 0
                        self.igst_total = self.igst * self.total / 100
                    else:
                        self.igst_total = self.igst * self.total / 100

            else:
                self.tax_total = self.tax * self.total / 100
        super(SaleTerm, self).save()


class SaleTax(models.Model):
    """
    Sale Tax Model
    """
    sale_voucher = models.ForeignKey(
        SaleVoucher, on_delete=models.CASCADE, related_name='sale_voucher_tax')
    ledger = models.ForeignKey(
        LedgerMaster, on_delete=models.CASCADE, related_name='sale_tax_ledger')
    total = models.DecimalField(max_digits=20, decimal_places=2, default=00)

    def __str__(self):
        return str(self.ledger)

    def save(self, **kwargs):
        """
        Save method to override the total value as per the ledger Selected in a voucher
        """
        if self.ledger:
            if self.ledger.tax_type == 'Central Tax':
                self.total = self.sale_voucher.cgst_total
            elif self.ledger.tax_type == 'State Tax':
                self.total = self.sale_voucher.sgst_total
            elif self.ledger.tax_type == 'Integrated Tax':
                self.total = self.sale_voucher.igst_total
            else:
                self.total = self.sale_voucher.cess_total
        super(SaleTax, self).save()
