"""
Signals for Credit Note
"""
from django.db.models import Value, Sum
from django.db.models.signals import pre_save, post_save, pre_delete, post_delete
from django.db.models.functions import Coalesce
from django.dispatch import receiver
from accounting_entry.models import JournalVoucher
from accounting_entry.decorators import prevent_signal_call_on_bulk_load
from .models import StockItem
from .models_credit_note import CreditNoteVoucher, CreditNoteTerm, CreditNoteTax


# @receiver(pre_save, sender=CreditNoteVoucher)
# @prevent_signal_call_on_bulk_load
# def update_subtotal_credit_note(sender, instance, *args, **kwargs):
#     """
#     Signal to calculate the sub total of every goods in a particular voucher
#     """
#     total = instance.credit_note_voucher.aggregate(
#         the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']

#     if total:
#         instance.sub_total = total



# @receiver(pre_save, sender=CreditNoteVoucher)
# @prevent_signal_call_on_bulk_load
# def update_gst_totals_credit_note(sender, instance, *args, **kwargs):
#     """
#     Signal to calculate the GST totals of a particular voucher
#     """
#     total_cgst_stock = instance.credit_note_voucher.aggregate(
#         the_sum=Coalesce(Sum('cgst_total'), Value(0)))['the_sum']
#     total_sgst_stock = instance.credit_note_voucher.aggregate(
#         the_sum=Coalesce(Sum('sgst_total'), Value(0)))['the_sum']
#     total_igst_stock = instance.credit_note_voucher.aggregate(
#         the_sum=Coalesce(Sum('igst_total'), Value(0)))['the_sum']

#     total_cgst_extra = instance.credit_note_term.aggregate(
#         the_sum=Coalesce(Sum('cgst_total'), Value(0)))['the_sum']
#     total_sgst_extra = instance.credit_note_term.aggregate(
#         the_sum=Coalesce(Sum('sgst_total'), Value(0)))['the_sum']
#     total_igst_extra = instance.credit_note_term.aggregate(
#         the_sum=Coalesce(Sum('igst_total'), Value(0)))['the_sum']

#     if total_cgst_stock or total_cgst_extra:
#         instance.cgst_total = total_cgst_stock + total_cgst_extra
#     if total_sgst_stock or total_sgst_extra:
#         instance.sgst_total = total_sgst_stock + total_sgst_extra
#     if total_igst_stock or total_igst_extra:
#         instance.igst_total = total_igst_stock + total_igst_extra


@receiver(pre_save, sender=CreditNoteVoucher)
@prevent_signal_call_on_bulk_load
def update_total_tax_credit_note(sender, instance, *args, **kwargs):
    """
    Signal to calculate the Tax totals of a particular voucher in case of Composite billing
    """
    total_tax_stock = instance.credit_note_voucher.aggregate(
        the_sum=Coalesce(Sum('tax_total'), Value(0)))['the_sum']

    total_tax_extra = instance.credit_note_term.aggregate(
        the_sum=Coalesce(Sum('tax_total'), Value(0)))['the_sum']

    if total_tax_stock and total_tax_extra:
        instance.tax_total = total_tax_stock + total_tax_extra
    elif total_tax_stock:
        instance.tax_total = total_tax_stock
    elif total_tax_extra:
        instance.tax_total = total_tax_extra
    else:
        instance.tax_total = 0


# @receiver(pre_save, sender=CreditNoteVoucher)
# @prevent_signal_call_on_bulk_load
# def update_credit_note_grand_total(sender, instance, *args, **kwargs):
#     """
#     Signal to calculate the Grand total of a particular voucher
#     """
#     tax_total = instance.credit_note_gst.aggregate(
#         the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']
#     extra_total = instance.credit_note_term.aggregate(
#         the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']
#     stock_total = instance.credit_note_voucher.aggregate(
#         the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']

#     if tax_total or extra_total or stock_total:
#         instance.total = tax_total + extra_total + stock_total


@receiver(post_save, sender=CreditNoteVoucher)
@prevent_signal_call_on_bulk_load
def user_created_credit_note(sender, instance, created, **kwargs):
    """
    Signal to create a journal entry whenever a voucher is submitted.
    """
    counter = JournalVoucher.objects.filter(
        user=instance.user, 
        company=instance.company).count() + 1
    if instance.sub_total != 0:
        JournalVoucher.objects.update_or_create(
            voucher_id=instance.id,
            voucher_type="Credit Note",
            url_hash=instance.url_hash,
            defaults={
                'counter': counter,
                'user': instance.user,
                'company': instance.company,
                'voucher_date': instance.voucher_date,
                'cr_ledger': instance.party_ac,
                'dr_ledger': instance.doc_ledger,
                'amount': instance.sub_total}
        )

@receiver(post_save, sender=CreditNoteTerm)
@prevent_signal_call_on_bulk_load
def user_created_credit_note_extra_charge(sender, instance, created, **kwargs):
    """
    Signals to create a journal entry for the additional charges Ledger in a particular entry
    """
    counter = JournalVoucher.objects.filter(
        user=instance.credit_note.user, 
        company=instance.credit_note.company).count() + 1
    if instance.total != 0:
        JournalVoucher.objects.update_or_create(
            voucher_id=instance.id,
            voucher_type="Charges_against_Credit_Note",
            defaults={
                'counter': counter,
                'user': instance.credit_note.user,
                'company': instance.credit_note.company,
                'voucher_date': instance.credit_note.voucher_date,
                'cr_ledger': instance.credit_note.party_ac,
                'dr_ledger': instance.ledger,
                'amount': instance.total}
        )


@receiver(post_save, sender=CreditNoteTax)
@prevent_signal_call_on_bulk_load
def user_created_credit_note_gst_charge(sender, instance, created, **kwargs):
    """
    Signal to create a jounal entry for the GST ledgers in a particular voucher
    """
    counter = JournalVoucher.objects.filter(
        user=instance.credit_note.user, company=instance.credit_note.company).count() + 1
    if instance.total != 0 and instance.ledger:
        JournalVoucher.objects.update_or_create(
            voucher_id=instance.id,
            voucher_type="Tax against Credit Note",
            defaults={
                'counter': counter,
                'user': instance.credit_note.user,
                'company': instance.credit_note.company,
                'voucher_date': instance.credit_note.voucher_date,
                'cr_ledger': instance.credit_note.party_ac,
                'dr_ledger': instance.ledger,
                'amount': instance.total}
        )



@receiver(pre_delete, sender=CreditNoteVoucher)
def delete_journal_voucher_against_terms_credit_note(sender, instance, **kwargs):
    """
    Signal to delete a journal entry whenever a additional ledger is deleted from a voucher
    """
    credit_extra = CreditNoteTerm.objects.filter(credit_note=instance)
    for s in credit_extra:
        s.save()
        JournalVoucher.objects.filter(
            user=s.credit_note.user, company=s.credit_note.company, voucher_id=s.id).delete()


@receiver(pre_delete, sender=CreditNoteVoucher)
def delete_journal_voucher_against_tax_credit_note(sender, instance, **kwargs):
    """
    Signal to delete a journal entry whenever a GST ledger is removed from a particular voucher
    """
    credit_gst = CreditNoteTax.objects.filter(credit_note=instance)
    for s in credit_gst:
        s.save()
        JournalVoucher.objects.filter(
            user=s.credit_note.user, company=s.credit_note.company, voucher_id=s.id).delete()


@receiver(pre_delete, sender=CreditNoteVoucher)
def delete_journal_voucher_against_voucher_credit_notes(sender, instance, **kwargs):
    """
    Signal to delete a jounal entry whenever a purchase entry is deleted
    """
    JournalVoucher.objects.filter(
        user=instance.user, company=instance.company, voucher_id=instance.id).delete()


@receiver(pre_delete, sender=CreditNoteVoucher)
def delete_related_party_ledger_credit_note(sender, instance, **kwargs):
    instance.party_ac.save()
    instance.party_ac.ledger_group.save()


@receiver(pre_delete, sender=CreditNoteVoucher)
def delete_related_credit_note_ledger(sender, instance, **kwargs):
    instance.doc_ledger.save()
    instance.doc_ledger.ledger_group.save()


@receiver(post_delete, sender=CreditNoteVoucher)
def delete_related_stock_for_credit_note(sender, instance, *args, **kwargs):
    sales_stock = StockItem.objects.filter(company=instance.company)
    for obj in sales_stock:
        obj.save()