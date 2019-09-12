from django.db.models import Value, Sum
from django.db.models.signals import pre_save, post_save, pre_delete, post_delete
from django.db.models.functions import Coalesce
from django.dispatch import receiver
from accounting_entry.models import JournalVoucher
from accounting_entry.decorators import prevent_signal_call_on_bulk_load
from .models_sale_accounts import SaleVoucherAccounts, SaleTermAccounts, SaleTaxAccounts


@receiver(pre_save, sender=SaleVoucherAccounts)
@prevent_signal_call_on_bulk_load
def update_total_tax_sales(sender, instance, *args, **kwargs):
    """
    Signal to calculate the Tax totals of a particular voucher in case of Composite billing
    """

    total_tax_term = instance.sale_voucher_term_accounts.aggregate(
        the_sum=Coalesce(Sum('tax_total'), Value(0)))['the_sum']

    if total_tax_term:
        instance.tax_total = total_tax_term


# @receiver(pre_save, sender=SaleVoucherAccounts)
# @prevent_signal_call_on_bulk_load
# def update_total_sales(sender, instance, *args, **kwargs):
#     """
#     Signal to calculate the sub total of every goods in a particular voucher
#     """
#     total_service = instance.sale_voucher_term_accounts.aggregate(
#         the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']
#     if total_service:
#         instance.sub_total = total_service


# @receiver(pre_save, sender=SaleVoucherAccounts)
# @prevent_signal_call_on_bulk_load
# def update_totalgst_sales(sender, instance, *args, **kwargs):
#     """
#     Signal to calculate the GST totals of a particular voucher
#     """

#     total_cgst_extra = instance.sale_voucher_term_accounts.aggregate(
#         the_sum=Coalesce(Sum('cgst_total'), Value(0)))['the_sum']
#     total_sgst_extra = instance.sale_voucher_term_accounts.aggregate(
#         the_sum=Coalesce(Sum('sgst_total'), Value(0)))['the_sum']
#     total_igst_extra = instance.sale_voucher_term_accounts.aggregate(
#         the_sum=Coalesce(Sum('igst_total'), Value(0)))['the_sum']

#     if total_cgst_extra :
#         instance.cgst_total = total_cgst_extra
#     if total_sgst_extra:
#         instance.sgst_total = total_sgst_extra
#     if total_igst_extra:
#         instance.igst_total = total_igst_extra


# @receiver(pre_save, sender=SaleVoucherAccounts)
# @prevent_signal_call_on_bulk_load
# def update_sales_grand_total(sender, instance, *args, **kwargs):
#     """
#     Signal to calculate the Grand total of a particular voucher
#     """




@receiver(post_save, sender=SaleTermAccounts)
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


@receiver(post_save, sender=SaleTaxAccounts)
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


@receiver(pre_delete, sender=SaleVoucherAccounts)
def delete_journal_voucher_against_terms_sales(sender, instance, **kwargs):
    """
    Signal to delete a journal entry whenever a additional ledger is deleted from a voucher
    """
    sale_voucher_term_accounts = SaleTermAccounts.objects.filter(sale_voucher=instance)
    for s in sale_voucher_term_accounts:
        s.save()
        JournalVoucher.objects.filter(
            company=s.sale_voucher.company, voucher_id=s.id).delete()


@receiver(pre_delete, sender=SaleVoucherAccounts)
def delete_journal_voucher_against_tax_sales(sender, instance, **kwargs):
    """
    Signal to delete a journal entry whenever a GST ledger is removed from a particular voucher
    """
    sales_tax = SaleTaxAccounts.objects.filter(sale_voucher=instance)
    for s in sales_tax:
        s.save()
        JournalVoucher.objects.filter(
            company=s.sale_voucher.company, voucher_id=s.id).delete()


@receiver(pre_delete, sender=SaleVoucherAccounts)
def delete_journal_voucher_against_voucher_sales(sender, instance, **kwargs):
    """
    Signal to delete a jounal entry whenever a purchase entry is deleted
    """
    JournalVoucher.objects.filter(
        user=instance.user, company=instance.company, voucher_id=instance.id).delete()


@receiver(pre_delete, sender=SaleVoucherAccounts)
def delete_related_party_ledger_sales(sender, instance, **kwargs):
    instance.party_ac.save()
    instance.party_ac.ledger_group.save()




