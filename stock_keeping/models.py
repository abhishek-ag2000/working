"""
Models
"""
import datetime
from sorl.thumbnail import ImageField
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from bracketline.models import UQC
from company.models import Company
from accounting_entry.decorators import prevent_signal_call_on_bulk_load


class StockGroup(models.Model):
    """
    Stock Group Model
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_group')
    counter = models.IntegerField()
    url_hash = models.CharField(max_length=100)
    group_name = models.CharField(max_length=132)
    self_group = models.ForeignKey("self", on_delete=models.DO_NOTHING, related_name='stock_group', null=True)
    boolean_types = (
        ('Yes', 'Yes'),
        ('No', 'No')
    )
    set_or_alter_gst = models.CharField(max_length=3, choices=boolean_types, default='No')
    hsn = models.CharField(max_length=8, null=True, blank=True)
    is_non_gst = models.CharField(max_length=100, choices=boolean_types, default='No')
    tax_cat = (
        ('Unknown', 'Unknown'),
        ('Exempt', 'Exempt'),
        ('Nil Rated', 'Nil Rated'),
        ('Taxable', 'Taxable'),
    )
    taxability = models.CharField(max_length=100, choices=tax_cat, default='Unknown')
    reverse_charge = models.CharField(max_length=100, choices=boolean_types, default='No')
    input_credit = models.CharField(max_length=100, choices=boolean_types, default='No')
    integrated_tax = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    central_tax = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    state_tax = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    cess = models.DecimalField(default=0, max_digits=20, decimal_places=2)

    def __str__(self):
        return self.group_name

    def save(self, **kwargs):
        if not self.url_hash:
            if self.user.profile.user_type == 'Bussiness user':
                self.url_hash = 'BU' + '-' + str(self.user.id) + '-' + 'P' + '-' + '1' + '-' + 'C' + str(
                    self.company.counter) + '-' + ('SSG') + str(self.counter)
            else:
                self.url_hash = 'PU' + '-' + str(self.user.id) + '-' + 'P' + '-' + '1' + '-' + 'C' + str(
                    self.company.counter) + '-' + ('SSG') + str(self.counter)
        super(StockGroup, self).save()


@receiver(post_save, sender=Company)
@prevent_signal_call_on_bulk_load
def user_created_stockgroup(sender, instance, created, **kwargs):
    c = StockGroup.objects.filter(user=instance.user, company=instance).count() + 1
    if created:
        StockGroup.objects.create(
            counter=c, user=instance.user, company=instance, group_name='Primary')


class SimpleUnit(models.Model):
    """
    Simple Unit Model
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    counter = models.IntegerField()
    url_hash = models.CharField(max_length=100)
    symbol = models.CharField(max_length=32)
    formal = models.CharField(max_length=32)
    uqc = models.ForeignKey(UQC, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.symbol

    def save(self, **kwargs):
        if not self.url_hash:
            if self.user.profile.user_type == 'Bussiness user':
                self.url_hash = 'BU' + '-' + str(self.user.id) + '-' + 'P' + '-' + '1' + '-' + 'C' + str(
                    self.company.counter) + '-' + ('SSU') + str(self.counter)
            else:
                self.url_hash = 'PU' + '-' + str(self.user.id) + '-' + 'P' + '-' + '1' + '-' + 'C' + str(
                    self.company.counter) + '-' + ('SSU') + str(self.counter)
        super(SimpleUnit, self).save()


class CompoundUnit(models.Model):
    """
    Compound Unit Model
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_compound_unit')
    counter = models.IntegerField(blank=True, null=True)
    url_hash = models.CharField(max_length=100, null=True, blank=True)
    first_unit = models.ForeignKey(SimpleUnit, on_delete=models.CASCADE, related_name='firsts')
    conversion = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    seconds_unit = models.ForeignKey(SimpleUnit, on_delete=models.CASCADE, related_name='seconds')

    def __str__(self):
        return str(self.first_unit) + '  of  ' + str(self.seconds_unit)

    def clean(self):
        if self.first_unit == self.seconds_unit:
            raise ValidationError({'seconds_unit': ["First Unit Should Not Be Equal To Second Unit!"], 'first_unit': [
                                  "First Unit Should Not Be Equal To Second Unit!"]})

    def save(self, **kwargs):
        if not self.url_hash:
            if self.user.profile.user_type == 'Bussiness user':
                self.url_hash = 'BU' + '-' + str(self.user.id) + '-' + 'P' + '-' + '1' + '-' + 'C' + str(
                    self.company.counter) + '-' + ('SCU') + str(self.counter)
            else:
                self.url_hash = 'PU' + '-' + str(self.user.id) + '-' + 'P' + '-' + '1' + '-' + 'C' + str(
                    self.company.counter) + '-' + ('SCU') + str(self.counter)
        super(CompoundUnit, self).save()


class StockItem(models.Model):
    """
    Stock Item Model
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_stock_items')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_stock_items')
    counter = models.IntegerField()
    url_hash = models.CharField(max_length=100)
    quantity = models.DecimalField(max_digits=20, decimal_places=3, default=0.000)
    rate = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    opening = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    stock_name = models.CharField(max_length=32)
    batch_no = models.PositiveIntegerField(blank=True, null=True)
    barcode_image = ImageField(upload_to='stockmanagement', null=True, blank=True)
    barcode_text = models.CharField(max_length=50, blank=True)
    mfd_date = models.DateField(blank=True, null=True)
    exp_date = models.DateField(blank=True, null=True)
    stock_group = models.ForeignKey(StockGroup, on_delete=models.DO_NOTHING, related_name='stock_item_group')
    simple_unit = models.ForeignKey(SimpleUnit, on_delete=models.DO_NOTHING, related_name='stock_item_simple_unit')
    compound_unit = models.ForeignKey(CompoundUnit, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='stock_item_compound_unit')
    boolean_types = (
        ('Yes', 'Yes'),
        ('No', 'No')
    )
    is_gst = models.CharField(max_length=3, choices=boolean_types, default='No')
    set_or_alter_gst = models.CharField(max_length=3, choices=boolean_types, default='No')
    hsn = models.CharField(max_length=8, null=True, blank=True)

    is_non_gst = models.CharField(max_length=3, choices=boolean_types, default='No')
    tax_cat = (
        ('Unknown', 'Unknown'),
        ('Exempt', 'Exempt'),
        ('Nil Rated', 'Nil Rated'),
        ('Taxable', 'Taxable'),
    )
    taxability = models.CharField(max_length=20, choices=tax_cat, default='Unknown')
    reverse_charge = models.CharField(max_length=3, choices=boolean_types, default='No')
    input_credit = models.CharField(max_length=3, choices=boolean_types, default='No')
    integrated_tax = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    central_tax = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    state_tax = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    cess = models.DecimalField(default=0, max_digits=20, decimal_places=2)

    def __str__(self):
        return self.stock_name

    def clean(self):
        if self.simple_unit and self.compound_unit:
            raise ValidationError({'compound_unit': ["You are not supposed to select both units!"], 'simple_unit': [
                                  "You are not supposed to select both units!"]})

    def save(self, *args, **kwargs):
        """
        Overwrite save to update hsn, opening balance, all taxes and url_hash
        """
        if self.stock_group.hsn:
            self.hsn = self.stock_group.hsn
        if self.stock_group.taxability != 'Unknown':
            self.taxability = self.stock_group.taxability
        if self.stock_group.integrated_tax != 0:
            self.integrated_tax = self.stock_group.integrated_tax
        if self.stock_group.central_tax != 0:
            self.central_tax = self.stock_group.central_tax
        if self.stock_group.state_tax != 0:
            self.state_tax = self.stock_group.state_tax
        if self.stock_group.cess != 0:
            self.cess = self.stock_group.cess
        if self.quantity or self.rate:
            self.opening = self.quantity * self.rate

        if not self.url_hash:
            if self.user.profile.user_type == 'Bussiness user':
                self.url_hash = 'BU' + '-' + str(self.user.id) + '-' + 'P' + '-' + '1' + '-' + 'C' + str(
                    self.company.counter) + '-' + ('SSD') + str(self.counter)
            else:
                self.url_hash = 'PU' + '-' + str(self.user.id) + '-' + 'P' + '-' + '1' + '-' + 'C' + str(
                    self.company.counter) + '-' + ('SSD') + str(self.counter)
        super(StockItem, self).save(*args, **kwargs)


class StockBalance(models.Model):
    """
    Stock Balance Model
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_stock_journal')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_stock_journal')
    date = models.DateField(default=datetime.date.today)
    stock_item = models.OneToOneField(StockItem, on_delete=models.CASCADE, related_name='stock_item_stock_journal')
    opening_stock = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    closing_quantity = models.DecimalField(max_digits=20, decimal_places=3, default=0.000)
    closing_stock = models.DecimalField(max_digits=20, decimal_places=2, null=True)

    def __str__(self):
        return str(self.stock_item)


@receiver(post_save, sender=StockItem)
@prevent_signal_call_on_bulk_load
def create_default_stock_ledger(sender, instance, created, **kwargs):
    if created:
        StockBalance.objects.create(user=instance.user, company=instance.company, stock_item=instance)
