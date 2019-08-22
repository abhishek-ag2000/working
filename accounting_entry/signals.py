"""
Signals
"""
import datetime
# import string
# import random
# from decimal import Decimal
# from functools import wraps
# from django.conf import settings
# from django.core.exceptions import ValidationError
# from django.db import models, transaction
from django.db.models.signals import pre_save, post_save, pre_delete  # , post_delete
from django.db.models.functions import Coalesce
from django.db.models import Value, Sum
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
#from django.urls import reverse
from django.utils import timezone
from bracketline.models import StateMaster, GroupBase
from company.models import Company
from user_profile.models import ProductActivated
from .decorators import prevent_signal_call_on_bulk_load
from .tasks import update_ledger_balances_task
from .models import BankReconciliation, ContraVoucher, ContraVoucherRows, PaymentVoucher, PaymentVoucherRows, ReceiptVoucher, ReceiptVoucherRows
from .models import PeriodSelected, LedgerGroup, LedgerMaster, JournalVoucher, MultiJournalVoucher


@receiver(post_save, sender=ProductActivated)
@prevent_signal_call_on_bulk_load
def create_default_period_selected(instance, created, **kwargs):
    if instance.product.id == 1 and instance.is_active:
        PeriodSelected.objects.update_or_create(
            user=instance.user,
            defaults={
                'start_date': datetime.date((datetime.datetime.now().year), 4, 1),
                'end_date': datetime.date((datetime.datetime.now().year) + 1, 3, 31)
            }
        )


@receiver(post_save, sender=Company)
@prevent_signal_call_on_bulk_load
def create_default_ledger_groups(sender, instance, created, **kwargs):
    if not created:
        return

    group_primary = LedgerGroup.objects.create(
        counter=1,
        user=instance.user,
        company=instance,
        group_name='Primary',
        self_group=None,
        group_base=GroupBase.objects.get(name='Primary'))

    LedgerGroup.objects.create(
        counter=2,
        user=instance.user,
        company=instance,
        group_name='Capital Account',
        self_group=group_primary,
        group_base=GroupBase.objects.get(name='Capital Account'))

    group_current_assets = LedgerGroup.objects.create(
        counter=3,
        user=instance.user,
        company=instance,
        group_name='Current Assets',
        self_group=group_primary,
        group_base=GroupBase.objects.get(name='Current Assets'))

    group_current_liabilities = LedgerGroup.objects.create(
        counter=4,
        user=instance.user,
        company=instance,
        group_name='Current Liabilities',
        self_group=group_primary,
        group_base=GroupBase.objects.get(name='Current Liabilities'))

    group_loans_liability = LedgerGroup.objects.create(
        counter=5,
        user=instance.user,
        company=instance,
        group_name='Loans (Liability)',
        self_group=group_primary,
        group_base=GroupBase.objects.get(name='Loans (Liability)'))

    LedgerGroup.objects.create(
        counter=6,
        user=instance.user,
        company=instance,
        group_name='Bank Accounts',
        self_group=group_current_assets,
        group_base=GroupBase.objects.get(name='Bank Accounts'))

    LedgerGroup.objects.create(
        counter=7,
        user=instance.user,
        company=instance,
        group_name='Bank OD A/c',
        self_group=group_loans_liability,
        group_base=GroupBase.objects.get(name='Bank OD A/c'))

    LedgerGroup.objects.create(
        counter=8,
        user=instance.user,
        company=instance,
        group_name='Branch / Divisions',
        self_group=group_primary,
        group_base=GroupBase.objects.get(name='Branch / Divisions'))

    LedgerGroup.objects.create(
        counter=9,
        user=instance.user,
        company=instance,
        group_name='Cash-in-Hand',
        self_group=group_current_assets,
        group_base=GroupBase.objects.get(name='Cash-in-Hand'))

    LedgerGroup.objects.create(
        counter=10,
        user=instance.user,
        company=instance,
        group_name='Deposits (Asset)',
        self_group=group_current_assets,
        group_base=GroupBase.objects.get(name='Deposits (Asset)'))

    LedgerGroup.objects.create(
        counter=11,
        user=instance.user,
        company=instance,
        group_name='Direct Expenses',
        self_group=group_primary,
        group_base=GroupBase.objects.get(name='Direct Expenses'))

    LedgerGroup.objects.create(
        counter=12,
        user=instance.user,
        company=instance,
        group_name='Direct Incomes',
        self_group=group_primary,
        group_base=GroupBase.objects.get(name='Direct Incomes'))

    LedgerGroup.objects.create(
        counter=13,
        user=instance.user,
        company=instance,
        group_name='Duties & Taxes',
        self_group=group_current_liabilities,
        group_base=GroupBase.objects.get(name='Duties & Taxes'))

    LedgerGroup.objects.create(
        counter=14,
        user=instance.user,
        company=instance,
        group_name='Fixed Assets',
        self_group=group_primary,
        group_base=GroupBase.objects.get(name='Fixed Assets'))

    LedgerGroup.objects.create(
        counter=15,
        user=instance.user,
        company=instance,
        group_name='Indirect Expenses',
        self_group=group_primary,
        group_base=GroupBase.objects.get(name='Indirect Expenses'))

    LedgerGroup.objects.create(
        counter=16,
        user=instance.user,
        company=instance,
        group_name='Indirect Incomes',
        self_group=group_primary,
        group_base=GroupBase.objects.get(name='Indirect Incomes'))

    LedgerGroup.objects.create(
        counter=17,
        user=instance.user,
        company=instance,
        group_name='Investments',
        self_group=group_primary,
        group_base=GroupBase.objects.get(name='Investments'))

    LedgerGroup.objects.create(
        counter=18,
        user=instance.user,
        company=instance,
        group_name='Loans & Advances (Asset)',
        self_group=group_current_assets,
        group_base=GroupBase.objects.get(name='Loans & Advances (Asset)'))

    LedgerGroup.objects.create(
        counter=19,
        user=instance.user,
        company=instance,
        group_name='Misc. Expenses (ASSET)',
        self_group=group_primary,
        group_base=GroupBase.objects.get(name='Misc. Expenses (ASSET)'))

    LedgerGroup.objects.create(
        counter=20,
        user=instance.user,
        company=instance,
        group_name='Provisions',
        self_group=group_current_liabilities,
        group_base=GroupBase.objects.get(name='Provisions'))

    LedgerGroup.objects.create(
        counter=21,
        user=instance.user,
        company=instance,
        group_name='Purchase Accounts',
        self_group=group_primary,
        group_base=GroupBase.objects.get(name='Purchase Accounts'))

    LedgerGroup.objects.create(
        counter=22,
        user=instance.user,
        company=instance,
        group_name='Reserves & Surplus',
        self_group=group_primary,
        group_base=GroupBase.objects.get(name='Reserves & Surplus'))

    LedgerGroup.objects.create(
        counter=23,
        user=instance.user,
        company=instance,
        group_name='Sales Accounts',
        self_group=group_primary,
        group_base=GroupBase.objects.get(name='Sales Accounts'))

    LedgerGroup.objects.create(
        counter=24,
        user=instance.user,
        company=instance,
        group_name='Secured Loans',
        self_group=group_loans_liability,
        group_base=GroupBase.objects.get(name='Secured Loans'))

    LedgerGroup.objects.create(
        counter=25,
        user=instance.user,
        company=instance,
        group_name='Stock-in-Hand',
        self_group=group_current_assets,
        group_base=GroupBase.objects.get(name='Stock-in-Hand'))

    LedgerGroup.objects.create(
        counter=26,
        user=instance.user,
        company=instance,
        group_name='Sundry Creditors',
        self_group=group_current_liabilities,
        group_base=GroupBase.objects.get(name='Sundry Creditors'))

    LedgerGroup.objects.create(
        counter=27,
        user=instance.user,
        company=instance,
        group_name='Sundry Debtors',
        self_group=group_current_assets,
        group_base=GroupBase.objects.get(name='Sundry Debtors'))

    LedgerGroup.objects.create(
        counter=28,
        user=instance.user,
        company=instance,
        group_name='Suspense A/c',
        self_group=group_primary,
        group_base=GroupBase.objects.get(name='Suspense A/c'))

    LedgerGroup.objects.create(
        counter=29,
        user=instance.user,
        company=instance,
        group_name='Unsecured Loans',
        self_group=group_loans_liability,
        group_base=GroupBase.objects.get(name='Unsecured Loans'))


@receiver(post_save, sender=LedgerGroup)
@prevent_signal_call_on_bulk_load
def save_group_company(sender, instance, created, **kwargs):
    instance.company.save()


@receiver(post_save, sender=LedgerMaster)
@prevent_signal_call_on_bulk_load
def create_ledger_openingclosing(sender, instance, created, **kwargs):
    """
    Signal implementation for accounting_entry.task module for celery implementation
    """
    period_selected = get_object_or_404(PeriodSelected, user=instance.user)

    update_ledger_balances_task(instance.company.pk, instance.pk, period_selected.pk)


@receiver(post_save, sender=Company)
@prevent_signal_call_on_bulk_load
def create_default_ledgers(sender, instance, created, **kwargs):
    counter = LedgerMaster.objects.filter(user=instance.user, company=instance).count() + 1

    if created and not LedgerMaster.objects.filter(counter=counter, user=instance.user, company=instance).exists():
        LedgerMaster.objects.create(
            counter=counter,
            user=instance.user,
            company=instance,
            ledger_group=instance.company_ledger_group.get(group_name='Cash-in-Hand'),
            ledger_name='Cash',
            opening_balance=0)
        counter += 1
        LedgerMaster.objects.create(
            counter=counter,
            user=instance.user,
            company=instance,
            ledger_group=instance.company_ledger_group.get(group_name='Primary'),
            ledger_name='Profit & Loss A/c',
            opening_balance=0)


# @receiver(post_save, sender=LedgerMaster)
# @prevent_signal_call_on_bulk_load
# def update_groups_per_ledger(sender, instance, created, **kwargs):
#     instance.ledger_group.save()


# @receiver(post_save, sender=JournalVoucher)
# @prevent_signal_call_on_bulk_load
# def update_ledger_closing_by(sender, instance, created, **kwargs):
#     instance.By.save()


# @receiver(post_save, sender=JournalVoucher)
# @prevent_signal_call_on_bulk_load
# def update_ledger_closing_to(sender, instance, created, **kwargs):
#     instance.To.save()


# @receiver(pre_delete, sender=JournalVoucher)
# @prevent_signal_call_on_bulk_load
# def delete_related_ledger_by(sender, instance, **kwargs):
#     instance.By.save()


# @receiver(pre_delete, sender=JournalVoucher)
# @prevent_signal_call_on_bulk_load
# def delete_related_ledger_to(sender, instance, **kwargs):
#     instance.To.save()


# @receiver(pre_delete, sender=JournalVoucher)
# @prevent_signal_call_on_bulk_load
# def delete_related_ledger_by_group(sender, instance, **kwargs):
#     instance.By.group1_Name.save()


# @receiver(pre_delete, sender=JournalVoucher)
# @prevent_signal_call_on_bulk_load
# def delete_related_ledger_to_group(sender, instance, **kwargs):
#     instance.To.group1_Name.save()


@receiver(post_save, sender=JournalVoucher)
@prevent_signal_call_on_bulk_load
def create_update_brs_entery(sender, instance, created, **kwargs):
    counter = BankReconciliation.objects.filter(
        user=instance.user, company=instance.company).count() + 1

    if instance.dr_ledger.ledger_group.group_base.name == 'Bank Accounts' and \
       instance.voucher_type != 'PaymentVoucher' and \
       instance.voucher_type != 'ReceiptVoucher' and \
       instance.voucher_type != 'ContraVoucher':
        BankReconciliation.objects.update_or_create(
            voucher_id=instance.id,
            voucher_type='Journal',
            url_hash=instance.url_hash,
            defaults={
                'counter': counter,
                'user': instance.user,
                'company': instance.company,
                'voucher_date': instance.voucher_date,
                'dr_ledger': instance.dr_ledger,
                'cr_ledger': instance.cr_ledger,
                'amount': instance.amount
            }
        )

        if instance.cr_ledger.ledger_group.group_base.name == 'Bank Accounts' and \
           instance.voucher_type != 'PaymentVoucher' and \
           instance.voucher_type != 'ReceiptVoucher' and \
           instance.voucher_type != 'ContraVoucher':
            BankReconciliation.objects.update_or_create(
                voucher_id=instance.id,
                voucher_type='Journal',
                url_hash=instance.url_hash,
                defaults={
                    'counter': counter,
                    'user': instance.user,
                    'company': instance.company,
                    'voucher_date': instance.voucher_date,
                    'dr_ledger': instance.dr_ledger,
                    'cr_ledger': instance.cr_ledger,
                    'amount': instance.amount
                }
            )


# @receiver(post_save, sender=JournalVoucher)
# @prevent_signal_call_on_bulk_load
# def create_bank_to(sender, instance, created, **kwargs):
#     counter = BankReconciliation.objects.filter(
#         user=instance.user, company=instance.company).count() + 1
#     if instance.To.group1_Name.group_name == 'Bank Accounts' and instance.voucher_type != 'PaymentVoucher' and instance.voucher_type != 'ReceiptVoucher' and instance.voucher_type != 'ContraVoucher':
#         BankReconciliation.objects.update_or_create(voucher_id=instance.id,
#                                                     voucher_type='JournalVoucher',
#                                                     url_hash=instance.url_hash,
#                                                     defaults={
#                                                         'counter': counter,
#                                                         'user': instance.user,
#                                                         'company': instance.company,
#                                                         'voucher_date': instance.Date,
#                                                         'dr_ledger': instance.By,
#                                                         'cr_ledger': instance.To,
#                                                         'amount': instance.Debit,
#                                                         'Credit': instance.Credit
#                                                     }
#                                                     )


@receiver(post_save, sender=PaymentVoucherRows)
@prevent_signal_call_on_bulk_load
def user_created_payment(sender, instance, created, **kwargs):
    counter = JournalVoucher.objects.filter(
        user=instance.payment.user, company=instance.payment.company).count() + 1

    JournalVoucher.objects.update_or_create(
        voucher_id=instance.id,
        voucher_type='PaymentVoucher',
        url_hash=instance.payment.url_hash,
        defaults={
            'counter': counter,
            'user': instance.payment.user,
            'company': instance.payment.company,
            'voucher_date': instance.payment.voucher_date,
            'dr_ledger': instance.particular,
            'cr_ledger': instance.payment.account,
            'amount': instance.amount
        }
    )

    if instance.payment.account.ledger_group.group_base.name == 'Bank Accounts':
        counter = BankReconciliation.objects.filter(
            user=instance.payment.user, company=instance.payment.company).count() + 1

        BankReconciliation.objects.update_or_create(
            voucher_id=instance.id,
            voucher_type='PaymentVoucher',
            url_hash=instance.payment.url_hash,
            defaults={
                'counter': counter,
                'user': instance.payment.user,
                'company': instance.payment.company,
                'voucher_date': instance.payment.voucher_date,
                'dr_ledger': instance.particular,
                'cr_ledger': instance.payment.account,
                'amount': instance.amount
            }
        )


@receiver(pre_delete, sender=PaymentVoucher)
def delete_journal_voucher_against_voucher_payment(sender, instance, **kwargs):
    payment_ledgers = PaymentVoucherRows.objects.filter(payment=instance)

    for obj in payment_ledgers:
        if obj.particular:
            JournalVoucher.objects.filter(
                user=obj.payment.user,
                company=obj.payment.company,
                voucher_type='PaymentVoucher',
                url_hash=obj.payment.url_hash,
                voucher_id=obj.id).delete()


@receiver(post_save, sender=ReceiptVoucherRows)
@prevent_signal_call_on_bulk_load
def user_created_receipt(sender, instance, created, **kwargs):
    counter = JournalVoucher.objects.filter(
        user=instance.receipt.user, company=instance.receipt.company).count() + 1

    JournalVoucher.objects.update_or_create(
        voucher_id=instance.id,
        voucher_type="ReceiptVoucher",
        url_hash=instance.receipt.url_hash,
        defaults={
            'counter': counter,
            'user': instance.receipt.user,
            'company': instance.receipt.company,
            'voucher_date': instance.receipt.voucher_date,
            'dr_ledger': instance.receipt.account,
            'cr_ledger': instance.particular,
            'amount': instance.amount
        }
    )

    if instance.receipt.account.ledger_group.group_base.name == 'Bank Accounts':
        counter = BankReconciliation.objects.filter(
            user=instance.receipt.user, company=instance.receipt.company).count() + 1

        BankReconciliation.objects.update_or_create(
            voucher_id=instance.id,
            voucher_type='ReceiptVoucher',
            url_hash=instance.receipt.url_hash,
            defaults={
                'counter': counter,
                'user': instance.receipt.user,
                'company': instance.receipt.company,
                'voucher_date': instance.receipt.voucher_date,
                'dr_ledger': instance.receipt.account,
                'cr_ledger': instance.particular,
                'amount': instance.amount
            }
        )


@receiver(pre_delete, sender=ReceiptVoucher)
def delete_journal_voucher_against_voucher_receipt(sender, instance, **kwargs):
    receipts_ledgers = ReceiptVoucherRows.objects.filter(receipt=instance)

    for obj in receipts_ledgers:
        if obj.particular:
            JournalVoucher.objects.filter(
                user=obj.receipt.user,
                company=obj.receipt.company,
                voucher_type="ReceiptVoucher",
                url_hash=obj.receipt.url_hash,
                voucher_id=obj.id).delete()


@receiver(post_save, sender=ContraVoucherRows)
@prevent_signal_call_on_bulk_load
def user_created_contra(sender, instance, created, **kwargs):
    counter = JournalVoucher.objects.filter(
        user=instance.contra.user, company=instance.contra.company).count() + 1

    JournalVoucher.objects.update_or_create(
        voucher_id=instance.id,
        voucher_type="ContraVoucher",
        url_hash=instance.contra.url_hash,
        defaults={
            'counter': counter,
            'user': instance.contra.user,
            'company': instance.contra.company,
            'voucher_date': instance.contra.voucher_date,
            'dr_ledger': instance.contra.account,
            'cr_ledger': instance.particular,
            'amount': instance.amount,
        }
    )

    if instance.contra.account.ledger_group.group_base.name == 'Bank Accounts':
        counter = BankReconciliation.objects.filter(
            user=instance.contra.user, company=instance.contra.company).count() + 1

        BankReconciliation.objects.update_or_create(
            voucher_id=instance.id,
            voucher_type="ContraVoucher",
            url_hash=instance.contra.url_hash,
            defaults={
                'counter': counter,
                'voucher_date': instance.contra.voucher_date,
                'user': instance.contra.user,
                'company': instance.contra.company,
                'dr_ledger': instance.contra.account,
                'cr_ledger': instance.particular,
                'amount': instance.amount
            }
        )

        if instance.particular.ledger_group.group_base.name == 'Bank Accounts':
            counter = BankReconciliation.objects.filter(
                user=instance.contra.user, company=instance.contra.company).count() + 1

            BankReconciliation.objects.update_or_create(
                voucher_id=instance.id,
                voucher_type="ContraVoucher",
                url_hash=instance.contra.url_hash,
                defaults={
                    'counter': counter,
                    'voucher_date': instance.contra.voucher_date,
                    'user': instance.contra.user,
                    'company': instance.contra.company,
                    'dr_ledger': instance.contra.account,
                    'cr_ledger': instance.particular,
                    'amount': instance.amount
                }
            )


@receiver(pre_delete, sender=ContraVoucher)
def delete_journal_voucher_against_voucher_contra(sender, instance, **kwargs):
    contras_ledgers = ContraVoucherRows.objects.filter(contra=instance)
    for obj in contras_ledgers:
        if obj.particular:
            JournalVoucher.objects.filter(
                user=obj.contra.user,
                company=obj.contra.company,
                voucher_type="ContraVoucher",
                url_hash=obj.contra.url_hash,
                voucher_id=obj.id).delete()

            #obj.particular.save()  # save row level ledger for balance update

    #instance.account.save()  # save doc level ledger for balance update
