"""
Signals for Purchase
"""
from django.db.models import Value, Sum
from django.db.models.signals import pre_save, post_save, pre_delete, post_delete
from django.db.models.functions import Coalesce
from django.dispatch import receiver
from accounting_entry.models import JournalVoucher
from accounting_entry.decorators import prevent_signal_call_on_bulk_load
from .model_purchase_accounts import PurchaseVoucherAccounts, PurchaseTermAccounts, PurchaseTaxAccounts


# @receiver(pre_save, sender=PurchaseVoucherAccounts)
# @prevent_signal_call_on_bulk_load
# def update_subtotal(sender, instance, *args, **kwargs):
#     """
#     Signal to calculate the sub total of every goods in a particular voucher
#     """
#     total_ledger = instance.purchase_voucher_term_accounts.aggregate(
#         the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']

#     if total_ledger:
#         instance.sub_total = total_ledger


# @receiver(pre_save, sender=PurchaseVoucherAccounts)
# @prevent_signal_call_on_bulk_load
# def update_totalgst_accounts(sender, instance, *args, **kwargs):
#     """
#     Signal to calculate the GST totals of a particular voucher
#     """

#     total_cgst_extra = instance.purchase_voucher_term_accounts.aggregate(
#         the_sum=Coalesce(Sum('cgst_total'), Value(0)))['the_sum']
#     total_sgst_extra = instance.purchase_voucher_term_accounts.aggregate(
#         the_sum=Coalesce(Sum('sgst_total'), Value(0)))['the_sum']
#     total_igst_extra = instance.purchase_voucher_term_accounts.aggregate(
#         the_sum=Coalesce(Sum('igst_total'), Value(0)))['the_sum']

#     if total_cgst_extra:
#         instance.cgst_total = total_cgst_extra
#     if total_sgst_extra:
#         instance.sgst_total = total_sgst_extra
#     if total_igst_extra:
#         instance.igst_total = total_igst_extra


@receiver(pre_save, sender=PurchaseVoucherAccounts)
@prevent_signal_call_on_bulk_load
def update_total_tax_accounts(sender, instance, *args, **kwargs):
    """
    Signal to calculate the Tax totals of a particular voucher in case of Composite billing
    """

    total_tax_extra = instance.purchase_voucher_term_accounts.aggregate(
        the_sum=Coalesce(Sum('tax_total'), Value(0)))['the_sum']

    if total_tax_extra:
        instance.tax_total = total_tax_extra


# @receiver(pre_save, sender=PurchaseVoucherAccounts)
# @prevent_signal_call_on_bulk_load
# def update_purchase_grand_total(sender, instance, *args, **kwargs):
#     """
#     Signal to calculate the Grand Total of a particular voucher
#     """
    


@receiver(post_save, sender=PurchaseTermAccounts)
@prevent_signal_call_on_bulk_load
def user_created_purchase_accounts_journal_accounts(sender, instance, created, **kwargs):
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


@receiver(post_save, sender=PurchaseTaxAccounts)
@prevent_signal_call_on_bulk_load
def user_created_purchase_gst_charge_accounts(sender, instance, created, **kwargs):
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


@receiver(pre_delete, sender=PurchaseVoucherAccounts)
def delete_journal_voucher_against_terms_purchases_accounts(sender, instance, **kwargs):
    """
    Signal to delete a journal entry whenever a additional ledger is deleted from a voucher
    """
    purchase_voucher_term = PurchaseTermAccounts.objects.filter(purchase_voucher=instance)
    for s in purchase_voucher_term:
        s.save()
        JournalVoucher.objects.filter(
            company=s.purchase_voucher.company, voucher_id=s.id).delete()


@receiver(pre_delete, sender=PurchaseVoucherAccounts)
def delete_journal_voucher_against_tax_purchases_accounts(sender, instance, **kwargs):
    """
    Signal to delete a journal entry whenever a GST ledger is removed from a particular voucher
    """
    purchase_voucher_tax = PurchaseTaxAccounts.objects.filter(
        purchase_voucher=instance)
    for s in purchase_voucher_tax:
        s.save()
        JournalVoucher.objects.filter(
            company=s.purchase_voucher.company, voucher_id=s.id).delete()


@receiver(pre_delete, sender=PurchaseVoucherAccounts)
def delete_related_journal_accounts(sender, instance, **kwargs):
    """
    Signal to delete a jounal entry whenever a purchase entry is deleted
    """
    JournalVoucher.objects.filter(
        user=instance.user, company=instance.company, voucher_id=instance.id).delete()


@receiver(pre_delete, sender=PurchaseVoucherAccounts)
def delete_related_party_ledger_purchase_accounts(sender, instance, **kwargs):
    instance.party_ac.save()
    instance.party_ac.ledger_group.save()

