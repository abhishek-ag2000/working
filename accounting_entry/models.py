"""
Models
"""
import datetime
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from company.models import Company
from bracketline.models import CountryMaster, StateMaster
from bracketline.models import GroupBase


class PeriodSelected(models.Model):
    """
    Period selected by a user
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name="auth_user", on_delete=models.CASCADE)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(default=timezone.now)

    def __str__(self):
        return str(self.user.username + " [From "+ str(self.start_date) + " To " + str(self.end_date) + "]")

    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError({'start_date': ["Start Date cannot be greater than End Date"], 'end_date': [
                "Start Date cannot be greater than End Date"]})


class LedgerGroup(models.Model):
    """
    Ledger Group Master
    """
    counter = models.IntegerField()
    url_hash = models.CharField(max_length=100)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_ledger_group")
    group_name = models.CharField(max_length=50)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_ledger_group')
    self_group = models.ForeignKey("self", on_delete=models.DO_NOTHING, related_name='master_group', null=True)
    group_base = models.ForeignKey(GroupBase, on_delete=models.DO_NOTHING, default=1)  # default 1 is Primary group base

    # negative_opening = models.DecimalField(
    #     max_digits=19, default=0, decimal_places=10, null=True)
    # positive_opening = models.DecimalField(
    #     max_digits=19, default=0, decimal_places=10, null=True)
    # negative_closing = models.DecimalField(
    #     max_digits=19, default=0, decimal_places=10, null=True)
    # positive_closing = models.DecimalField(
    #     max_digits=19, default=0, decimal_places=10, null=True)

    def __str__(self):
        return self.group_name

    class Meta:
        ordering = ['group_name']
        unique_together = ['company', 'group_name']

    def get_absolute_url(self, **kwargs):
        """
        Returns the absolute url
        """
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        return reverse("accounting_entry:groupdetail", kwargs={'ledger_group_pk': self.pk, 'company_pk': company.pk})

    def save(self, *args, **kwargs):
        """
        Overwrite save to update base and url_hash
        """
        if self.group_base.name == "Primary" and self.self_group:
            self.group_base = self.self_group.group_base

        if not self.url_hash:
            if self.user.profile.user_type == 'Bussiness User':
                self.url_hash = 'BU' + '-' + str(self.user.id) + '-' + 'P' + '-' + '1' + '-' + 'C' + str(
                    self.company.counter) + '-' + ('AG') + str(self.counter)
            else:
                self.url_hash = 'PU' + '-' + str(self.user.id) + '-' + 'P' + '-' + '1' + '-' + 'C' + str(
                    self.company.counter) + '-' + ('AG') + str(self.counter)

        super(LedgerGroup, self).save(*args, **kwargs)


class LedgerMaster(models.Model):
    """
    Ledger Master
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_ledger_master')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_ledger_master')
    counter = models.IntegerField(blank=True)
    url_hash = models.CharField(max_length=100, blank=True)
    ledger_name = models.CharField(max_length=80) #unique together with company using meta
    ledger_group = models.ForeignKey(LedgerGroup, on_delete=models.DO_NOTHING, related_name='group_ledger')
    opening_balance = models.DecimalField(default=0.00, max_digits=19, decimal_places=2)
    balance_opening = models.DecimalField(default=0.00, max_digits=19, decimal_places=2)
    party_name = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.ForeignKey(CountryMaster, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='ledger_master_country')
    state = models.ForeignKey(StateMaster, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='ledger_master_state')
    pin_code = models.CharField(max_length=6, blank=True)
    pan_no = models.CharField(max_length=10, blank=True)
    gst_no = models.CharField(max_length=15, blank=True)
    closing_balance = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    # bank related fields
    account_holder_name = models.CharField(max_length=255, blank=True)
    account_no = models.CharField(max_length=30, blank=True)
    ifsc_code = models.CharField(max_length=255, blank=True)
    bank_name = models.CharField(max_length=255, blank=True)
    branch = models.CharField(max_length=255, blank=True)

    taxes = (
        ('Others', 'Others'),
        ('GST', 'GST'),
    )
    duty_tax_type = models.CharField(max_length=10, choices=taxes, default='Others', blank=True)
    types = (
        ('Central Tax', 'Central Tax'),
        ('Cess', 'Cess'),
        ('Integrated Tax', 'Integrated Tax'),
        ('State Tax', 'State Tax'),
    )
    tax_type = models.CharField(max_length=100, choices=types, blank=True)

    # For Current Assets & Unsecured Loans & Loans (Liability) & Secured Loans
    values = (
        ('Not Applicable', 'Not Applicable'),
        ('GST', 'GST'),
    )
    assessable_value = models.CharField(max_length=20, choices=values, default='Not Applicable', blank=True)

    appropiate = (
        ('Both', 'Both'),
        ('Goods', 'Goods'),
        ('Services', 'Services'),
    )
    appropiate_to = models.CharField(max_length=20, choices=appropiate, default='Both', blank=True)

    calculation = (
        ('Based on Quantity', 'Based on Quantity'),
        ('Based on Value', 'Based on Value'),
    )
    calculation_method = models.CharField(max_length=20, choices=calculation, default='Based on Value', blank=True)

    for_gst = (
        ('Applicable', 'Applicable'),
        ('Not Applicable', 'Not Applicable'),
        ('Undefined', 'Undefined'),
    )
    gst_applicable = models.CharField(max_length=20, choices=for_gst, default='Not Applicable', blank=True)

    yes_no_choice = (
        ('Yes', 'Yes'),
        ('No', 'No'),
    )
    set_or_alter_gst = models.CharField(max_length=3, choices=yes_no_choice, default='No', blank=True)
    set_or_alter_gst_tax = models.CharField(max_length=3, choices=yes_no_choice, default='No', blank=True)

    supplies = (
        ('Goods', 'Goods'),
        ('Services', 'Services'),
    )
    supply_type = models.CharField(max_length=10, choices=supplies, default='Goods', blank=True)

    registration = (
        ('Unknown', 'Unknown'),
        ('Composition', 'Composition'),
        ('Consumer', 'Consumer'),
        ('Regular', 'Regular'),
        ('Unregistered', 'Unregistered'),
    )
    registration_type = models.CharField(max_length=20, choices=registration, default='Unregistered', blank=True)

    is_eoperator = models.CharField(max_length=3, choices=yes_no_choice, default='No', blank=True)
    deemed_expoter = models.CharField(max_length=3, choices=yes_no_choice, default='No', blank=True)

    parties = (
        ('Not Applicable', 'Not Applicable'),
        ('Deemed Export', 'Deemed Export'),
        ('Embassy/UN Body', 'Embassy/UN Body'),
        ('SEZ', 'SEZ'),
    )
    party_type = models.CharField(max_length=100, choices=parties, default='Not Applicable', blank=True)

    is_transporter = models.CharField(max_length=3, choices=yes_no_choice, default='No', blank=True)
    transporter_id = models.CharField(max_length=50, blank=True)
    hsn_desc = models.CharField(max_length=255, blank=True)
    hsn_no = models.CharField(max_length=20, blank=True)

    is_non_gst = models.CharField(max_length=3, choices=yes_no_choice, default='No', blank=True)

    transaction_types_purchase = (
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
    nature_transactions_purchase = models.CharField(max_length=100, choices=transaction_types_purchase, default='Not Applicable', blank=True)

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
        ('Interstate Sales to Embassy / UN Body- Exempt',
         'Interstate Sales to Embassy / UN Body- Exempt'),
        ('Interstate Sales to Embassy / UN Body- Nil Rated',
         'Interstate Sales to Embassy / UN Body- Nil Rated'),
        ('Interstate Sales to Embassy / UN Body- Taxable',
         'Interstate Sales to Embassy / UN Body- Taxable'),
        ('Intrastate Deemed Exports Exempt',
         'Intrastate Deemed Exports Exempt'),
        ('Intrastate Deemed Exports Nil Rated',
         'Intrastate Deemed Exports Nil Rated'),
        ('Intrastate Deemed Exports Taxable',
         'Intrastate Deemed Exports Taxable'),
        ('Sales Exempt', 'Sales Exempt'),
        ('Sales Nil Rated', 'Sales Nil Rated'),
        ('Intrastate Sales Taxable', 'Intrastate Sales Taxable'),
        ('Sales to Consumer - Exempt', 'Sales to Consumer - Exempt'),
        ('Sales to Consumer - Nil Rated ', 'Sales to Consumer - Nil Rated'),
        ('Sales to Consumer - Taxable', 'Sales to Consumer - Taxable'),
        ('Sales to SEZ - Exempt', 'Sales to SEZ - Exempt'),
        ('Sales to SEZ - LUT/Bond', 'Sales to SEZ - LUT/Bond'),
        ('Sales to SEZ - Nil Rated', 'Sales to SEZ - Nil Rated'),
        ('Sales to SEZ - Taxable', 'Sales to SEZ - Taxable'),
    )
    nature_transactions_sales = models.CharField(max_length=100, choices=transaction_types_sales, default='Not Applicable', blank=True)

    gd_nature = (
        ('Not Applicable', 'Not Applicable'),
        ('Capital Goods', 'Capital Goods'),
    )
    goods_nature = models.CharField(max_length=20, choices=gd_nature, default='Not Applicable', blank=True)

    tax_category = (
        ('Unknown', 'Unknown'),
        ('Exempt', 'Exempt'),
        ('Nil Rated', 'Nil Rated'),
        ('Taxable', 'Taxable'),
    )
    taxability = models.CharField(max_length=20, choices=tax_category, default='Unknown', blank=True)

    integrated_tax = models.DecimalField(default=0.00, max_digits=20, decimal_places=2, blank=True)
    central_tax = models.DecimalField(default=0.00, max_digits=20, decimal_places=2, blank=True)
    state_tax = models.DecimalField(default=0.00, max_digits=20, decimal_places=2, blank=True)
    cess = models.DecimalField(default=0.00, max_digits=20, decimal_places=2, blank=True)

    def __str__(self):
        return self.ledger_name

    def clean(self):
        state_req_groups = ['Sundry Debtors', 'Sundry Creditors', 'Cash-in-Hand', 'Bank Accounts', 'Bank OD A/c']

        if not self.state and self.ledger_group.group_base.name in state_req_groups:
            raise ValidationError({'state': ["State name is compulsory for the selected ledger type"]})

    class Meta:
        ordering = ['ledger_name']
        unique_together = ['company', 'ledger_name']

    def get_absolute_url(self, **kwargs):
        """
        Get the absolute URL
        """
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        period_selected = get_object_or_404(PeriodSelected, pk=kwargs['period_pk'])
        return reverse("accounting_entry:ledgerdetail", kwargs={'ledger_master_pk': self.pk, 'company_pk': company.pk, 'period_pk': period_selected.pk})

    def save(self, *args, **kwargs):
        if self.country != 'India':
            self.state.state_name = "Other Territory"
        if not self.url_hash:
            if self.user.profile.user_type == 'Bussiness User':
                self.url_hash = 'BU' + '-' + str(self.user.id) + '-' + 'P' + '-' + '1' + '-' + 'C' + str(
                    self.company.counter) + '-' + ('AL') + str(self.counter)
            else:
                self.url_hash = 'PU' + '-' + str(self.user.id) + '-' + 'P' + '-' + '1' + '-' + 'C' + str(
                    self.company.counter) + '-' + ('AL') + str(self.counter)

        super(LedgerMaster, self).save(*args, **kwargs)


class JournalVoucher(models.Model):
    """
    Journal Voucher
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_journal_voucher')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_journal_voucher')
    counter = models.IntegerField()
    url_hash = models.CharField(max_length=100)
    voucher_date = models.DateField(default=datetime.date.today)
    voucher_id = models.PositiveIntegerField(blank=True, null=True)  # ref voucher id
    voucher_type = models.CharField(default='Journal', max_length=100)
    dr_ledger = models.ForeignKey(LedgerMaster, on_delete=models.DO_NOTHING, related_name='dr_ledger_journal_voucher')
    cr_ledger = models.ForeignKey(LedgerMaster, on_delete=models.DO_NOTHING, related_name='cr_ledger_journal_voucher')
    amount = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    narration = models.TextField(blank=True)

    def __str__(self):
        return str(self.dr_ledger + " a/c Dr To " + self.cr_ledger)

    # def get_absolute_url(self):
    #     """
    #     Get the absolute url
    #     """
    #     return reverse("accounting_entry:detail", kwargs={'journal_voucher_pk': self.pk})

    def clean(self):
        if self.dr_ledger == self.cr_ledger:
            raise ValidationError(
                {
                    'dr_ledger': ['Both debit and credit ledger cannot be same'],
                    'cr_ledger': ['Both debit and credit ledger cannot be same'],
                })

    def save(self, *args, **kwargs):
        if not self.url_hash:
            if self.user.profile.user_type == 'Bussiness User':
                self.url_hash = 'BU' + '-' + str(self.user.id) + '-' + 'P' + '-' + '1' + '-' + 'C' + str(
                    self.company.counter) + '-' + ('AJ') + str(self.counter)
            else:
                self.url_hash = 'PU' + '-' + str(self.user.id) + '-' + 'P' + '-' + '1' + '-' + 'C' + str(
                    self.company.counter) + '-' + ('AJ') + str(self.counter)

        super(JournalVoucher, self).save(*args, **kwargs)


class BankReconciliation(models.Model):
    """
    Bank Reconciliation
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_bank_reconcliation')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_bank_reconciliation')
    counter = models.IntegerField()
    url_hash = models.CharField(max_length=100)
    voucher_date = models.DateField(default=datetime.date.today)
    voucher_id = models.PositiveIntegerField()
    voucher_type = models.CharField(max_length=100)
    dr_ledger = models.ForeignKey(LedgerMaster, on_delete=models.DO_NOTHING, related_name='dr_ledger_bank_reconciliation')
    cr_ledger = models.ForeignKey(LedgerMaster, on_delete=models.DO_NOTHING, related_name='cr_ledger_bank_reconciliation')
    amount = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    category = (
        ('ATM', 'ATM'),
        ('Cash', 'Cash'),
        ('Cheque/DD', 'Cheque/DD'),
        ('Card', 'Card'),
        ('ECS', 'ECS'),
        ('Electronic Cheque', 'Electronic Cheque'),
        ('Electronic DD/PO', 'Electronic DD/PO'),
        ('e-Fund Transfer', 'e-Fund Transfer'),
        ('Others', 'Others'),
    )
    transaction_type = models.CharField(
        max_length=60, choices=category, default='Cheque/DD')
    instrument_no = models.CharField(max_length=50, blank=True)
    bank_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return str(self.dr_ledger + " a/c Dr To " + self.cr_ledger)

    def clean(self):
        if self.dr_ledger == self.cr_ledger:
            raise ValidationError(
                'Both debit and credit ledger cannot be same')

    def save(self, *args, **kwargs):
        if not self.url_hash:
            if self.user.profile.user_type == 'Bussiness User':
                self.url_hash = 'BU' + '-' + str(self.user.id) + '-' + 'P' + '-' + '1' + '-' + 'C' + str(
                    self.company.counter) + '-' + ('AJ') + str(self.counter)
            else:
                self.url_hash = 'PU' + '-' + str(self.user.id) + '-' + 'P' + '-' + '1' + '-' + 'C' + str(
                    self.company.counter) + '-' + ('AJ') + str(self.counter)

        super(BankReconciliation, self).save(*args, **kwargs)


class PaymentVoucher(models.Model):
    """
    Payment Voucher
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_payment_voucher')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_payment_voucher')
    counter = models.IntegerField()
    url_hash = models.CharField(max_length=100)
    voucher_date = models.DateField(default=datetime.date.today)
    account = models.ForeignKey(LedgerMaster, on_delete=models.DO_NOTHING, related_name='ledger_payment_voucher')
    total_amt = models.DecimalField(max_digits=20, decimal_places=2)

    def __str__(self):
        return str(self.account)

    def save(self, *args, **kwargs):
        if not self.url_hash:
            if self.user.profile.user_type == 'Bussiness User':
                self.url_hash = 'BU' + '-' + str(self.user.id) + '-' + 'P' + '-' + '1' + '-' + 'C' + str(
                    self.company.counter) + '-' + ('AJ') + str(self.counter)
            else:
                self.url_hash = 'PU' + '-' + str(self.user.id) + '-' + 'P' + '-' + '1' + '-' + 'C' + str(
                    self.company.counter) + '-' + ('AJ') + str(self.counter)

        super(PaymentVoucher, self).save(*args, **kwargs)


class PaymentVoucherRows(models.Model):
    """
    Payment Voucher Rows (payments)
    """
    payment = models.ForeignKey(PaymentVoucher, on_delete=models.CASCADE, related_name='payment_payment_voucher_row')
    particular = models.ForeignKey(LedgerMaster, on_delete=models.DO_NOTHING, related_name='ledger_paryment_voucher_row')
    amount = models.DecimalField(max_digits=20, decimal_places=2)

    def __str__(self):
        return str(self.payment + " -> " + self.particular)


class ReceiptVoucher(models.Model):
    """
    Receipt Voucher
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_receipt_voucher')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_receipt_voucher')
    counter = models.IntegerField()
    url_hash = models.CharField(max_length=100)
    voucher_date = models.DateField(default=datetime.date.today)
    account = models.ForeignKey(LedgerMaster, on_delete=models.DO_NOTHING, related_name='ledger_receipt_voucher')
    total_amt = models.DecimalField(max_digits=20, decimal_places=2)

    def __str__(self):
        return str(self.account)

    def save(self, *args, **kwargs):
        if not self.url_hash:
            if self.user.profile.user_type == 'Bussiness User':
                self.url_hash = 'BU' + '-' + str(self.user.id) + '-' + 'P' + '-' + '1' + '-' + 'C' + str(
                    self.company.counter) + '-' + ('AJ') + str(self.counter)
            else:
                self.url_hash = 'PU' + '-' + str(self.user.id) + '-' + 'P' + '-' + '1' + '-' + 'C' + str(
                    self.company.counter) + '-' + ('AJ') + str(self.counter)

        super(ReceiptVoucher, self).save(*args, **kwargs)


class ReceiptVoucherRows(models.Model):
    """
    Receipt Voucher Rows (receipts)
    """
    receipt = models.ForeignKey(ReceiptVoucher, on_delete=models.CASCADE, related_name='receipt_receipt_voucher_row')
    particular = models.ForeignKey(LedgerMaster, on_delete=models.CASCADE, related_name='ledger_receipt_voucher_row')
    amount = models.DecimalField(max_digits=20, decimal_places=2)

    def __str__(self):
        return str(self.receipt + " -> " + self.particular)


class ContraVoucher(models.Model):
    """
    Contra Voucher
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_contra_voucher')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_contra_voucher')
    counter = models.IntegerField()
    url_hash = models.CharField(max_length=100)
    voucher_date = models.DateField(default=datetime.date.today)
    account = models.ForeignKey(LedgerMaster, on_delete=models.DO_NOTHING, related_name='ledger_contra_voucher')
    total_amt = models.DecimalField(max_digits=20, decimal_places=2)

    def __str__(self):
        return str(self.account)

    def save(self, *args, **kwargs):
        if not self.url_hash:
            if self.user.profile.user_type == 'Bussiness User':
                self.url_hash = 'BU' + '-' + str(self.user.id) + '-' + 'P' + '-' + '1' + '-' + 'C' + str(
                    self.company.counter) + '-' + ('AJ') + str(self.counter)
            else:
                self.url_hash = 'PU' + '-' + str(self.user.id) + '-' + 'P' + '-' + '1' + '-' + 'C' + str(
                    self.company.counter) + '-' + ('AJ') + str(self.counter)

        super(ContraVoucher, self).save(*args, **kwargs)


class ContraVoucherRows(models.Model):
    """
    Contra Voucher Rows
    """
    contra = models.ForeignKey(ContraVoucher, on_delete=models.CASCADE, related_name='contra_contra_voucher_row')
    particular = models.ForeignKey(LedgerMaster, on_delete=models.DO_NOTHING, related_name='ledger_contra_voucher_row')
    amount = models.DecimalField(max_digits=20, decimal_places=2)

    def __str__(self):
        return str(self.contra + " -> " + self.particular)


class MultiJournalVoucher(models.Model):
    """
    Multi-Journal Voucher
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_multi_journal_voucher')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_multi_journal_voucher')
    voucher_date = models.DateField(default=datetime.date.today)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    narration = models.TextField(blank=True)

    def __str__(self):
        return str(self.pk)

    def get_absolute_url(self, **kwargs):
        """
        Get the absolute url
        """
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        period = get_object_or_404(PeriodSelected, pk=kwargs['period_pk'])
        return reverse("accounting_entry:multijournaldetail", kwargs={'multi_journal_voucher_pk': self.pk, 'company_pk': company.pk, 'period_pk': period.pk})


class MultiJournalVoucherDrRows(models.Model):
    """
    Multi-Journal Voucher Debit Rows
    """
    multi_journal = models.ForeignKey(MultiJournalVoucher, on_delete=models.CASCADE, related_name='multi_journal_voucher_dr_rows')
    ledger = models.ForeignKey(LedgerMaster, on_delete=models.DO_NOTHING, related_name='ledger_multi_journal_voucher_dr_rows')
    amount = models.DecimalField(max_digits=20, decimal_places=2)

    def __str__(self):
        return str(self.multi_journal + " -> " + self.ledger)


class MultiJournalVoucherCrRows(models.Model):
    """
    Multi-Journal Voucher Credit Rows
    """
    multi_journal = models.ForeignKey(MultiJournalVoucher, on_delete=models.CASCADE, related_name='multi_journal_voucher_cr_rows')
    ledger = models.ForeignKey(LedgerMaster, on_delete=models.DO_NOTHING, related_name='ledger_multi_journal_voucher_cr_rows')
    amount = models.DecimalField(max_digits=20, decimal_places=2)

    def __str__(self):
        return str(self.multi_journal + " -> " + self.ledger)
