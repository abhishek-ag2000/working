"""
Tasks
"""
from __future__ import absolute_import, unicode_literals
from decimal import Decimal, DecimalException
from celery.decorators import task
from django.shortcuts import get_object_or_404
from django.db.models.functions import Coalesce
from django.db.models import Value, Sum
from accounting_entry.models import PeriodSelected
from stock_keeping.models import StockItem, StockBalance


@task()
def user_created_stock_ledger_task(stock_id):
    stock_details = get_object_or_404(StockItem, pk=stock_id)
    period_selected = get_object_or_404(PeriodSelected, user=stock_details.user)

    total_purchase_quantity_in_range = stock_details.purchase_stock.filter(purchase_voucher_date__lt=period_selected.start_date)
    total_sales_quantity_in_range = stock_details.sale_stock.filter(sale_voucher_date__lt=period_selected.start_date)
    total_debit_quantity_in_range = stock_details.debit_note_stock.filter(debit_notes__date__lt=period_selected.start_date)
    total_credit_quantity_in_range = stock_details.credit_note_stock.filter(credit_note__date__lt=period_selected.start_date)

    total_purchase_quantity_fos = total_purchase_quantity_in_range.aggregate(the_sum=Coalesce(Sum('quantity_p'), Value(0)))['the_sum']
    total_purchase_fos = total_purchase_quantity_in_range.aggregate(the_sum=Coalesce(Sum('total_p'), Value(0)))['the_sum']
    total_sales_quantity_fos = total_sales_quantity_in_range.aggregate(the_sum=Coalesce(Sum('quantity'), Value(0)))['the_sum']
    #total_sales_fos = total_sales_quantity_in_range.aggregate(the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']
    total_debit_quantity_os = total_debit_quantity_in_range.aggregate(the_sum=Coalesce(Sum('quantity'), Value(0)))['the_sum']
    total_debit_os = total_debit_quantity_in_range.aggregate(the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']
    total_credit_quantity_os = total_credit_quantity_in_range.aggregate(the_sum=Coalesce(Sum('quantity'), Value(0)))['the_sum']
    #total_credit_os = total_credit_quantity_in_range.aggregate(the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']

    total_purchase_quantity_os = total_purchase_quantity_fos - total_debit_quantity_os
    total_purchase_os = total_purchase_fos - total_debit_os

    total_sales_quantity_os = total_sales_quantity_fos - total_credit_quantity_os
    #total_sales_os = total_sales_fos - total_credit_os

    if not total_purchase_quantity_os:
        total_purchase_quantity_os = 0

    if not total_sales_quantity_os:
        total_sales_quantity_os = 0

    if not total_debit_quantity_os:
        total_debit_quantity_os = 0

    if not total_sales_quantity_os:
        total_sales_quantity_os = 0

    if not stock_details.quantity:
        opening_quantity = (total_purchase_quantity_fos - (total_debit_quantity_os + total_sales_quantity_os))
    else:
        opening_quantity = stock_details.quantity + (total_purchase_quantity_fos - (total_debit_quantity_os + total_sales_quantity_os))

    if total_purchase_quantity_os == 0:
        opening_stock = stock_details.opening
    else:
        opening_stock = stock_details.opening + ((Decimal(total_purchase_os) / Decimal(total_purchase_quantity_os)) * opening_quantity)  # for weighted average

# closing stock calculations
    total_purchase_quantity_in_range_cs = stock_details.purchase_stock.filter(purchase_voucher__date__gte=period_selected.start_date, purchase_voucher__date__lte=period_selected.end_date)
    total_sales_quantity_in_range_cs = stock_details.sale_stock.filter(sale_voucher__date__gte=period_selected.start_date,  sale_voucher__date__lte=period_selected.end_date)
    total_debit_quantity_in_range_cs = stock_details.debit_note_stock.filter(debit_notes__date__gte=period_selected.start_date,  debit_notes__date__lte=period_selected.end_date)
    total_credit_quantity_in_range_cs = stock_details.credit_note_stock.filter(credit_note__date__gte=period_selected.start_date,  credit_note__date__lte=period_selected.end_date)

    total_purchase_quantity_initial = total_purchase_quantity_in_range_cs.aggregate(the_sum=Coalesce(Sum('quantity_p'), Value(0)))['the_sum']
    #total_purchase_initial = total_purchase_quantity_in_range_cs.aggregate(the_sum=Coalesce(Sum('total_p'), Value(0)))['the_sum']
    total_sales_quantity_initial = total_sales_quantity_in_range_cs.aggregate(the_sum=Coalesce(Sum('quantity'), Value(0)))['the_sum']
    #total_sales = total_sales_quantity_in_range_cs.aggregate(the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']
    total_debit_quantity = total_debit_quantity_in_range_cs.aggregate(the_sum=Coalesce(Sum('quantity'), Value(0)))['the_sum']
    #total_debit = total_debit_quantity_in_range_cs.aggregate(the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']
    total_credit_quantity = total_credit_quantity_in_range_cs.aggregate(the_sum=Coalesce(Sum('quantity'), Value(0)))['the_sum']

    total_purchase_quantity = total_purchase_quantity_initial - total_debit_quantity

    #total_purchase = total_purchase_initial - total_debit

    total_sales_quantity = total_sales_quantity_initial - total_credit_quantity

    if not total_purchase_quantity:
        total_purchase_quantity = 0

    if not total_sales_quantity:
        total_sales_quantity = 0

    if not total_debit_quantity:
        total_debit_quantity = 0

    if not stock_details.quantity:
        stock_details.quantity = 0

    closing_quantity = total_purchase_quantity - total_sales_quantity

    if stock_details.quantity == 0:
        closing_quantity_real = (total_purchase_quantity - total_sales_quantity)
    elif stock_details.quantity == 0 and total_purchase_quantity == 0:
        closing_quantity_real = total_sales_quantity
    else:
        closing_quantity_real = abs(stock_details.quantity + (total_purchase_quantity - total_sales_quantity))

# weighted average calculations
    total_purchase_quantity_in_range_wavg = stock_details.purchase_stock.filter(purchases__date__lte=period_selected.end_date)

    total_purchase_quantity_wavg = total_purchase_quantity_in_range_wavg.aggregate(the_sum=Coalesce(Sum('quantity_p'), Value(0)))['the_sum']
    total_purchase_wavg = total_purchase_quantity_in_range_wavg.aggregate(the_sum=Coalesce(Sum('total_p'), Value(0)))['the_sum']

    if total_purchase_quantity_wavg == 0 and total_purchase_wavg == 0 and opening_stock == 0 and closing_quantity == 0:
        closing_stock = 0
    elif not total_purchase_quantity_wavg and not total_purchase_wavg and not opening_stock and not closing_quantity:
        closing_stock = 0
    else:
        if not total_purchase_wavg:
            closing_stock = 0
        elif not total_purchase_quantity_wavg:
            closing_stock = 0
        elif not closing_quantity:
            closing_stock = 0
        elif not opening_stock:
            closing_stock = 0
        else:
            try:
                closing_stock = (
                    (Decimal(total_purchase_wavg + stock_details.opening) /
                     Decimal(total_purchase_quantity_wavg + stock_details.quantity)) * (closing_quantity + stock_details.quantity)
                )  # for weighted average
            except DecimalException:  # handle empty transactions
                return None

    StockBalance.objects.filter(
        user=stock_details.user,
        company=stock_details.company,
        stock_item=stock_details).update(date=period_selected.start_date, opening_stock=opening_stock, closing_quantity=closing_quantity_real, closing_stock=closing_stock)
