"""
Models
"""
import datetime
from django.conf import settings
from django.db.models import Value, Sum
from django.db.models.functions import Coalesce
from django.db import models
from bracketline.models import StateMaster, CountryMaster
from company.models import Company
from accounting_entry.models import LedgerMaster
from .model_purchase_accounts import PurchaseVoucherAccounts


class DebitNoteAccountsVoucher(models.Model):
    """
    Debit Note Voucher For Accounts Only Model
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_debit_note_accounts')
    purchase_voucher = models.ForeignKey(PurchaseVoucherAccounts, on_delete=models.CASCADE, related_name='debit_note_purchase_voucher_accounts',blank=True, null=True)
    counter = models.IntegerField()
    url_hash = models.CharField(max_length=100)
    voucher_date = models.DateField(default=datetime.date.today)

    bool_list = (
        ('Yes', 'Yes'),
        ('No', 'No')
    )
    manual = models.CharField(max_length=100, choices=bool_list, default='No')
    # manual entry field when ref voucher missing and manual value is Yes
    purchase_invno = models.CharField(max_length=30, null=True, blank=True)
    purchase_date = models.DateField(blank=True, null=True)
    purchase_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    ref_no = models.CharField(max_length=100)
    party_ac = models.ForeignKey(LedgerMaster, on_delete=models.CASCADE, related_name='party_ledger_debit_note_accounts')
    supply_place = models.ForeignKey(StateMaster, related_name="debit_note_supply_state_accounts", on_delete=models.DO_NOTHING, null=True, blank=True)

    transaction_types = (
        ('Not Applicable', 'Not Applicable'),
        ('Branch Transfer Inward', 'Branch Transfer Inward'),
        ('Imports Exempt', 'Imports Exempt'),
        ('Imports Nil Rated', 'Imports Nil Rated'),
        ('Imports Taxable', 'Imports Taxable'),
        ('Interstate Purchase Exempt', 'Interstate Purchase Exempt'),
        ('Interstate Purchase from Unregistered Dealer - Exempt',
         'Interstate Purchase from Unregistered Dealer - Exempt'),
        ('Interstate Purchase from Unregistered Dealer - Nil Rated',
         'Interstate Purchase from Unregistered Dealer - Nil Rated'),
        ('Interstate Purchase from Unregistered Dealer - Services',
         'Interstate Purchase from Unregistered Dealer - Services'),
        ('Interstate Purchase from Unregistered Dealer - Taxable',
         'Interstate Purchase from Unregistered Dealer - Taxable'),
        ('Interstate Purchase - Nil Rated',
         'Interstate Purchase  - Nil Rated '),
        ('Interstate Purchase - Taxable', 'Interstate Purchase  - Taxable'),
        ('Interstate Purchase Deemed Exports - Exempt',
         'Interstate Purchase Deemed Exports - Exempt'),
        ('Interstate Purchase Deemed Exports - Nil Rated',
         'Interstate Purchase Deemed Exports - Nil Rated'),
        ('Interstate Purchase Deemed Exports - Taxable',
         'Interstate Purchase Deemed Exports - Taxable'),
        ('Purchase Deemed Exports - Exempt',
         'Purchase Deemed Exports - Exempt'),
        ('Purchase Deemed Exports - Nil Rated',
         'Purchase Deemed Exports - Nil Rated'),
        ('Purchase Deemed Exports - Taxable',
         'Purchase Deemed Exports - Taxable'),
        ('Purchase Exempt', 'Purchase Exempt'),
        ('Purchase From Composition Dealer',
         'Purchase From Composition Dealer'),
        ('Purchase From SEZ - Exempt', 'Purchase From SEZ - Exempt'),
        ('Purchase From SEZ - LUT/Bond', 'Purchase From SEZ - LUT/Bond'),
        ('Purchase From SEZ - Nil Rated ', 'Purchase From SEZ - Nil Rated'),
        ('Purchase From SEZ - Taxable', 'Purchase From SEZ - Taxable'),
        ('Purchase From SEZ (Without Bill Of Entry) - Exempt',
         'Purchase From SEZ (Without Bill Of Entry) - Exempt'),
        ('Purchase From SEZ (Without Bill Of Entry) - Nil Rated',
         'Purchase From SEZ (Without Bill Of Entry) - Nil Rated'),
        ('Purchase From SEZ (Without Bill Of Entry) - Taxable',
         'Purchase From SEZ (Without Bill Of Entry) - Taxable'),
        ('Purchase From Unregister Dealer - Exempt',
         'Purchase From Unregister Dealer - Exempt'),
        ('Purchase From Unregister Dealer - Nil Rated',
         'Purchase From Unregister Dealer - Nil Rated'),
        ('Purchase From Unregister Dealer - Taxable',
         'Purchase From Unregister Dealer - Taxable'),
        ('Purchase Nil Rated', 'Purchase Nil Rated'),
        ('Intrastate Purchase Taxable', 'Intrastate Purchase Taxable'),
    )
    nature_transactions_purchase = models.CharField(max_length=100, choices=transaction_types, default='Not Applicable',blank=True)
    delivery_note = models.CharField(max_length=32, blank=True)
    supplier_ref = models.CharField(max_length=32, blank=True)
    mode = models.TextField(blank=True)
    sub_total = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    cgst_total = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    sgst_total = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    igst_total = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    cess_total = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    tax_total = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    gst_details = models.CharField(max_length=100, choices=bool_list, default='No')
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
    issue_reason = models.CharField(max_length=100, choices=reason, default='00')
    note_no = models.CharField(max_length=32, blank=True)
    date_after_no = models.DateField(default=datetime.date.today)
    bill_no = models.CharField(max_length=32, blank=True)
    bill_date = models.DateField(default=datetime.date.today, blank=True)
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
        CountryMaster, default=12, related_name="debit_note_supply_country_accounts", on_delete=models.DO_NOTHING, blank=True)

    def __str__(self):
        return str(self.party_ac)

    def save(self, **kwargs):
        gst_total = self.debit_note_gst_accounts.aggregate(
            the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']
        extra_total = self.debit_note_extra_accounts.aggregate(
            the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']
        if gst_total or extra_total:
            self.total = gst_total + extra_total
            self.sub_total = extra_total

        total_cgst_extra = self.debit_note_extra_accounts.aggregate(
        the_sum=Coalesce(Sum('cgst_total'), Value(0)))['the_sum']
        total_sgst_extra = self.debit_note_extra_accounts.aggregate(
            the_sum=Coalesce(Sum('sgst_total'), Value(0)))['the_sum']
        total_igst_extra = self.debit_note_extra_accounts.aggregate(
            the_sum=Coalesce(Sum('igst_total'), Value(0)))['the_sum']

        if not total_cgst_extra:
            total_cgst_extra = 0

        if not total_sgst_extra:
            total_sgst_extra = 0

        if not total_igst_extra:
            total_igst_extra = 0

        self.cgst_total = total_cgst_extra
        
        self.sgst_total = total_sgst_extra

        self.igst_total = total_igst_extra

        if not self.url_hash:
            if self.user.profile.user_type == 'Bussiness user':
                self.url_hash = 'BU' + '-' + str(self.user.id) + '-' + 'P' + '-' + '1' + '-' + 'C' + str(
                    self.company.counter) + '-' + ('SP') + str(self.counter)
            else:
                self.url_hash = 'PU' + '-' + str(self.user.id) + '-' + 'P' + '-' + '1' + '-' + 'C' + str(
                    self.company.counter) + '-' + ('SP') + str(self.counter)
        super(DebitNoteAccountsVoucher, self).save()



class DebitNoteAccountsTerm(models.Model):
    """
    Debit Note Term For Accounts Only Model
    """
    debit_note = models.ForeignKey(DebitNoteAccountsVoucher, on_delete=models.CASCADE, related_name='debit_note_extra_accounts')
    ledger = models.ForeignKey(LedgerMaster, on_delete=models.DO_NOTHING, related_name='debit_note_term_ledger_accounts')
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

        if self.ledger:
            if self.ledger.ledger_group.group_base.name != 'Direct Incomes' and self.ledger.ledger_group.group_base.name != 'Indirect Incomes' and self.ledger.ledger_group.group_base.name != 'Sales Accounts':     
                if self.debit_note.company.gst_registration_type == 'Regular':
                    if self.debit_note.nature_transactions_purchase == 'Not Applicable':
                        if self.ledger.nature_transactions_purchase == 'Purchase Deemed Exports - Taxable':
                            if self.ledger.central_tax != 0 or self.ledger.state_tax != 0:
                                self.cgst = self.ledger.central_tax
                                self.sgst = self.ledger.state_tax
                                self.igst = 0

                            else:
                                self.cgst = self.debit_note.company.central_tax
                                self.sgst = self.debit_note.company.state_tax
                                self.igst = 0

                        elif self.ledger.nature_transactions_purchase == 'Intrastate Purchase Taxable':
                            if self.ledger.central_tax != 0 or self.ledger.state_tax != 0:
                                self.cgst = self.ledger.central_tax
                                self.sgst = self.ledger.state_tax
                                self.igst = 0

                            else:
                                self.cgst = self.debit_note.company.central_tax
                                self.sgst = self.debit_note.company.state_tax
                                self.igst = 0

                        elif self.ledger.nature_transactions_purchase == 'Interstate Purchase Deemed Exports - Taxable':
                            if self.ledger.integrated_tax != 0:
                                self.cgst = 0
                                self.sgst = 0
                                self.igst = self.ledger.integrated_tax

                            else:
                                self.cgst = 0
                                self.sgst = 0
                                self.igst = self.debit_note.company.integrated_tax

                        elif self.ledger.nature_transactions_purchase == 'Interstate Purchase - Taxable':
                            if self.ledger.integrated_tax != 0:
                                self.cgst = 0
                                self.sgst = 0
                                self.igst = self.ledger.integrated_tax

                            else:
                                self.cgst = 0
                                self.sgst = 0
                                self.igst = self.debit_note.company.integrated_tax

                        elif self.ledger.nature_transactions_purchase == 'Purchase From SEZ (Without Bill Of Entry) - Taxable':
                            if self.ledger.integrated_tax != 0:
                                self.cgst = 0
                                self.sgst = 0
                                self.igst = self.ledger.integrated_tax

                            else:
                                self.cgst = 0
                                self.sgst = 0
                                self.igst = self.debit_note.company.integrated_tax

                        elif self.ledger.nature_transactions_purchase == 'Purchase From SEZ - Taxable':
                            if self.ledger.integrated_tax != 0:
                                self.cgst = 0
                                self.sgst = 0
                                self.igst = self.ledger.integrated_tax

                            else:
                                self.cgst = 0
                                self.sgst = 0
                                self.igst = self.debit_note.company.integrated_tax


                        else:
                            self.cgst = 0
                            self.igst = 0
                            self.sgst = 0

                    else:
                        if self.debit_note.nature_transactions_purchase == 'Purchase Deemed Exports - Taxable':
                            if self.ledger.central_tax != 0 or self.ledger.state_tax != 0:
                                self.cgst = self.ledger.central_tax
                                self.sgst = self.ledger.state_tax
                                self.igst = 0

                            else:
                                self.cgst = self.debit_note.company.central_tax
                                self.sgst = self.debit_note.company.state_tax
                                self.igst = 0

                        elif self.debit_note.nature_transactions_purchase == 'Intrastate Purchase Taxable':
                            if self.ledger.central_tax != 0 or self.ledger.state_tax != 0:
                                self.cgst = self.ledger.central_tax
                                self.sgst = self.ledger.state_tax
                                self.igst = 0

                            else:
                                self.cgst = self.debit_note.company.central_tax
                                self.sgst = self.debit_note.company.state_tax
                                self.igst = 0

                        elif self.debit_note.nature_transactions_purchase == 'Interstate Purchase Deemed Exports - Taxable':
                            if self.ledger.integrated_tax != 0:
                                self.cgst = 0
                                self.sgst = 0
                                self.igst = self.ledger.integrated_tax

                            else:
                                self.cgst = 0
                                self.sgst = 0
                                self.igst = self.debit_note.company.integrated_tax

                        elif self.debit_note.nature_transactions_purchase == 'Interstate Purchase - Taxable':
                            if self.ledger.integrated_tax != 0:
                                self.cgst = 0
                                self.sgst = 0
                                self.igst = self.ledger.integrated_tax

                            else:
                                self.cgst = 0
                                self.sgst = 0
                                self.igst = self.debit_note.company.integrated_tax

                        elif self.debit_note.nature_transactions_purchase == 'Purchase From SEZ (Without Bill Of Entry) - Taxable':
                            if self.ledger.integrated_tax != 0:
                                self.cgst = 0
                                self.sgst = 0
                                self.igst = self.ledger.integrated_tax

                            else:
                                self.cgst = 0
                                self.sgst = 0
                                self.igst = self.debit_note.company.integrated_tax

                        elif self.debit_note.nature_transactions_purchase == 'Purchase From SEZ - Taxable':
                            if self.ledger.integrated_tax != 0:
                                self.cgst = 0
                                self.sgst = 0
                                self.igst = self.ledger.integrated_tax

                            else:
                                self.cgst = 0
                                self.sgst = 0
                                self.igst = self.debit_note.company.integrated_tax
                        

                        else:
                            self.cgst = 0
                            self.igst = 0
                            self.sgst = 0
                else:
                    self.tax = self.ledger.integrated_tax

        if self.ledger:
            if self.ledger.ledger_group.group_base.name != 'Direct Incomes' and self.ledger.ledger_group.group_base.name != 'Indirect Incomes' and self.ledger.ledger_group.group_base.name != 'Sales Accounts':
                if self.debit_note.company.gst_registration_type == 'Regular':
                    if self.debit_note.nature_transactions_purchase == 'Not Applicable':
                        if self.ledger.nature_transactions_purchase == 'Purchase Deemed Exports - Taxable':
                            self.cgst_total = self.cgst * self.total / 100
                            self.sgst_total = self.sgst * self.total / 100

                        elif self.ledger.nature_transactions_purchase == 'Intrastate Purchase Taxable':
                            self.cgst_total = self.cgst * self.total / 100
                            self.sgst_total = self.sgst * self.total / 100

                        elif self.ledger.nature_transactions_purchase == 'Interstate Purchase Deemed Exports - Taxable':
                            self.cgst_total = 0
                            self.sgst_total = 0
                            self.igst_total = self.igst * self.total / 100

                        elif self.ledger.nature_transactions_purchase == 'Imports Taxable':
                            self.cgst_total = 0
                            self.sgst_total = 0
                            self.igst_total = 0

                        elif self.ledger.nature_transactions_purchase == 'Interstate Purchase - Taxable':
                            self.cgst_total = 0
                            self.sgst_total = 0
                            self.igst_total = self.igst * self.total / 100

                        elif self.ledger.nature_transactions_purchase == 'Purchase From SEZ (Without Bill Of Entry) - Taxable':
                            self.cgst_total = 0
                            self.sgst_total = 0
                            self.igst_total = self.igst * self.total / 100

                        elif self.ledger.nature_transactions_purchase == 'Purchase From SEZ - Taxable':
                            self.cgst_total = 0
                            self.sgst_total = 0
                            self.igst_total = self.igst * self.total / 100
                        else:
                            self.igst_total = self.igst * self.total / 100
                    else:
                        if self.debit_note.nature_transactions_purchase == 'Purchase Deemed Exports - Taxable':
                            self.cgst_total = self.cgst * self.total / 100
                            self.sgst_total = self.sgst * self.total / 100

                        elif self.debit_note.nature_transactions_purchase == 'Intrastate Purchase Taxable':
                            self.cgst_total = self.cgst * self.total / 100
                            self.sgst_total = self.sgst * self.total / 100

                        elif self.debit_note.nature_transactions_purchase == 'Interstate Purchase Deemed Exports - Taxable':
                            self.cgst_total = 0
                            self.sgst_total = 0
                            self.igst_total = self.igst * self.total / 100

                        elif self.debit_note.nature_transactions_purchase == 'Imports Taxable':
                            self.cgst_total = 0
                            self.sgst_total = 0
                            self.igst_total = 0

                        elif self.debit_note.nature_transactions_purchase == 'Interstate Purchase - Taxable':
                            self.cgst_total = 0
                            self.sgst_total = 0
                            self.igst_total = self.igst * self.total / 100

                        elif self.debit_note.nature_transactions_purchase == 'Purchase From SEZ (Without Bill Of Entry) - Taxable':
                            self.cgst_total = 0
                            self.sgst_total = 0
                            self.igst_total = self.igst * self.total / 100

                        elif self.debit_note.nature_transactions_purchase == 'Purchase From SEZ - Taxable':
                            self.cgst_total = 0
                            self.sgst_total = 0
                            self.igst_total = self.igst * self.total / 100
                        else:
                            self.igst_total = self.igst * self.total / 100
                else:
                    self.tax_total = self.tax * self.total / 100

        super(DebitNoteAccountsTerm, self).save()


class DebitNoteTax(models.Model):
    """
    Debit Note Tax For Accounts Only Model
    """
    debit_note = models.ForeignKey(DebitNoteAccountsVoucher, on_delete=models.CASCADE, related_name='debit_note_gst_accounts')
    ledger = models.ForeignKey(LedgerMaster, on_delete=models.DO_NOTHING, related_name='debit_note_tax_ledger_accounts')
    total = models.DecimalField(max_digits=20, decimal_places=2, default=0.00, null=True, blank=True)

    def __str__(self):
        return str(self.ledger)

    def save(self, **kwargs):
        """
        Save method to override the total value as per the ledger Selected in a voucher
        """
        if self.ledger:
            if self.ledger.tax_type == 'Central Tax':
                self.total = self.debit_note.cgst_total
            elif self.ledger.tax_type == 'State Tax':
                self.total = self.debit_note.sgst_total
            elif self.ledger.tax_type == 'Integrated Tax':
                self.total = self.debit_note.igst_total
            else:
                self.total = self.debit_note.cess_total
        super(DebitNoteTax, self).save()
