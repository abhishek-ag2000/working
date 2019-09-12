"""
Signals for Purchase
"""
from django.db.models import Value, Sum
from django.db.models.signals import pre_save, post_save, pre_delete, post_delete
from django.db.models.functions import Coalesce
from django.dispatch import receiver
from accounting_entry.models import JournalVoucher
from accounting_entry.decorators import prevent_signal_call_on_bulk_load
from .models import StockItem
from .models_purchase import PurchaseVoucher, PurchaseTerm, PurchaseTax


# @receiver(pre_save, sender=PurchaseVoucher)
# @prevent_signal_call_on_bulk_load
# def update_subtotal(sender, instance, *args, **kwargs):
#     """
#     Signal to calculate the sub total of every goods in a particular voucher
#     """
#     total_stock = instance.purchase_voucher_stock.aggregate(
#         the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']

#     if total_stock:
#         instance.sub_total = total_stock


# @receiver(pre_save, sender=PurchaseVoucher)
# @prevent_signal_call_on_bulk_load
# def update_totalgst(sender, instance, *args, **kwargs):
#     """
#     Signal to calculate the GST totals of a particular voucher
#     """
#     total_cgst_stock = instance.purchase_voucher_stock.aggregate(
#         the_sum=Coalesce(Sum('cgst_total'), Value(0)))['the_sum']
#     total_sgst_stock = instance.purchase_voucher_stock.aggregate(
#         the_sum=Coalesce(Sum('sgst_total'), Value(0)))['the_sum']
#     total_igst_stock = instance.purchase_voucher_stock.aggregate(
#         the_sum=Coalesce(Sum('igst_total'), Value(0)))['the_sum']

#     total_cgst_extra = instance.purchase_voucher_term.aggregate(
#         the_sum=Coalesce(Sum('cgst_total'), Value(0)))['the_sum']
#     total_sgst_extra = instance.purchase_voucher_term.aggregate(
#         the_sum=Coalesce(Sum('sgst_total'), Value(0)))['the_sum']
#     total_igst_extra = instance.purchase_voucher_term.aggregate(
#         the_sum=Coalesce(Sum('igst_total'), Value(0)))['the_sum']

#     if total_cgst_stock or total_cgst_extra:
#         instance.cgst_total = total_cgst_stock + total_cgst_extra
#     if total_sgst_stock or total_sgst_extra:
#         instance.sgst_total = total_sgst_stock + total_sgst_extra
#     if total_igst_stock or total_igst_extra:
#         instance.igst_total = total_igst_stock + total_igst_extra


@receiver(pre_save, sender=PurchaseVoucher)
@prevent_signal_call_on_bulk_load
def update_total_tax(sender, instance, *args, **kwargs):
    """
    Signal to calculate the Tax totals of a particular voucher in case of Composite billing
    """
    total_tax_stock = instance.purchase_voucher_stock.aggregate(
        the_sum=Coalesce(Sum('tax_total'), Value(0)))['the_sum']

    total_tax_extra = instance.purchase_voucher_term.aggregate(
        the_sum=Coalesce(Sum('tax_total'), Value(0)))['the_sum']

    if total_tax_stock or total_tax_extra:
        instance.tax_total = total_tax_stock + total_tax_extra


# @receiver(pre_save, sender=PurchaseVoucher)
# @prevent_signal_call_on_bulk_load
# def update_purchase_grand_total(sender, instance, *args, **kwargs):
#     """
#     Signal to calculate the Grand Total of a particular voucher
#     """
    


@receiver(post_save, sender=PurchaseVoucher)
@prevent_signal_call_on_bulk_load
def user_created(sender, instance, created, **kwargs):
    """
    Signal to create a journal entry whenever a voucher is submitted.
    """
    c = JournalVoucher.objects.filter(
        user=instance.user, company=instance.company).count() + 1
    if instance.sub_total != 0:
        JournalVoucher.objects.update_or_create(
            voucher_id=instance.id,
            voucher_type="PurchaseVoucher",
            url_hash=instance.url_hash,
            defaults={
                'counter': c,
                'user': instance.user,
                'company': instance.company,
                'voucher_date': instance.voucher_date,
                'cr_ledger': instance.party_ac,
                'dr_ledger': instance.doc_ledger,
                'amount': instance.sub_total}
        )


@receiver(post_save, sender=PurchaseTerm)
@prevent_signal_call_on_bulk_load
def user_created_purchase_extra_charge(sender, instance, created, **kwargs):
    """
    Signals to create a journal entry for the additional charges Ledger in a particular entry
    """
    c = JournalVoucher.objects.filter(
        user=instance.purchase_voucher.user, company=instance.purchase_voucher.company).count() + 1
    if instance.total != 0:
        JournalVoucher.objects.update_or_create(
            voucher_id=instance.id,
            voucher_type="Charges_against_Purchase",
            defaults={
                'counter': c,
                'user': instance.purchase_voucher.user,
                'company': instance.purchase_voucher.company,
                'voucher_date': instance.purchase_voucher.voucher_date,
                'cr_ledger': instance.purchase_voucher.party_ac,
                'dr_ledger': instance.ledger,
                'amount': instance.total}
        )


@receiver(post_save, sender=PurchaseTax)
@prevent_signal_call_on_bulk_load
def user_created_purchase_gst_charge(sender, instance, created, **kwargs):
    """
    Signal to create a jounal entry for the GST ledgers in a particular voucher
    """
    c = JournalVoucher.objects.filter(
        user=instance.purchase_voucher.user, company=instance.purchase_voucher.company).count() + 1
    if instance.ledger:
        JournalVoucher.objects.update_or_create(
            voucher_id=instance.id,
            voucher_type="Tax_against_Purchase",
            defaults={
                'counter': c,
                'user': instance.purchase_voucher.user,
                'company': instance.purchase_voucher.company,
                'voucher_date': instance.purchase_voucher.voucher_date,
                'cr_ledger': instance.purchase_voucher.party_ac,
                'dr_ledger': instance.ledger,
                'amount': instance.total}
        )


@receiver(pre_delete, sender=PurchaseVoucher)
def delete_journal_voucher_against_terms_purchases(sender, instance, **kwargs):
    """
    Signal to delete a journal entry whenever a additional ledger is deleted from a voucher
    """
    purchase_voucher_term = PurchaseTerm.objects.filter(purchase_voucher=instance)
    for s in purchase_voucher_term:
        s.save()
        JournalVoucher.objects.filter(
            company=s.purchase_voucher.company, voucher_id=s.id).delete()


@receiver(pre_delete, sender=PurchaseVoucher)
def delete_journal_voucher_against_tax_purchases(sender, instance, **kwargs):
    """
    Signal to delete a journal entry whenever a GST ledger is removed from a particular voucher
    """
    purchase_voucher_tax = PurchaseTax.objects.filter(
        purchase_voucher=instance)
    for s in purchase_voucher_tax:
        s.save()
        JournalVoucher.objects.filter(
            company=s.purchase_voucher.company, voucher_id=s.id).delete()


@receiver(pre_delete, sender=PurchaseVoucher)
def delete_related_journal(sender, instance, **kwargs):
    """
    Signal to delete a jounal entry whenever a purchase entry is deleted
    """
    JournalVoucher.objects.filter(
        user=instance.user, company=instance.company, voucher_id=instance.id).delete()


# @receiver(pre_delete, sender=PurchaseVoucher)
# def delete_related_party_ledger_purchase(sender, instance, **kwargs):
#     instance.party_ac.save()
#     instance.party_ac.ledger_group.save()


# @receiver(pre_delete, sender=PurchaseVoucher)
# def delete_related_purchase_ledger(sender, instance, **kwargs):
#     instance.doc_ledger.save()
#     instance.doc_ledger.ledger_group.save()


# @receiver(post_delete, sender=PurchaseVoucher)
# def delete_related_stock_for_purchase(sender, instance, *args, **kwargs):
#     purchase_stock = StockItem.objects.filter(company=instance.company)
#     for obj in purchase_stock:
#         obj.save()
