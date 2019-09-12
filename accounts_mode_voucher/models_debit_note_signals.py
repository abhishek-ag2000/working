"""
Signals for Debit Note
"""
from django.db.models import Value, Sum
from django.db.models.signals import pre_save, post_save, pre_delete, post_delete
from django.db.models.functions import Coalesce
from django.dispatch import receiver
from accounting_entry.models import JournalVoucher
from accounting_entry.decorators import prevent_signal_call_on_bulk_load
from .models_debit_note import DebitNoteAccountsVoucher, DebitNoteAccountsTerm, DebitNoteTax



# @receiver(pre_save, sender=DebitNoteAccountsVoucher)
# @prevent_signal_call_on_bulk_load
# def update_gst_totals_debit_note(sender, instance, *args, **kwargs):
#     """
#     Signal to calculate the GST totals of a particular voucher
#     """

#     total_cgst_extra = instance.debit_note_extra_accounts.aggregate(
#         the_sum=Coalesce(Sum('cgst_total'), Value(0)))['the_sum']
#     total_sgst_extra = instance.debit_note_extra_accounts.aggregate(
#         the_sum=Coalesce(Sum('sgst_total'), Value(0)))['the_sum']
#     total_igst_extra = instance.debit_note_extra_accounts.aggregate(
#         the_sum=Coalesce(Sum('igst_total'), Value(0)))['the_sum']

#     if total_cgst_extra:
#         instance.cgst_total = total_cgst_extra
#     if total_sgst_extra:
#         instance.sgst_total = total_sgst_extra
#     if total_igst_extra:
#         instance.igst_total = total_igst_extra


@receiver(pre_save, sender=DebitNoteAccountsVoucher)
@prevent_signal_call_on_bulk_load
def update_total_tax_debit_note(sender, instance, *args, **kwargs):
    """
    Signal to calculate the Tax totals of a particular voucher in case of Composite billing
    """

    total_tax_extra = instance.debit_note_extra_accounts.aggregate(
        the_sum=Coalesce(Sum('tax_total'), Value(0)))['the_sum']

    if total_tax_extra:
        instance.tax_total = total_tax_extra


# @receiver(pre_save, sender=DebitNoteAccountsVoucher)
# @prevent_signal_call_on_bulk_load
# def update_debitnote_grand_total(sender, instance, *args, **kwargs):
#     """
#     Signal to calculate the Grand Total of a particular voucher
#     """


# @receiver(post_save, sender=DebitNoteAccountsVoucher)
# @prevent_signal_call_on_bulk_load
# def user_created_debit_note(sender, instance, created, **kwargs):
#     """
#     Signal to create a journal entry whenever a voucher is submitted.
#     """
#     c = JournalVoucher.objects.filter(
#         user=instance.user, company=instance.company).count() + 1
#     if instance.sub_total != 0 and instance.doc_ledger:
#         JournalVoucher.objects.update_or_create(
#             voucher_id=instance.id,
#             voucher_type="Debit Note",
#             url_hash=instance.url_hash,
#             defaults={
#                 'counter': c,
#                 'user': instance.user,
#                 'company': instance.company,
#                 'voucher_date': instance.voucher_date,
#                 'dr_ledger': instance.party_ac,
#                 'cr_ledger': instance.doc_ledger,
#                 'amount': instance.sub_total}
#         )


@receiver(post_save, sender=DebitNoteAccountsTerm)
@prevent_signal_call_on_bulk_load
def user_created_debitnote_extra_charge(sender, instance, created, **kwargs):
    """
    Signals to create a journal entry for the additional charges Ledger in a particular entry
    """
    c = JournalVoucher.objects.filter(
        user=instance.debit_note.user, company=instance.debit_note.company).count() + 1
    if instance.total != 0 and instance.ledger:
        JournalVoucher.objects.update_or_create(
            voucher_id=instance.id,
            voucher_type="Charges_against_Debitnote",
            defaults={
                'counter': c,
                'user': instance.debit_note.user,
                'company': instance.debit_note.company,
                'voucher_date': instance.debit_note.voucher_date,
                'dr_ledger': instance.debit_note.party_ac,
                'cr_ledger': instance.ledger,
                'amount': instance.total}
        )


@receiver(post_save, sender=DebitNoteTax)
@prevent_signal_call_on_bulk_load
def user_created_debitnote_gst_charge(sender, instance, created, **kwargs):
    """
    Signal to create a jounal entry for the GST ledgers in a particular voucher
    """
    c = JournalVoucher.objects.filter(
        user=instance.debit_note.user, company=instance.debit_note.company).count() + 1
    if instance.total != 0 and instance.ledger:
        JournalVoucher.objects.update_or_create(
            voucher_id=instance.id,
            voucher_type="Tax_aganist_debitnote",
            defaults={
                'counter': c,
                'user': instance.debit_note.user,
                'company': instance.debit_note.company,
                'voucher_date': instance.debit_note.voucher_date,
                'dr_ledger': instance.debit_note.party_ac,
                'cr_ledger': instance.ledger,
                'amount': instance.total}
        )


@receiver(pre_delete, sender=DebitNoteAccountsVoucher)
def delete_journal_voucher_against_terms_debitnote(sender, instance, **kwargs):
    """
    Signal to delete a journal entry whenever a additional ledger is deleted from a voucher
    """
    debit_extra = DebitNoteAccountsTerm.objects.filter(debit_note=instance)
    for s in debit_extra:
        s.save()
        JournalVoucher.objects.filter(
            company=s.debit_note.company, voucher_id=s.id).delete()


@receiver(pre_delete, sender=DebitNoteAccountsVoucher)
def delete_journal_voucher_against_tax_debitnote(sender, instance, **kwargs):
    """
    Signal to delete a journal entry whenever a GST ledger is removed from a particular voucher
    """
    debit_extra = DebitNoteTax.objects.filter(debit_note=instance)
    for s in debit_extra:
        s.save()
        JournalVoucher.objects.filter(
            company=s.debit_note.company, voucher_id=s.id).delete()


@receiver(pre_delete, sender=DebitNoteAccountsVoucher)
def delete_journal_voucher_against_voucher_debit_notes(sender, instance, **kwargs):
    """
    Signal to delete a jounal entry whenever a purchase entry is deleted
    """
    JournalVoucher.objects.filter(
        user=instance.user, company=instance.company, voucher_id=instance.id).delete()


@receiver(pre_delete, sender=DebitNoteAccountsVoucher)
def delete_related_party_ledger_debitnote(sender, instance, **kwargs):
    instance.party_ac.save()
    instance.party_ac.ledger_group.save()
