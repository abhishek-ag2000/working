from django.db.models import Value, Sum
from django.db.models.signals import pre_save, post_save, pre_delete, post_delete
from django.db.models.functions import Coalesce
from django.dispatch import receiver
from accounting_entry.models import JournalVoucher
from accounting_entry.decorators import prevent_signal_call_on_bulk_load
from .models import StockItem
from .models_sale import SaleVoucher, SaleTerm, SaleTax


@receiver(pre_save, sender=SaleVoucher)
@prevent_signal_call_on_bulk_load
def update_total_tax_sales(sender, instance, *args, **kwargs):
    """
    Signal to calculate the Tax totals of a particular voucher in case of Composite billing
    """
    total_tax_stock = instance.sale_voucher_stock.aggregate(
        the_sum=Coalesce(Sum('tax_total'), Value(0)))['the_sum']

    total_tax_term = instance.sale_voucher_term.aggregate(
        the_sum=Coalesce(Sum('tax_total'), Value(0)))['the_sum']

    if total_tax_stock or total_tax_term:
        instance.tax_total = total_tax_stock + total_tax_term


@receiver(pre_save, sender=SaleVoucher)
@prevent_signal_call_on_bulk_load
def update_total_sales(sender, instance, *args, **kwargs):
    """
    Signal to calculate the sub total of every goods in a particular voucher
    """
    total_goods = instance.sale_voucher_stock.aggregate(
        the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']
    if total_goods:
        instance.sub_total = total_goods


@receiver(pre_save, sender=SaleVoucher)
@prevent_signal_call_on_bulk_load
def update_totalgst_sales(sender, instance, *args, **kwargs):
    """
    Signal to calculate the GST totals of a particular voucher
    """
    total_cgst_stock = instance.sale_voucher_stock.aggregate(
        the_sum=Coalesce(Sum('cgst_total'), Value(0)))['the_sum']
    total_sgst_stock = instance.sale_voucher_stock.aggregate(
        the_sum=Coalesce(Sum('sgst_total'), Value(0)))['the_sum']
    total_igst_stock = instance.sale_voucher_stock.aggregate(
        the_sum=Coalesce(Sum('igst_total'), Value(0)))['the_sum']

    total_cgst_extra = instance.sale_voucher_term.aggregate(
        the_sum=Coalesce(Sum('cgst_total'), Value(0)))['the_sum']
    total_sgst_extra = instance.sale_voucher_term.aggregate(
        the_sum=Coalesce(Sum('sgst_total'), Value(0)))['the_sum']
    total_igst_extra = instance.sale_voucher_term.aggregate(
        the_sum=Coalesce(Sum('igst_total'), Value(0)))['the_sum']

    if total_cgst_extra or total_cgst_stock:
        instance.cgst_total = total_cgst_stock + total_cgst_extra
    if total_sgst_extra or total_sgst_stock:
        instance.sgst_total = total_sgst_stock + total_sgst_extra
    if total_igst_stock or total_igst_extra:
        instance.igst_total = total_igst_stock + total_igst_extra


# @receiver(pre_save, sender=SaleVoucher)
# @prevent_signal_call_on_bulk_load
# def update_sales_grand_total(sender, instance, *args, **kwargs):
#     """
#     Signal to calculate the Grand total of a particular voucher
#     """



@receiver(post_save, sender=SaleVoucher)
@prevent_signal_call_on_bulk_load
def user_created_sales(sender, instance, created, **kwargs):
    """
    Signal to create a journal entry whenever a voucher is submitted.
    """
    c = JournalVoucher.objects.filter(
        user=instance.user, company=instance.company).count() + 1
    JournalVoucher.objects.update_or_create(
        voucher_id=instance.id,
        voucher_type="Sales",
        url_hash=instance.url_hash,
        defaults={
            'counter': c,
            'user': instance.user,
            'company': instance.company,
            'voucher_date': instance.voucher_date,
            'dr_ledger': instance.party_ac,
            'cr_ledger': instance.doc_ledger,
            'amount': instance.sub_total}
    )


@receiver(post_save, sender=SaleTerm)
@prevent_signal_call_on_bulk_load
def user_created_sales_extra_charge(sender, instance, created, **kwargs):
    """
    Signals to create a journal entry for the additional charges Ledger in a particular entry
    """
    c = JournalVoucher.objects.filter(user=instance.sale_voucher.user, company=instance.sale_voucher.company).count() + 1
    if instance.ledger:
        JournalVoucher.objects.update_or_create(
            voucher_id=instance.id,
            voucher_type="Charges_against_Sales",
            defaults={
                'counter': c,
                'user': instance.sale_voucher.user,
                'company': instance.sale_voucher.company,
                'voucher_date': instance.sale_voucher.voucher_date,
                'dr_ledger': instance.sale_voucher.party_ac,
                'cr_ledger': instance.ledger,
                'amount': instance.total}
        )


@receiver(post_save, sender=SaleTax)
@prevent_signal_call_on_bulk_load
def user_created_sales_gst_charge(sender, instance, created, **kwargs):
    """
    Signal to create a jounal entry for the GST ledgers in a particular voucher
    """
    c = JournalVoucher.objects.filter(
        user=instance.sale_voucher.user, company=instance.sale_voucher.company).count() + 1
    if instance.ledger != None:
        JournalVoucher.objects.update_or_create(
            voucher_id=instance.id,
            voucher_type="Tax_aganist_sales",
            defaults={
                'counter': c,
                'user': instance.sale_voucher.user,
                'company': instance.sale_voucher.company,
                'voucher_date': instance.sale_voucher.voucher_date,
                'dr_ledger': instance.sale_voucher.party_ac,
                'cr_ledger': instance.ledger,
                'amount': instance.total}
        )


@receiver(pre_delete, sender=SaleVoucher)
def delete_journal_voucher_against_terms_sales(sender, instance, **kwargs):
    """
    Signal to delete a journal entry whenever a additional ledger is deleted from a voucher
    """
    sale_voucher_term = SaleTerm.objects.filter(sale_voucher=instance)
    for s in sale_voucher_term:
        s.save()
        JournalVoucher.objects.filter(
            company=s.sale_voucher.company, voucher_id=s.id).delete()


@receiver(pre_delete, sender=SaleVoucher)
def delete_journal_voucher_against_tax_sales(sender, instance, **kwargs):
    """
    Signal to delete a journal entry whenever a GST ledger is removed from a particular voucher
    """
    sales_tax = SaleTax.objects.filter(sale_voucher=instance)
    for s in sales_tax:
        s.save()
        JournalVoucher.objects.filter(
            company=s.sale_voucher.company, voucher_id=s.id).delete()


@receiver(pre_delete, sender=SaleVoucher)
def delete_journal_voucher_against_voucher_sales(sender, instance, **kwargs):
    """
    Signal to delete a jounal entry whenever a purchase entry is deleted
    """
    JournalVoucher.objects.filter(
        user=instance.user, company=instance.company, voucher_id=instance.id).delete()


@receiver(pre_delete, sender=SaleVoucher)
def delete_related_party_ledger_sales(sender, instance, **kwargs):
    instance.party_ac.save()
    instance.party_ac.ledger_group.save()


@receiver(pre_delete, sender=SaleVoucher)
def delete_related_sales_ledger(sender, instance, **kwargs):
    instance.doc_ledger.save()
    instance.doc_ledger.ledger_group.save()


@receiver(post_delete, sender=SaleVoucher)
def delete_related_stock_for_sales(sender, instance, *args, **kwargs):
    sales_stock = StockItem.objects.filter(company=instance.company)
    for obj in sales_stock:
        obj.save()
