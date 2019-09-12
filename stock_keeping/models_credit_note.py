"""
Models
"""
import datetime
from django.conf import settings
from django.db import models
from bracketline.models import StateMaster, CountryMaster
from company.models import Company
from accounting_entry.models import LedgerMaster
from .models import StockItem
from .models_sale import SaleVoucher
from django.db.models import Value, Sum
from django.db.models.functions import Coalesce



class CreditNoteVoucher(models.Model):
    """
    Credit Note Voucher Model
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_credit_note')
    sale_voucher = models.ForeignKey(SaleVoucher, on_delete=models.DO_NOTHING, blank=True, related_name='credit_note_sale_voucher')
    counter = models.IntegerField()
    url_hash = models.CharField(max_length=100)
    voucher_date = models.DateField(default=datetime.date.today)

    bool_list = (
        ('Yes', 'Yes'),
        ('No', 'No')
    )
    manual = models.CharField(max_length=100, choices=bool_list, default='No')
    # manual entry field when ref voucher missing and manual value is Yes
    sales_invno = models.CharField(max_length=30, null=True, blank=True)
    sales_date = models.DateField(blank=True, null=True)
    sales_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    ref_no = models.CharField(max_length=100)
    party_ac = models.ForeignKey(LedgerMaster, on_delete=models.DO_NOTHING, related_name='party_ledger_credit_note')
    doc_ledger = models.ForeignKey(LedgerMaster, on_delete=models.DO_NOTHING, related_name='doc_ledger_credit_note')
    supply_place = models.ForeignKey(StateMaster, related_name="credit_note_supply_state", on_delete=models.DO_NOTHING, null=True, blank=True)

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
        ('Interstate Deemed Exports Exempt', 'Interstate Deemed Exports Exempt'),
        ('Interstate Deemed Exports Nil Rated',
         'Interstate Deemed Exports Nil Rated'),
        ('Interstate Deemed Exports Taxable',
         'Interstate Deemed Exports Taxable'),
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
    nature_transactions_sales = models.CharField(max_length=50, choices=transaction_types_sales, default='Not Applicable',blank=True)
    delivery_note = models.CharField(max_length=32, blank=True)
    supplier_ref = models.CharField(max_length=32, blank=True)
    mode = models.TextField(blank=True)
    sub_total = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    cgst_total = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    sgst_total = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    igst_total = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    cess_total = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    tax_total = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    total = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    gst_details = models.CharField(max_length=3, choices=bool_list, default='No')
    reason = (
        ('00', 'Not Applicable'),
        ('01', 'Sales Return'),
        ('02', 'Post Sales Discount'),
        ('03', 'Deficiency in services'),
        ('04', 'Correction in Invoices'),
        ('05', 'Change in POS'),
        ('06', 'Finalisation of provisional assessment'),
        ('07', 'Others'),
    )
    issue_reason = models.CharField(max_length=3, choices=reason, default='00')
    note_no = models.CharField(max_length=32, blank=True)
    date_after_no = models.DateField(default=datetime.date.today)
    bill_no = models.CharField(max_length=32, blank=True)
    bill_date = models.DateField(default=datetime.date.today,blank=True)
    port_code = models.CharField(max_length=32, blank=True)

    despatch_no = models.CharField(max_length=132, blank=True)
    despatch_info = models.CharField(max_length=132, blank=True)
    destination = models.CharField(max_length=132, blank=True)
    landing_bill = models.CharField(max_length=132, blank=True)
    landing_date = models.DateField(default=datetime.date.today)
    vechicle_no = models.CharField(max_length=132, blank=True)

    shipper_place = models.TextField(blank=True)
    flight_no = models.CharField(max_length=20, blank=True)
    loading_port = models.CharField(max_length=50, blank=True)
    discharge_port = models.CharField(max_length=50, blank=True)
    supply_country = models.ForeignKey(
        CountryMaster, default=12, related_name="credit_note_supply_country", on_delete=models.DO_NOTHING, blank=True)

    def __str__(self):
        return str(self.party_ac)

    def save(self, **kwargs):
        tax_total = self.credit_note_gst.aggregate(
        the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']
        extra_total = self.credit_note_term.aggregate(
            the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']
        stock_total = self.credit_note_voucher.aggregate(
            the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']

        if tax_total or extra_total or stock_total:
            self.total = tax_total + extra_total + stock_total
            self.sub_total = total

        total_cgst_stock = self.credit_note_voucher.aggregate(
        the_sum=Coalesce(Sum('cgst_total'), Value(0)))['the_sum']
        total_sgst_stock = self.credit_note_voucher.aggregate(
            the_sum=Coalesce(Sum('sgst_total'), Value(0)))['the_sum']
        total_igst_stock = self.credit_note_voucher.aggregate(
            the_sum=Coalesce(Sum('igst_total'), Value(0)))['the_sum']

        if not total_cgst_stock:
            total_cgst_stock = 0

        if not total_sgst_stock:
            total_sgst_stock = 0

        if not total_igst_stock:
            total_igst_stock = 0

        total_cgst_extra = self.credit_note_term.aggregate(
            the_sum=Coalesce(Sum('cgst_total'), Value(0)))['the_sum']
        total_sgst_extra = self.credit_note_term.aggregate(
            the_sum=Coalesce(Sum('sgst_total'), Value(0)))['the_sum']
        total_igst_extra = self.credit_note_term.aggregate(
            the_sum=Coalesce(Sum('igst_total'), Value(0)))['the_sum']

        if not total_cgst_extra:
            total_cgst_extra = 0

        if not total_sgst_extra:
            total_sgst_extra = 0

        if not total_igst_extra:
            total_igst_extra = 0

        self.cgst_total = total_cgst_stock + total_cgst_extra
        
        self.sgst_total = total_sgst_stock + total_sgst_extra

        self.igst_total = total_igst_stock + total_igst_extra

        if not self.url_hash:
            if self.user.profile.user_type == 'Bussiness user':
                self.url_hash = 'BU' + '-' + str(self.user.id) + '-' + 'P' + '-' + '1' + '-' + 'C' + str(
                    self.company.counter) + '-' + ('SP') + str(self.counter)
            else:
                self.url_hash = 'PU' + '-' + str(self.user.id) + '-' + 'P' + '-' + '1' + '-' + 'C' + str(
                    self.company.counter) + '-' + ('SP') + str(self.counter)

        super(CreditNoteVoucher, self).save()


class CreditNoteStock(models.Model):
    """
    Credit Note Stock Model
    """
    credit_note = models.ForeignKey(CreditNoteVoucher, on_delete=models.CASCADE, null=True, blank=False, related_name='credit_note_voucher')
    stock_item = models.ForeignKey(StockItem, on_delete=models.DO_NOTHING, related_name='credit_note_stock')
    quantity = models.DecimalField(max_digits=20, decimal_places=3, default=0.000)
    rate = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    disc = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    tax = models.DecimalField(default=0.00, max_digits=5, decimal_places=2)  # composite tax percent
    cgst = models.DecimalField(default=0.00, max_digits=5, decimal_places=2)
    sgst = models.DecimalField(default=0.00, max_digits=5, decimal_places=2)
    igst = models.DecimalField(default=0.00, max_digits=5, decimal_places=2)
    cess = models.DecimalField(default=0.00, max_digits=5, decimal_places=2)
    cgst_total = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    sgst_total = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    igst_total = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    cess_total = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    tax_total = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)

    def __str__(self):
        return str(self.credit_note)

    def save(self, **kwargs):
        """
        Save function to override the total value of particular stock and their GST Total
        """
        self.total = self.rate * self.quantity * (1 - (self.disc/100))
        print('Not Regular Company')


        if self.stock_item:
            if self.stock_item.is_non_gst != 'Yes' and self.stock_item.taxability != 'Exempt' and self.stock_item.taxability != 'Nil Rated' and self.stock_item.taxability != 'Unknown':
                if self.credit_note.company.gst_registration_type == 'Regular':
                    if self.credit_note.company.organisation.state == self.credit_note.supply_place and self.credit_note.nature_transactions_sales == 'Not Applicable':
                        if self.credit_note.doc_ledger.central_tax != 0 or self.credit_note.doc_ledger.state_tax != 0:
                            self.cgst = self.credit_note.doc_ledger.central_tax
                            self.sgst = self.credit_note.doc_ledger.state_tax
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
                            self.cgst = self.credit_note.company.central_tax
                            self.sgst = self.credit_note.company.state_tax
                            self.igst = 0

                    elif self.credit_note.company.organisation.state != self.credit_note.supply_place and self.credit_note.nature_transactions_sales == 'Not Applicable':
                        if self.credit_note.doc_ledger.integrated_tax != 0:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = self.credit_note.doc_ledger.integrated_tax

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
                            self.igst = self.credit_note.company.integrated_tax

                    elif self.credit_note.nature_transactions_sales == 'Deemed Exports Taxable':
                        if self.credit_note.doc_ledger.central_tax != 0 or self.credit_note.doc_ledger.state_tax != 0:
                            self.cgst = self.credit_note.doc_ledger.central_tax
                            self.sgst = self.credit_note.doc_ledger.state_tax
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
                            self.cgst = self.credit_note.company.central_tax
                            self.sgst = self.credit_note.company.state_tax
                            self.igst = 0

                    elif self.credit_note.nature_transactions_sales == 'Intrastate Sales Taxable':
                        if self.credit_note.doc_ledger.central_tax != 0 or self.credit_note.doc_ledger.state_tax != 0:
                            self.cgst = self.credit_note.doc_ledger.central_tax
                            self.sgst = self.credit_note.doc_ledger.state_tax
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
                            self.cgst = self.credit_note.company.central_tax
                            self.sgst = self.credit_note.company.state_tax
                            self.igst = 0

                    elif self.credit_note.nature_transactions_sales == 'sales to Consumer - Taxable':
                        if self.credit_note.doc_ledger.central_tax != 0 or self.credit_note.doc_ledger.state_tax != 0:
                            self.cgst = self.credit_note.doc_ledger.central_tax
                            self.sgst = self.credit_note.doc_ledger.state_tax
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
                            self.cgst = self.credit_note.company.central_tax
                            self.sgst = self.credit_note.company.state_tax
                            self.igst = 0

                    elif self.credit_note.nature_transactions_sales == 'Interstate Deemed Exports Taxable':
                        if self.credit_note.doc_ledger.integrated_tax != 0:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = self.credit_note.doc_ledger.integrated_tax

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
                            self.igst = self.credit_note.company.integrated_tax

                    elif self.credit_note.nature_transactions_sales == 'Exports Taxable':
                        if self.credit_note.doc_ledger.integrated_tax != 0:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = self.credit_note.doc_ledger.integrated_tax

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
                            self.igst = self.credit_note.company.integrated_tax

                    elif self.credit_note.nature_transactions_sales == 'Interstate Sales - Taxable':
                        if self.credit_note.doc_ledger.integrated_tax != 0:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = self.credit_note.doc_ledger.integrated_tax

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
                            self.igst = self.credit_note.company.integrated_tax
                    elif self.credit_note.nature_transactions_sales == 'Interstate Sales to Embassy / UN Body Taxable':
                        if self.credit_note.doc_ledger.integrated_tax != 0:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = self.credit_note.doc_ledger.integrated_tax

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
                            self.igst = self.credit_note.company.integrated_tax

                    elif self.credit_note.nature_transactions_sales == 'Sales to SEZ - Taxable':
                        if self.credit_note.doc_ledger.integrated_tax != 0:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = self.credit_note.doc_ledger.integrated_tax

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
                            self.igst = self.credit_note.company.integrated_tax

                    elif self.credit_note.company.organisation.state == 'Andaman & Nicobar Islands' and self.credit_note.party_ac.state == 'Andaman & Nicobar Islands' and self.credit_note.nature_transactions_sales == 'Deemed Exports Taxable':
                        if self.credit_note.doc_ledger.central_tax != 0 or self.credit_note.doc_ledger.state_tax != 0:
                            self.cgst = self.credit_note.doc_ledger.central_tax
                            self.sgst = self.credit_note.doc_ledger.state_tax
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
                            self.cgst = self.credit_note.company.central_tax
                            self.sgst = self.credit_note.company.state_tax
                            self.igst = 0
                            self.sgst = 0

                    elif self.credit_note.company.organisation.state == 'Andaman & Nicobar Islands' and self.credit_note.party_ac.state == 'Andaman & Nicobar Islands' and self.credit_note.nature_transactions_sales == 'Intrastate Sales Taxable':
                        if self.credit_note.doc_ledger.central_tax != 0 or self.credit_note.doc_ledger.state_tax != 0:
                            self.cgst = self.credit_note.doc_ledger.central_tax
                            self.sgst = self.credit_note.doc_ledger.state_tax
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
                            self.cgst = self.credit_note.company.central_tax
                            self.sgst = self.credit_note.company.state_tax
                            self.igst = 0

                    elif self.credit_note.company.organisation.state == 'Andaman & Nicobar Islands' and self.credit_note.party_ac.state == 'Andaman & Nicobar Islands' and self.credit_note.nature_transactions_sales == 'sales to Consumer - Taxable':
                        if self.credit_note.doc_ledger.central_tax != 0 or self.credit_note.doc_ledger.state_tax != 0:
                            self.cgst = self.credit_note.doc_ledger.central_tax
                            self.sgst = self.credit_note.doc_ledger.state_tax
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
                            self.cgst = self.credit_note.company.central_tax
                            self.sgst = self.credit_note.company.state_tax
                            self.igst = 0
                    elif self.credit_note.company.organisation.state == 'Chandigarh' and self.credit_note.party_ac.state == 'Chandigarh' and self.credit_note.nature_transactions_sales == 'Intrastate Sales Taxable':
                        if self.credit_note.doc_ledger.central_tax != 0 or self.credit_note.doc_ledger.state_tax != 0:
                            self.cgst = self.credit_note.doc_ledger.central_tax
                            self.sgst = self.credit_note.doc_ledger.state_tax
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
                            self.cgst = self.credit_note.company.central_tax
                            self.sgst = self.credit_note.company.state_tax
                            self.igst = 0
                    elif self.credit_note.company.organisation.state == 'Chandigarh' and self.credit_note.party_ac.state == 'Chandigarh' and self.credit_note.nature_transactions_sales == 'Deemed Exports Taxable':
                        if self.credit_note.doc_ledger.central_tax != 0 or self.credit_note.doc_ledger.state_tax != 0:
                            self.cgst = self.credit_note.doc_ledger.central_tax
                            self.sgst = self.credit_note.doc_ledger.state_tax
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
                            self.cgst = self.credit_note.company.central_tax
                            self.sgst = self.credit_note.company.state_tax
                            self.igst = 0
                    elif self.credit_note.company.organisation.state == 'Chandigarh' and self.credit_note.party_ac.state == 'Chandigarh' and self.credit_note.nature_transactions_sales == 'sales to Consumer - Taxable':
                        if self.credit_note.doc_ledger.central_tax != 0 or self.credit_note.doc_ledger.state_tax != 0:
                            self.cgst = self.credit_note.doc_ledger.central_tax
                            self.sgst = self.credit_note.doc_ledger.state_tax
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
                            self.cgst = self.credit_note.company.central_tax
                            self.sgst = self.credit_note.company.state_tax
                            self.igst = 0
                    elif self.credit_note.company.organisation.state == 'Dadra and Nagar Haveli' and self.credit_note.party_ac.state == 'Dadra and Nagar Haveli' and self.credit_note.nature_transactions_sales == 'Deemed Exports Taxable':
                        if self.credit_note.doc_ledger.central_tax != 0 or self.credit_note.doc_ledger.state_tax != 0:
                            self.cgst = self.credit_note.doc_ledger.central_tax
                            self.sgst = self.credit_note.doc_ledger.state_tax
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
                            self.cgst = self.credit_note.company.central_tax
                            self.sgst = self.credit_note.company.state_tax
                            self.igst = 0
                    elif self.credit_note.company.organisation.state == 'Dadra and Nagar Haveli' and self.credit_note.party_ac.state == 'Dadra and Nagar Haveli' and self.credit_note.nature_transactions_sales == 'Intrastate Sales Taxable':
                        if self.credit_note.doc_ledger.central_tax != 0 or self.credit_note.doc_ledger.state_tax != 0:
                            self.cgst = self.credit_note.doc_ledger.central_tax
                            self.sgst = self.credit_note.doc_ledger.state_tax
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
                            self.cgst = self.credit_note.company.central_tax
                            self.sgst = self.credit_note.company.state_tax
                            self.igst = 0
                    elif self.credit_note.company.organisation.state == 'Dadra and Nagar Haveli' and self.credit_note.party_ac.state == 'Dadra and Nagar Haveli' and self.credit_note.nature_transactions_sales == 'sales to Consumer - Taxable':
                        if self.credit_note.doc_ledger.central_tax != 0 or self.credit_note.doc_ledger.state_tax != 0:
                            self.cgst = self.credit_note.doc_ledger.central_tax
                            self.sgst = self.credit_note.doc_ledger.state_tax
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
                            self.cgst = self.credit_note.company.central_tax
                            self.sgst = self.credit_note.company.state_tax
                            self.igst = 0
                    elif self.credit_note.company.organisation.state == 'Daman and Diu' and self.credit_note.party_ac.state == 'Daman and Diu' and self.credit_note.nature_transactions_sales == 'Deemed Exports Taxable':
                        if self.credit_note.doc_ledger.central_tax != 0 or self.credit_note.doc_ledger.state_tax != 0:
                            self.cgst = self.credit_note.doc_ledger.central_tax
                            self.sgst = self.credit_note.doc_ledger.state_tax
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
                            self.cgst = self.credit_note.company.central_tax
                            self.sgst = self.credit_note.company.state_tax
                            self.igst = 0
                    elif self.credit_note.company.organisation.state == 'Daman and Diu' and self.credit_note.party_ac.state == 'Daman and Diu' and self.credit_note.nature_transactions_sales == 'Intrastate Sales Taxable':
                        if self.credit_note.doc_ledger.central_tax != 0 or self.credit_note.doc_ledger.state_tax != 0:
                            self.cgst = self.credit_note.doc_ledger.central_tax
                            self.sgst = self.credit_note.doc_ledger.state_tax
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
                            self.cgst = self.credit_note.company.central_tax
                            self.sgst = self.credit_note.company.state_tax
                            self.igst = 0
                    elif self.credit_note.company.organisation.state == 'Daman and Diu' and self.credit_note.party_ac.state == 'Daman and Diu' and self.credit_note.nature_transactions_sales == 'sales to Consumer - Taxable':
                        if self.credit_note.doc_ledger.central_tax != 0 or self.credit_note.doc_ledger.state_tax != 0:
                            self.cgst = self.credit_note.doc_ledger.central_tax
                            self.sgst = self.credit_note.doc_ledger.state_tax
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
                            self.cgst = self.credit_note.company.central_tax
                            self.sgst = self.credit_note.company.state_tax
                            self.igst = 0
                    elif self.credit_note.company.organisation.state == 'Lakshadweep' and self.credit_note.party_ac.state == 'Lakshadweep' and self.credit_note.nature_transactions_sales == 'Deemed Exports Taxable':
                        if self.credit_note.doc_ledger.central_tax != 0 or self.credit_note.doc_ledger.state_tax != 0:
                            self.cgst = self.credit_note.doc_ledger.central_tax
                            self.sgst = self.credit_note.doc_ledger.state_tax
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
                            self.cgst = self.credit_note.company.central_tax
                            self.sgst = self.credit_note.company.state_tax
                            self.igst = 0
                    elif self.credit_note.company.organisation.state == 'Lakshadweep' and self.credit_note.party_ac.state == 'Lakshadweep' and self.credit_note.nature_transactions_sales == 'Intrastate Sales Taxable':
                        if self.credit_note.doc_ledger.central_tax != 0 or self.credit_note.doc_ledger.state_tax != 0:
                            self.cgst = self.credit_note.doc_ledger.central_tax
                            self.sgst = self.credit_note.doc_ledger.state_tax
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
                            self.cgst = self.credit_note.company.central_tax
                            self.sgst = self.credit_note.company.state_tax
                            self.igst = 0

                    elif self.credit_note.company.organisation.state == 'Lakshadweep' and self.credit_note.party_ac.state == 'Lakshadweep' and self.credit_note.nature_transactions_sales == 'sales to Consumer - Taxable':
                        if self.credit_note.doc_ledger.central_tax != 0 or self.credit_note.doc_ledger.state_tax != 0:
                            self.cgst = self.credit_note.doc_ledger.central_tax
                            self.sgst = self.credit_note.doc_ledger.state_tax
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
                            self.cgst = self.credit_note.company.central_tax
                            self.sgst = self.credit_note.company.state_tax
                            self.igst = 0

                    else:
                        self.cgst = 0
                        self.sgst = 0
                        self.igst = 0
                else:
                    self.tax = self.stock_item.integrated_tax
            else:
                if self.credit_note.company.gst_registration_type == 'Regular':
                    if self.credit_note.company.organisation.state == self.credit_note.supply_place and self.credit_note.nature_transactions_sales == 'Not Applicable':
                        if self.credit_note.doc_ledger.central_tax != 0 or self.credit_note.doc_ledger.state_tax != 0:
                            self.cgst = self.credit_note.doc_ledger.central_tax
                            self.sgst = self.credit_note.doc_ledger.state_tax
                            self.igst = 0
                        else:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = 0

                    elif self.credit_note.company.organisation.state != self.credit_note.supply_place and self.credit_note.nature_transactions_sales == 'Not Applicable':
                        if self.credit_note.doc_ledger.integrated_tax != 0:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = self.credit_note.doc_ledger.integrated_tax

                        else:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = 0

                    elif self.credit_note.nature_transactions_sales == 'Deemed Exports Taxable':
                        if self.credit_note.doc_ledger.central_tax != 0 or self.credit_note.doc_ledger.state_tax != 0:
                            self.cgst = self.credit_note.doc_ledger.central_tax
                            self.sgst = self.credit_note.doc_ledger.state_tax
                            self.igst = 0

                        else:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = 0

                    elif self.credit_note.nature_transactions_sales == 'Intrastate Sales Taxable':
                        if self.credit_note.doc_ledger.central_tax != 0 or self.credit_note.doc_ledger.state_tax != 0:
                            self.cgst = self.credit_note.doc_ledger.central_tax
                            self.sgst = self.credit_note.doc_ledger.state_tax
                            self.igst = 0

                        else:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = 0

                    elif self.credit_note.nature_transactions_sales == 'sales to Consumer - Taxable':
                        if self.credit_note.doc_ledger.central_tax != 0 or self.credit_note.doc_ledger.state_tax != 0:
                            self.cgst = self.credit_note.doc_ledger.central_tax
                            self.sgst = self.credit_note.doc_ledger.state_tax
                            self.igst = 0

                        else:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = 0

                    elif self.credit_note.nature_transactions_sales == 'Interstate Deemed Exports Taxable':
                        if self.credit_note.doc_ledger.integrated_tax != 0:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = self.credit_note.doc_ledger.integrated_tax

                        else:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = 0

                    elif self.credit_note.nature_transactions_sales == 'Exports Taxable':
                        if self.credit_note.doc_ledger.integrated_tax != 0:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = self.credit_note.doc_ledger.integrated_tax

                        else:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = 0

                    elif self.credit_note.nature_transactions_sales == 'Interstate Sales - Taxable':
                        if self.credit_note.doc_ledger.integrated_tax != 0:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = self.credit_note.doc_ledger.integrated_tax

                        else:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = 0

                    elif self.credit_note.nature_transactions_sales == 'Interstate Sales to Embassy / UN Body Taxable':
                        if self.credit_note.doc_ledger.integrated_tax != 0:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = self.credit_note.doc_ledger.integrated_tax

                        else:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = 0

                    elif self.credit_note.nature_transactions_sales == 'Sales to SEZ - Taxable':
                        if self.credit_note.doc_ledger.integrated_tax != 0:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = self.credit_note.doc_ledger.integrated_tax

                        else:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = 0

                    elif self.credit_note.company.organisation.state == 'Andaman & Nicobar Islands' and self.credit_note.party_ac.state == 'Andaman & Nicobar Islands' and self.credit_note.nature_transactions_sales == 'Deemed Exports Taxable':
                        if self.credit_note.doc_ledger.central_tax != 0 or self.credit_note.doc_ledger.state_tax != 0:
                            self.cgst = self.credit_note.doc_ledger.central_tax
                            self.sgst = self.credit_note.doc_ledger.state_tax
                            self.igst = 0

                        else:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = 0

                    elif self.credit_note.company.organisation.state == 'Andaman & Nicobar Islands' and self.credit_note.party_ac.state == 'Andaman & Nicobar Islands' and self.credit_note.nature_transactions_sales == 'Intrastate Sales Taxable':
                        if self.credit_note.doc_ledger.central_tax != 0 or self.credit_note.doc_ledger.state_tax != 0:
                            self.cgst = self.credit_note.doc_ledger.central_tax
                            self.sgst = self.credit_note.doc_ledger.state_tax
                            self.igst = 0

                        else:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = 0

                    elif self.credit_note.company.organisation.state == 'Andaman & Nicobar Islands' and self.credit_note.party_ac.state == 'Andaman & Nicobar Islands' and self.credit_note.nature_transactions_sales == 'sales to Consumer - Taxable':
                        if self.credit_note.doc_ledger.central_tax != 0 or self.credit_note.doc_ledger.state_tax != 0:
                            self.cgst = self.credit_note.doc_ledger.central_tax
                            self.sgst = self.credit_note.doc_ledger.state_tax
                            self.igst = 0

                        else:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = 0

                    elif self.credit_note.company.organisation.state == 'Chandigarh' and self.credit_note.party_ac.state == 'Chandigarh' and self.credit_note.nature_transactions_sales == 'Intrastate Sales Taxable':
                        if self.credit_note.doc_ledger.central_tax != 0 or self.credit_note.doc_ledger.state_tax != 0:
                            self.cgst = self.credit_note.doc_ledger.central_tax
                            self.sgst = self.credit_note.doc_ledger.state_tax
                            self.igst = 0

                        else:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = 0

                    elif self.credit_note.company.organisation.state == 'Chandigarh' and self.credit_note.party_ac.state == 'Chandigarh' and self.credit_note.nature_transactions_sales == 'Deemed Exports Taxable':
                        if self.credit_note.doc_ledger.central_tax != 0 or self.credit_note.doc_ledger.state_tax != 0:
                            self.cgst = self.credit_note.doc_ledger.central_tax
                            self.sgst = self.credit_note.doc_ledger.state_tax
                            self.igst = 0

                        else:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = 0

                    elif self.credit_note.company.organisation.state == 'Chandigarh' and self.credit_note.party_ac.state == 'Chandigarh' and self.credit_note.nature_transactions_sales == 'sales to Consumer - Taxable':
                        if self.credit_note.doc_ledger.central_tax != 0 or self.credit_note.doc_ledger.state_tax != 0:
                            self.cgst = self.credit_note.doc_ledger.central_tax
                            self.sgst = self.credit_note.doc_ledger.state_tax
                            self.igst = 0

                        else:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = 0

                    elif self.credit_note.company.organisation.state == 'Dadra and Nagar Haveli' and self.credit_note.party_ac.state == 'Dadra and Nagar Haveli' and self.credit_note.nature_transactions_sales == 'Deemed Exports Taxable':
                        if self.credit_note.doc_ledger.central_tax != 0 or self.credit_note.doc_ledger.state_tax != 0:
                            self.cgst = self.credit_note.doc_ledger.central_tax
                            self.sgst = self.credit_note.doc_ledger.state_tax
                            self.igst = 0

                        else:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = 0

                    elif self.credit_note.company.organisation.state == 'Dadra and Nagar Haveli' and self.credit_note.party_ac.state == 'Dadra and Nagar Haveli' and self.credit_note.nature_transactions_sales == 'Intrastate Sales Taxable':
                        if self.credit_note.doc_ledger.central_tax != 0 or self.credit_note.doc_ledger.state_tax != 0:
                            self.cgst = self.credit_note.doc_ledger.central_tax
                            self.sgst = self.credit_note.doc_ledger.state_tax
                            self.igst = 0

                        else:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = 0

                    elif self.credit_note.company.organisation.state == 'Dadra and Nagar Haveli' and self.credit_note.party_ac.state == 'Dadra and Nagar Haveli' and self.credit_note.nature_transactions_sales == 'sales to Consumer - Taxable':
                        if self.credit_note.doc_ledger.central_tax != 0 or self.credit_note.doc_ledger.state_tax != 0:
                            self.cgst = self.credit_note.doc_ledger.central_tax
                            self.sgst = self.credit_note.doc_ledger.state_tax
                            self.igst = 0

                        else:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = 0

                    elif self.credit_note.company.organisation.state == 'Daman and Diu' and self.credit_note.party_ac.state == 'Daman and Diu' and self.credit_note.nature_transactions_sales == 'Deemed Exports Taxable':
                        if self.credit_note.doc_ledger.central_tax != 0 or self.credit_note.doc_ledger.state_tax != 0:
                            self.cgst = self.credit_note.doc_ledger.central_tax
                            self.sgst = self.credit_note.doc_ledger.state_tax
                            self.igst = 0

                        else:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = 0

                    elif self.credit_note.company.organisation.state == 'Daman and Diu' and self.credit_note.party_ac.state == 'Daman and Diu' and self.credit_note.nature_transactions_sales == 'Intrastate Sales Taxable':
                        if self.credit_note.doc_ledger.central_tax != 0 or self.credit_note.doc_ledger.state_tax != 0:
                            self.cgst = self.credit_note.doc_ledger.central_tax
                            self.sgst = self.credit_note.doc_ledger.state_tax
                            self.igst = 0

                        else:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = 0

                    elif self.credit_note.company.organisation.state == 'Daman and Diu' and self.credit_note.party_ac.state == 'Daman and Diu' and self.credit_note.nature_transactions_sales == 'sales to Consumer - Taxable':
                        if self.credit_note.doc_ledger.central_tax != 0 or self.credit_note.doc_ledger.state_tax != 0:
                            self.cgst = self.credit_note.doc_ledger.central_tax
                            self.sgst = self.credit_note.doc_ledger.state_tax
                            self.igst = 0

                        else:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = 0

                    elif self.credit_note.company.organisation.state == 'Lakshadweep' and self.credit_note.party_ac.state == 'Lakshadweep' and self.credit_note.nature_transactions_sales == 'Deemed Exports Taxable':
                        if self.credit_note.doc_ledger.central_tax != 0 or self.credit_note.doc_ledger.state_tax != 0:
                            self.cgst = self.credit_note.doc_ledger.central_tax
                            self.sgst = self.credit_note.doc_ledger.state_tax
                            self.igst = 0

                        else:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = 0

                    elif self.credit_note.company.organisation.state == 'Lakshadweep' and self.credit_note.party_ac.state == 'Lakshadweep' and self.credit_note.nature_transactions_sales == 'Intrastate Sales Taxable':
                        if self.credit_note.doc_ledger.central_tax != 0 or self.credit_note.doc_ledger.state_tax != 0:
                            self.cgst = self.credit_note.doc_ledger.central_tax
                            self.sgst = self.credit_note.doc_ledger.state_tax
                            self.igst = 0

                        else:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = 0

                    elif self.credit_note.company.organisation.state == 'Lakshadweep' and self.credit_note.party_ac.state == 'Lakshadweep' and self.credit_note.nature_transactions_sales == 'sales to Consumer - Taxable':
                        if self.credit_note.doc_ledger.central_tax != 0 or self.credit_note.doc_ledger.state_tax != 0:
                            self.cgst = self.credit_note.doc_ledger.central_tax
                            self.sgst = self.credit_note.doc_ledger.state_tax
                            self.igst = 0

                        else:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = 0

                    else:
                        self.cgst = 0
                        self.sgst = 0
                        self.igst = 0
                else:
                    self.tax = self.stock_item.integrated_tax


        if self.credit_note.company.gst_registration_type == 'Regular':
            if self.credit_note.nature_transactions_sales == 'Deemed Exports Taxable':
                self.cgst_total = self.cgst * self.total / 100
                self.sgst_total = self.sgst * self.total / 100
                self.igst_total = 0

            elif self.credit_note.nature_transactions_sales == 'Intrastate Sales Taxable':
                self.cgst_total = self.cgst * self.total / 100
                self.sgst_total = self.sgst * self.total / 100
                self.igst_total = 0

            elif self.credit_note.nature_transactions_sales == 'sales to Consumer - Taxable':
                self.cgst_total = self.cgst * self.total / 100
                self.sgst_total = self.sgst * self.total / 100
                self.igst_total = 0

            elif self.credit_note.nature_transactions_sales == 'Interstate Deemed Exports Taxable':
                self.cgst_total = 0
                self.sgst_total = 0
                self.igst_total = self.igst * self.total / 100

            elif self.credit_note.nature_transactions_sales == 'Exports Taxable':
                self.cgst_total = 0
                self.sgst_total = 0
                self.igst_total = self.igst * self.total / 100

            elif self.credit_note.nature_transactions_sales == 'Interstate Sales - Taxable':
                self.cgst_total = 0
                self.sgst_total = 0
                self.igst_total = self.igst * self.total / 100

            elif self.credit_note.nature_transactions_sales == 'Interstate Sales to Embassy / UN Body Taxable':
                self.cgst_total = 0
                self.sgst_total = 0
                self.igst_total = self.igst * self.total / 100

            elif self.credit_note.nature_transactions_sales == 'Sales to SEZ - Taxable':
                self.cgst_total = 0
                self.sgst_total = 0
                self.igst_total = self.igst * self.total / 100

            elif self.credit_note.company.organisation.state == 'Andaman & Nicobar Islands' and self.credit_note.party_ac.state == 'Andaman & Nicobar Islands' and self.credit_note.nature_transactions_sales == 'Deemed Exports Taxable':
                self.cgst_total = self.cgst * self.total / 100
                self.sgst_total = self.sgst * self.total / 100
                self.igst_total = 0

            elif self.credit_note.company.organisation.state == 'Andaman & Nicobar Islands' and self.credit_note.party_ac.state == 'Andaman & Nicobar Islands' and self.credit_note.nature_transactions_sales == 'Intrastate Sales Taxable':
                self.cgst_total = self.cgst * self.total / 100
                self.sgst_total = self.sgst * self.total / 100
                self.igst_total = 0

            elif self.credit_note.company.organisation.state == 'Andaman & Nicobar Islands' and self.credit_note.party_ac.state == 'Andaman & Nicobar Islands' and self.credit_note.nature_transactions_sales == 'sales to Consumer - Taxable':
                self.cgst_total = self.cgst * self.total / 100
                self.sgst_total = self.sgst * self.total / 100
                self.igst_total = 0

            elif self.credit_note.company.organisation.state == 'Chandigarh' and self.credit_note.party_ac.state == 'Chandigarh' and self.credit_note.nature_transactions_sales == 'Deemed Exports Taxable':
                self.cgst_total = self.cgst * self.total / 100
                self.sgst_total = self.sgst * self.total / 100
                self.igst_total = 0

            elif self.credit_note.company.organisation.state == 'Chandigarh' and self.credit_note.party_ac.state == 'Chandigarh' and self.credit_note.nature_transactions_sales == 'Intrastate Sales Taxable':
                self.cgst_total = self.cgst * self.total / 100
                self.sgst_total = self.sgst * self.total / 100
                self.igst_total = 0

            elif self.credit_note.company.organisation.state == 'Chandigarh' and self.credit_note.party_ac.state == 'Chandigarh' and self.credit_note.nature_transactions_sales == 'sales to Consumer - Taxable':
                self.cgst_total = self.cgst * self.total / 100
                self.sgst_total = self.sgst * self.total / 100
                self.igst_total = 0

            elif self.credit_note.company.organisation.state == 'Dadra and Nagar Haveli' and self.credit_note.party_ac.state == 'Dadra and Nagar Haveli' and self.credit_note.nature_transactions_sales == 'Deemed Exports Taxable':
                self.cgst_total = self.cgst * self.total / 100
                self.sgst_total = self.sgst * self.total / 100
                self.igst_total = 0

            elif self.credit_note.company.organisation.state == 'Dadra and Nagar Haveli' and self.credit_note.party_ac.state == 'Dadra and Nagar Haveli' and self.credit_note.nature_transactions_sales == 'Intrastate Sales Taxable':
                self.cgst_total = self.cgst * self.total / 100
                self.sgst_total = self.sgst * self.total / 100
                self.igst_total = 0

            elif self.credit_note.company.organisation.state == 'Dadra and Nagar Haveli' and self.credit_note.party_ac.state == 'Dadra and Nagar Haveli' and self.credit_note.nature_transactions_sales == 'sales to Consumer - Taxable':
                self.cgst_total = self.cgst * self.total / 100
                self.sgst_total = self.sgst * self.total / 100
                self.igst_total = 0

            elif self.credit_note.company.organisation.state == 'Daman and Diu' and self.credit_note.party_ac.state == 'Daman and Diu' and self.credit_note.nature_transactions_sales == 'Deemed Exports Taxable':
                self.cgst_total = self.cgst * self.total / 100
                self.sgst_total = self.sgst * self.total / 100
                self.igst_total = 0

            elif self.credit_note.company.organisation.state == 'Daman and Diu' and self.credit_note.party_ac.state == 'Daman and Diu' and self.credit_note.nature_transactions_sales == 'Intrastate Sales Taxable':
                self.cgst_total = self.cgst * self.total / 100
                self.sgst_total = self.sgst * self.total / 100
                self.igst_total = 0

            elif self.credit_note.company.organisation.state == 'Daman and Diu' and self.credit_note.party_ac.state == 'Daman and Diu' and self.credit_note.nature_transactions_sales == 'sales to Consumer - Taxable':
                self.cgst_total = self.cgst * self.total / 100
                self.sgst_total = self.sgst * self.total / 100
                self.igst_total = 0

            elif self.credit_note.company.organisation.state == 'Lakshadweep' and self.credit_note.party_ac.state == 'Lakshadweep' and self.credit_note.nature_transactions_sales == 'Deemed Exports Taxable':
                self.cgst_total = self.cgst * self.total / 100
                self.sgst_total = self.sgst * self.total / 100
                self.igst_total = 0

            elif self.credit_note.company.organisation.state == 'Lakshadweep' and self.credit_note.party_ac.state == 'Lakshadweep' and self.credit_note.nature_transactions_sales == 'Intrastate Sales Taxable':
                self.cgst_total = self.cgst * self.total / 100
                self.sgst_total = self.sgst * self.total / 100
                self.igst_total = 0

            elif self.credit_note.company.organisation.state == 'Lakshadweep' and self.credit_note.party_ac.state == 'Lakshadweep' and self.credit_note.nature_transactions_sales == 'sales to Consumer - Taxable':
                self.cgst_total = self.cgst * self.total / 100
                self.sgst_total = self.sgst * self.total / 100
                self.igst_total = 0
            else:
                self.cgst_total = 0
                self.sgst_total = 0
                self.igst_total = 0
        else:
            self.sgst_total = self.tax * self.total / 100
            self.tax_total = self.tax * self.total / 100

            super(CreditNoteStock, self).save()


class CreditNoteTerm(models.Model):
    """
    Credit Note Term Model
    """
    credit_note = models.ForeignKey(CreditNoteVoucher, on_delete=models.CASCADE, related_name='credit_note_term')
    ledger = models.ForeignKey(LedgerMaster, on_delete=models.DO_NOTHING, related_name='credit_note_term_ledger')
    rate = models.DecimalField(default=0.00, max_digits=5, decimal_places=2)
    tax = models.DecimalField(default=0.00, max_digits=5, decimal_places=2)  # composite tax percent
    cgst = models.DecimalField(default=0.00, max_digits=5, decimal_places=2)
    sgst = models.DecimalField(default=0.00, max_digits=5, decimal_places=2)
    igst = models.DecimalField(default=0.00, max_digits=5, decimal_places=2)
    cess = models.DecimalField(default=0.00, max_digits=5, decimal_places=2)
    cgst_total = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    sgst_total = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    igst_total = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    cess_total = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    tax_total = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)

    def __str__(self):
        return str(self.ledger)

    def save(self, **kwargs):
        """
        Save function to override the total value of particular ledger and their GST Totals
        """
        if self.total == 0:
            if self.rate != 0:
                self.total = self.credit_note.sub_total * (self.rate / 100)

        if self.ledger:
            if self.sale_voucher.company.gst_registration_type == 'Regular':
                if self.sale_voucher.nature_transactions_sales == 'Not Applicable':
                    if self.ledger.nature_transactions_sales == 'Not Applicable' and self.sale_voucher.supply_place.id == self.sale_voucher.company.organisation.state.id:
                        if self.ledger.central_tax != 0 or self.ledger.state_tax != 0:
                            self.cgst = self.ledger.central_tax
                            self.sgst = self.ledger.state_tax
                            self.igst = 0

                        else:
                            self.cgst = self.sale_voucher.company.central_tax
                            self.sgst = self.sale_voucher.company.state_tax
                            self.igst = 0

                    elif self.ledger.nature_transactions_sales == 'Not Applicable' and self.sale_voucher.supply_place.id != self.sale_voucher.company.organisation.state.id:
                        if self.ledger.integrated_tax != 0:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = self.ledger.integrated_tax
                        else:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = self.sale_voucher.company.integrated_tax

                    elif self.ledger.nature_transactions_sales == 'Deemed Exports Taxable':
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
                    elif self.ledger.nature_transactions_sales == 'Interstate Deemed Exports Taxable':
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
                    if self.sale_voucher.nature_transactions_sales == 'Not Applicable' and self.sale_voucher.supply_place.id == self.sale_voucher.company.organisation.state.id:
                        if self.ledger.central_tax != 0 or self.ledger.state_tax != 0:
                            self.cgst = self.ledger.central_tax
                            self.sgst = self.ledger.state_tax
                            self.igst = 0

                        else:
                            self.cgst = self.sale_voucher.company.central_tax
                            self.sgst = self.sale_voucher.company.state_tax
                            self.igst = 0

                    elif self.sale_voucher.nature_transactions_sales == 'Not Applicable' and self.sale_voucher.supply_place.id != self.sale_voucher.company.organisation.state.id:
                        if self.ledger.integrated_tax != 0:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = self.ledger.integrated_tax
                        else:
                            self.cgst = 0
                            self.sgst = 0
                            self.igst = self.sale_voucher.company.integrated_tax

                    elif self.sale_voucher.nature_transactions_sales == 'Deemed Exports Taxable':
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
                    elif self.sale_voucher.nature_transactions_sales == 'Interstate Deemed Exports Taxable':
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
                        print('Nothing')
                        self.cgst = 0
                        self.igst = 0
                        self.sgst = 0
                        self.sgst = 0

            else:
                self.tax = self.ledger.integrated_tax

        if self.ledger: 
            if self.sale_voucher.company.gst_registration_type == 'Regular':
                if self.sale_voucher.nature_transactions_sales == 'Not Applicable':
                    if self.ledger.nature_transactions_sales == 'Not Applicable' and self.sale_voucher.supply_place == self.sale_voucher.company.organisation.state:
                        self.cgst_total = self.cgst * self.total / 100
                        self.sgst_total = self.sgst * self.total / 100

                    elif self.ledger.nature_transactions_sales == 'Not Applicable' and self.sale_voucher.supply_place != self.sale_voucher.company.organisation.state:
                        self.cgst_total = 0
                        self.sgst_total = 0
                        self.igst_total = self.igst * self.total / 100

                    elif self.ledger.nature_transactions_sales == 'Deemed Exports Taxable':
                        self.cgst_total = self.cgst * self.total / 100
                        self.sgst_total = self.sgst * self.total / 100

                    elif self.ledger.nature_transactions_sales == 'Intrastate Sales Taxable':
                        self.cgst_total = self.cgst * self.total / 100
                        self.sgst_total = self.sgst * self.total / 100

                    elif self.ledger.nature_transactions_sales == 'sales to Consumer - Taxable':
                        self.cgst_total = self.cgst * self.total / 100
                        self.sgst_total = self.sgst * self.total / 100

                    elif self.ledger.nature_transactions_sales == 'Interstate Deemed Exports Taxable':
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
                    if self.sale_voucher.nature_transactions_sales == 'Not Applicable' and self.sale_voucher.supply_place == self.sale_voucher.company.organisation.state:
                        print
                        self.cgst_total = self.cgst * self.total / 100
                        self.sgst_total = self.sgst * self.total / 100

                    elif self.sale_voucher.nature_transactions_sales == 'Not Applicable' and self.sale_voucher.supply_place != self.sale_voucher.company.organisation.state:
                        self.cgst_total = 0
                        self.sgst_total = 0
                        self.igst_total = self.igst * self.total / 100

                    elif self.sale_voucher.nature_transactions_sales == 'Deemed Exports Taxable':
                        self.cgst_total = self.cgst * self.total / 100
                        self.sgst_total = self.sgst * self.total / 100

                    elif self.sale_voucher.nature_transactions_sales == 'Intrastate Sales Taxable':
                        self.cgst_total = self.cgst * self.total / 100
                        self.sgst_total = self.sgst * self.total / 100

                    elif self.sale_voucher.nature_transactions_sales == 'sales to Consumer - Taxable':
                        self.cgst_total = self.cgst * self.total / 100
                        self.sgst_total = self.sgst * self.total / 100

                    elif self.sale_voucher.nature_transactions_sales == 'Interstate Deemed Exports Taxable':
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
        super(CreditNoteTerm, self).save()


class CreditNoteTax(models.Model):
    """
    Credit Note Tax Model
    """
    credit_note = models.ForeignKey(CreditNoteVoucher, on_delete=models.CASCADE, related_name='credit_note_gst')
    ledger = models.ForeignKey(LedgerMaster, on_delete=models.DO_NOTHING, related_name='credit_note_tax_ledger')
    total = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)

    def __str__(self):
        return str(self.ledger)

    def save(self, **kwargs):
        """
        Save method to override the total value as per the ledger Selected in a voucher
        """
        if self.ledger:
            if self.ledger.tax_type == 'Central Tax':
                self.total = self.credit_note.cgst_total
            elif self.ledger.tax_type == 'State Tax':
                self.total = self.credit_note.sgst_total
            elif self.ledger.tax_type == 'Integrated Tax':
                self.total = self.credit_note.igst_total
            else:
                self.total = self.credit_note.cess_total
        super(CreditNoteTax, self).save()
