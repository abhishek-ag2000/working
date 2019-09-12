"""
Views for Final Account and related statements
"""
import decimal
from django.shortcuts import get_object_or_404, render
from django.db.models.functions import Coalesce
from django.db.models import Case, When, Count, Value, Sum, ExpressionWrapper, Q, F, OuterRef, Subquery, FloatField
from django.db.models.fields import DecimalField
from django.contrib.auth.decorators import login_required
from company.models import Company
from messaging.models import Message
from ecommerce_integration.decorators import product_1_activation
from stock_keeping.models import StockBalance
from .models import PeriodSelected, LedgerGroup, LedgerMaster, JournalVoucher
from stock_keeping.models import StockItem
from stock_keeping.models_purchase import PurchaseStock
from stock_keeping.models_sale import SaleStock
from stock_keeping.models_debit_note import DebitNoteStock
from stock_keeping.models_credit_note import CreditNoteStock


@login_required
@product_1_activation
def profit_and_loss_condensed_view(request, company_pk, period_selected_pk):
    company = get_object_or_404(Company, pk=company_pk)
    period_selected = get_object_or_404(PeriodSelected, pk=period_selected_pk)

    # Opening Stock
    Stock_item_list = StockItem.objects.filter(company=company)
    total_purchase_stock_in_range = PurchaseStock.objects.filter(
        purchase_voucher__voucher_date__lt=period_selected.start_date).values('stock_item')
    total_sales_stock_in_range = SaleStock.objects.filter(
        sale_voucher__voucher_date__lt=period_selected.start_date).values('stock_item')
    total_debit_note_stock_in_range = DebitNoteStock.objects.filter(
        debit_note__voucher_date__lt=period_selected.start_date).values('stock_item')
    total_credit_note_stock_in_range = CreditNoteStock.objects.filter(
        credit_note__voucher_date__lt=period_selected.start_date).values('stock_item')

    stock_item_quantity = Stock_item_list.aggregate(
        the_sum=Coalesce(Sum('quantity'), Value(0)))['the_sum']

    stock_item_opening = Stock_item_list.aggregate(
        the_sum=Coalesce(Sum('opening'), Value(0)))['the_sum']

    total_purchase_quantity = total_purchase_stock_in_range.aggregate(
        the_sum=Coalesce(Sum('quantity'), Value(0)))['the_sum']

    total_purchase_stock = total_purchase_stock_in_range.aggregate(
        the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']

    total_sales_quantity = total_sales_stock_in_range.aggregate(
        the_sum=Coalesce(Sum('quantity'), Value(0)))['the_sum']

    total_debitnote_quantity = total_debit_note_stock_in_range.aggregate(
        the_sum=Coalesce(Sum('quantity'), Value(0)))['the_sum']

    total_debit_note = total_debit_note_stock_in_range.aggregate(
        the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']

    total_creditnote_quantity = total_credit_note_stock_in_range.aggregate(
        the_sum=Coalesce(Sum('quantity'), Value(0)))['the_sum']

    if not total_purchase_quantity:
        total_purchase_quantity = 0

    if not total_purchase_stock:
        total_purchase_stock = 0

    if not total_sales_quantity:
        total_sales_quantity = 0

    if not total_debitnote_quantity:
        total_debitnote_quantity = 0

    if not total_debit_note:
        total_debit_note = 0

    if not total_debit_note:
        total_debit_note = 0

    if not total_creditnote_quantity:
        total_creditnote_quantity = 0

    total_purchase_quantity_os = total_purchase_quantity - total_debitnote_quantity
    total_purchase_os = total_purchase_stock - total_debit_note

    total_sales_quantity_os = total_sales_quantity - total_creditnote_quantity

    if not stock_item_quantity:
        opening_quantity = (
            total_purchase_quantity - (total_debitnote_quantity + total_sales_quantity_os))
    else:
        opening_quantity = stock_item_quantity + \
            (total_purchase_quantity -
             (total_debitnote_quantity + total_sales_quantity_os))

    if total_purchase_quantity_os != 0 and opening_quantity != 0 and total_purchase_os != 0:
        opening_stock = stock_item_opening + \
            (((total_purchase_os) / (total_purchase_quantity_os))
             * opening_quantity)  # for weighted average
    else:
        # opening_stock = stock_item_opening + (((total_purchase_os) / (total_purchase_quantity_os)) * opening_quantity)  # for weighted average
        opening_stock = stock_item_opening

    if not opening_stock:
        opening_stock = 0

    # Closing Stock Calculation
    purchase_stock = PurchaseStock.objects.filter(purchase_voucher__company=company, stock_item=OuterRef(
        'pk'), purchase_voucher__voucher_date__gte=period_selected.start_date, purchase_voucher__voucher_date__lte=period_selected.end_date).values('stock_item')
    purchase_stock_total = PurchaseStock.objects.filter(purchase_voucher__company=company, stock_item=OuterRef(
        'pk'), purchase_voucher__voucher_date__gte=period_selected.start_date, purchase_voucher__voucher_date__lte=period_selected.end_date).values('stock_item')
    sales_stock = SaleStock.objects.filter(sale_voucher__company=company, stock_item=OuterRef(
        'pk'), sale_voucher__voucher_date__gte=period_selected.start_date, sale_voucher__voucher_date__lte=period_selected.end_date).values('stock_item')
    debit_note_stock = DebitNoteStock.objects.filter(debit_note__company=company, stock_item=OuterRef(
        'pk'), debit_note__voucher_date__gte=period_selected.start_date, debit_note__voucher_date__lte=period_selected.end_date).values('stock_item')
    credit_note_stock = CreditNoteStock.objects.filter(credit_note__company=company, stock_item=OuterRef(
        'pk'), credit_note__voucher_date__gte=period_selected.start_date, credit_note__voucher_date__lte=period_selected.end_date).values('stock_item')

    total_purchase_quantity = purchase_stock.annotate(
        quantity_total=Coalesce(Sum('quantity'), Value(0))).values('quantity_total')

    total_purchase_value = purchase_stock_total.annotate(
        total=Coalesce(Sum('total'), Value(0))).values('total')

    total_sales_quantity = sales_stock.annotate(
        quantity_total=Coalesce(Sum('quantity'), Value(0))).values('quantity_total')

    total_debit_note_quantity = debit_note_stock.annotate(
        quantity_total=Coalesce(Sum('quantity'), Value(0))).values('quantity_total')

    total_credit_note_quantity = credit_note_stock.annotate(
        quantity_total=Coalesce(Sum('quantity'), Value(0))).values('quantity_total')

    stock_list = StockItem.objects.filter(company=company).annotate(
        purchase_quantity=Coalesce(
            Subquery(total_purchase_quantity, output_field=FloatField()), Value(0)),
        sales_quantity=Coalesce(
            Subquery(total_sales_quantity, output_field=FloatField()), Value(0)),
        debit_note_quantity=Coalesce(
            Subquery(total_debit_note_quantity, output_field=FloatField()), Value(0)),
        credit_note_quantity=Coalesce(
            Subquery(total_credit_note_quantity, output_field=FloatField()), Value(0)),
        purchase_value=Coalesce(
            Subquery(total_purchase_value, output_field=FloatField()), Value(0)),
    )

    stock_quantities = stock_list.annotate(
        total_purchase_quantity_final=ExpressionWrapper(
            F('purchase_quantity') - F('debit_note_quantity'), output_field=FloatField()),
        total_sales_quantity_final=ExpressionWrapper(
            F('sales_quantity') - F('credit_note_quantity'), output_field=FloatField()),
    )

    stock_closing_quantity = stock_quantities.annotate(
        closing_quantity=ExpressionWrapper(F('quantity') + F('total_purchase_quantity_final') - F(
            'total_sales_quantity_final'), output_field=FloatField()),
        grand_total_purchase_quantity=ExpressionWrapper(
            F('quantity') + F('total_purchase_quantity_final'), output_field=FloatField()),
        grand_total_purchase=ExpressionWrapper(
            F('purchase_value') + F('opening'), output_field=FloatField()),
    )

    closing_balance_only_purchase = stock_closing_quantity.annotate(
        purchase_closing_balance=Case(
            When(grand_total_purchase_quantity__gt=0, then=F(
                'grand_total_purchase') / F('grand_total_purchase_quantity')),
            default=0,
            output_field=FloatField()
        )
    )

    closing_balance_final = closing_balance_only_purchase.annotate(
        closing_balance=ExpressionWrapper(
            F('purchase_closing_balance') * F('closing_quantity'), output_field=FloatField()),
    )

    total_closing_stock = closing_balance_final.aggregate(
        the_sum=Coalesce(Sum('closing_balance'), Value(0)))['the_sum']

    # Journal queries to get the debit and credit balances of all ledgers
    Journal_debit = JournalVoucher.objects.filter(company=company, dr_ledger=OuterRef(
        'pk'), voucher_date__gte=period_selected.start_date, voucher_date__lte=period_selected.end_date).values('dr_ledger')

    Journal_credit = JournalVoucher.objects.filter(company=company, cr_ledger=OuterRef(
        'pk'), voucher_date__gte=period_selected.start_date, voucher_date__lte=period_selected.end_date).values('cr_ledger')

    Journal_debit_opening = JournalVoucher.objects.filter(company=company, dr_ledger=OuterRef(
        'pk'), voucher_date__lt=period_selected.start_date).values('dr_ledger')

    Journal_credit_opening = JournalVoucher.objects.filter(company=company, cr_ledger=OuterRef(
        'pk'), voucher_date__lt=period_selected.start_date).values('cr_ledger')

    total_debit = Journal_debit.annotate(
        total=Coalesce(Sum('amount'), Value(0))).values('total')

    total_credit = Journal_credit.annotate(
        total=Coalesce(Sum('amount'), Value(0))).values('total')

    total_debit_opening = Journal_debit_opening.annotate(
        total=Coalesce(Sum('amount'), Value(0))).values('total')

    total_credit_opening = Journal_credit_opening.annotate(
        total=Coalesce(Sum('amount'), Value(0))).values('total')

    ledgers = LedgerMaster.objects.filter(company=company).annotate(
        debit_balance_opening=Coalesce(
            Subquery(total_debit_opening, output_field=FloatField()), Value(0)),
        credit_balance_opening=Coalesce(
            Subquery(total_credit_opening, output_field=FloatField()), Value(0)),
        debit_balance=Coalesce(
            Subquery(total_debit, output_field=FloatField()), Value(0)),
        credit_balance=Coalesce(
            Subquery(total_credit, output_field=FloatField()), Value(0))
    )

    ledger_list = ledgers.annotate(
        opening_balance_generated=Case(
            When(ledger_group__group_base__is_debit='Yes', then=F(
                'opening_balance') + F('debit_balance_opening') - F('credit_balance_opening')),
            When(ledger_group__group_base__is_debit='No', then=F(
                'opening_balance') + F('credit_balance_opening') - F('debit_balance_opening')),
            default=None,
            output_field=FloatField()
        ),
    )

    ledger_final_list = ledger_list.annotate(
        closing_balance_generated=Case(
            When(ledger_group__group_base__is_debit='Yes', then=F(
                'opening_balance_generated') + F('debit_balance') - F('credit_balance')),
            When(ledger_group__group_base__is_debit='No', then=F(
                'opening_balance_generated') + F('credit_balance') - F('debit_balance')),
            default=None,
            output_field=FloatField()
        ),
    )


    # closing stock
    qs2 = decimal.Decimal(round(total_closing_stock , 2))

    # opening stock
    qo2 = decimal.Decimal(round(opening_stock , 2))

    # purchases #debit
    ld = ledger_final_list.filter(ledger_group__group_base__name__contains='Purchase Accounts')
    ldc = decimal.Decimal(ld.aggregate(the_sum=Coalesce(
        Sum('closing_balance_generated'), Value(0)))['the_sum'])

    # Direct Expense #debit
    ldd = ledger_final_list.filter(ledger_group__group_base__name__contains='Direct Expenses')
    lddt = decimal.Decimal(ldd.aggregate(the_sum=Coalesce(
        Sum('closing_balance_generated'), Value(0)))['the_sum'])

    # Direct Income #credit
    ldii = ledger_final_list.filter(ledger_group__group_base__name__contains='Direct Incomes')
    lddi = decimal.Decimal(ldii.aggregate(the_sum=Coalesce(
        Sum('closing_balance_generated'), Value(0)))['the_sum'])

    # sales #credit
    lds = ledger_final_list.filter(ledger_group__group_base__name__contains='Sales Account')
    ldsc = decimal.Decimal(lds.aggregate(the_sum=Coalesce(
        Sum('closing_balance_generated'), Value(0)))['the_sum'])

    # Indirect Expense  #debit
    lde = ledger_final_list.filter(ledger_group__group_base__name__contains='Indirect Expenses')
    total = decimal.Decimal(lde.aggregate(the_sum=Coalesce(
        Sum('closing_balance_generated'), Value(0)))['the_sum'])
    # ldsecr = lde.aggregate(the_sum=Coalesce(Sum('negative_closing'), Value(0)))['the_sum']
    # if ldse == 0 or ldse == None:
    #     total = - ldsecr
    # elif ldsecr == 0 or ldsecr == None:
    #     total = ldse
    # else:
    #     total = ldse - ldsecr

    # Indirect Income #credit
    ldi = ledger_final_list.filter(ledger_group__group_base__name__contains='Indirect Incomes')
    ldsi = decimal.Decimal(ldi.aggregate(the_sum=Coalesce(
        Sum('closing_balance_generated'), Value(0)))['the_sum'])
    print(type(ldsi))
    # qo1 means opening stock exists

    # lddt = Direct Expenses
    # lddi = Direct Incomes
    # ldc = Purchase Accounts
    # ldsc = Sales Account
    # qs2 = closing stock
    # qo2 = opening stock

    # gross profit/loss calculation
    if lddi < 0 and lddt < 0:
        gp = abs(ldsc) + abs(qs2) + abs(lddt) - abs(qo2) - abs(ldc) - abs(lddi)
    elif lddt < 0:
        gp = abs(ldsc) + abs(qs2) + abs(lddi) + abs(lddt) - abs(qo2) - abs(ldc)
    elif lddi < 0:
        gp = abs(ldsc) + abs(qs2) - abs(lddi) - abs(qo2) - abs(ldc) - abs(lddt)
    else:
        gp = abs(ldsc) + abs(qs2) + abs(lddi) - abs(qo2) - abs(ldc) - abs(lddt)

    # Trading profil/loss calculation
    if gp >= 0:
        if lddi < 0 and lddt < 0:
            tradingp = abs(qo2) + abs(ldc) + (gp) + abs(lddi)
            tgp = abs(qs2) + abs(ldsc) + abs(lddt)
        elif lddt < 0:
            tradingp = abs(qo2) + abs(ldc) + (gp)
            tgp = abs(qs2) + abs(lddi) + abs(ldsc) + abs(lddt)
        elif lddi < 0:
            tradingp = abs(qo2) + abs(ldc) + abs(lddt) + (gp) + abs(lddi)
            tgp = abs(qs2) + abs(ldsc)

        else:
            tradingp = abs(qo2) + abs(ldc) + abs(lddt) + (gp)
            tgp = abs(qs2) + abs(lddi) + abs(ldsc)

    else:  # gp <0
        if lddi < 0 and lddt < 0:
            tradingp = abs(qo2) + abs(ldc) + abs(lddi)
            tgp = abs(qs2) + abs(ldsc) + abs(gp) + abs(lddt)
        elif lddt < 0:
            tradingp = abs(qo2) + abs(ldc)
            tgp = abs(qs2) + abs(lddi) + abs(ldsc) + abs(gp) + abs(lddt)
        elif lddi < 0:
            tradingp = abs(qo2) + abs(ldc) + abs(lddt) + abs(lddi)
            tgp = abs(qs2) + abs(ldsc) + abs(gp)

        else:
            tradingp = abs(qo2) + abs(ldc) + abs(lddt)
            tgp = abs(qs2) + abs(lddi) + abs(ldsc) + abs(gp)

    # total = Indirect Expense
    # ldsi = Indirect Income

    # nett profit/loss calculation
    if gp >= 0:
        if ldsi < 0 and total < 0:
            np = (gp) + abs(total) - abs(ldsi)
        elif total < 0:
            np = (gp) + abs(ldsi) + abs(total)
        elif ldsi < 0:
            np = (gp) - abs(ldsi) - abs(total)
        else:
            np = (gp) + abs(ldsi) - abs(total)
    else:
        if ldsi < 0 and total < 0:
            np = abs(total) - abs(ldsi) - abs(gp)
        elif ldsi < 0:
            np = abs(ldsi) + abs(total) + abs(gp)
        elif total < 0:
            np = abs(ldsi) + abs(total) - abs(gp)
        else:
            np = abs(ldsi) - abs(total) - abs(gp)

    # total = Indirect Expense
    # ldsi = Indirect Income

    # Total value calculation
    if gp >= 0:
        if np >= 0:
            if ldsi < 0 and total < 0:
                tp = abs(ldsi) + np
                tc = abs(total) + (gp)
            elif ldsi < 0:
                tp = abs(ldsi) + np + abs(total)
                tc = (gp)
            elif total < 0:
                tp = np
                tc = abs(ldsi) + (gp) + abs(total)
            else:
                tp = abs(total) + np
                tc = abs(ldsi) + (gp)
        else:
            if ldsi < 0 and total < 0:
                tp = abs(ldsi)
                tc = gp + np + abs(total)
            elif ldsi < 0:
                tp = abs(total) + abs(ldsi)
                tc = gp + np
            elif total < 0:
                tp = 0
                tc = gp + np + abs(ldsi) + abs(total)
            else:
                tp = abs(total)
                tc = gp + np + abs(ldsi)
    else:  # gp<0
        if np >= 0:
            if ldsi < 0 and total < 0:
                tp = abs(ldsi) + np + abs(gp)
                tc = abs(total)
            elif ldsi < 0:
                tp = abs(total) + np + abs(gp) + abs(ldsi)
                tc = 0
            elif total < 0:
                tp = np + abs(gp)
                tc = abs(ldsi) + abs(total)
            else:
                tp = abs(total) + np + abs(gp)
                tc = abs(ldsi)
        else:
            if ldsi < 0 and total < 0:
                tp = abs(ldsi) + abs(gp)
                tc = abs(np) + abs(total)
            elif ldsi < 0:
                tp = abs(total) + abs(gp) + abs(ldsi)
                tc = abs(np)
            elif total < 0:
                tp = abs(gp)
                tc = abs(np) + abs(ldsi) + abs(total)
            else:
                tp = abs(total) + abs(gp)
                tc = abs(np) + abs(ldsi)

    # company_detail = Company.objects.get(pk=company.pk)
    # company_detail.pl = abs(np)
    # company_detail.save(update_fields=['pl'])

    inbox = Message.objects.filter(reciever=request.user)
    inbox_count = inbox.aggregate(
        the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
    send_count = Message.objects.filter(sender=request.user).aggregate(
        the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

    context = {

        'company': company,
        'period_selected': period_selected,
        'closing_stock': qs2,
        # 'each_closing_stock' : qs1.values(),
        'opening_stock': qo2,
        # 'each_opening_stock' : qo1.values(),
        'purchase_ledger': ld,
        'total_purchase_ledger': ldc,
        # 'specific_purchase_total' : ldsp,
        'sales_ledger': lds,
        'total_sales_ledger': ldsc,
        'indirectexp_group': lde,
        'total_indirectexp_ledger': total,
        'indirectinc_group': ldi,
        'total_indirectinc_ledger': ldsi,
        'total_direct_expenses': lddt,
        'direct_expenses_group': ldd,
        'total_direct_incomes': lddi,
        'direct_incomes': ldii,
        'gross_profit': gp,
        'nett_profit': np,
        'tradingprofit': tradingp,
        'tradingprofit2': tgp,
        'totalpl': tp,
        'totalplright': tc,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count
    }

    return render(request, 'accounting_entry/P&Lcondnsd.html', context)


@login_required
@product_1_activation
def balance_sheet_condensed_view(request, pk, pk3):
    company = get_object_or_404(Company, pk=pk)
    period_selected = get_object_or_404(PeriodSelected, pk=pk3)

    # All primary groups with nature of group is 'Liabilities'
    group_lia = LedgerGroup.objects.filter(
        company=company,
        # self_group__group_name__iexact='Primary', Nature_of_LedgerGroup__iexact='Liabilities'
        base__is_revenue__exact='No',
        base__is_debit__exact='No')

    # Getting the positive closing balances of all groups with nature of group is 'Liabilities'

    group_lia_clo = group_lia.annotate(
        closing_positive=Coalesce(Sum('positive_closing'), 0),
        closing_negative=Coalesce(Sum('negative_closing'), 0))

    # Closing balances of all groups with nature of group is 'Liabilities'
    lia_particular = group_lia_clo.annotate(
        difference=ExpressionWrapper(
            F('closing_negative') - F('closing_positive'), output_field=DecimalField()),
    )

    # Total of positive liabilities
    total_lia_positive = lia_particular.filter(difference__gte=0).aggregate(
        the_sum=Coalesce(Sum('difference'), Value(0)))['the_sum']

    # Total of negative liabilities
    total_lia_negative = lia_particular.filter(difference__lt=0).aggregate(
        the_sum=Coalesce(Sum('difference'), Value(0)))['the_sum']

    # closing stock
    ldstckcb = StockBalance.objects.filter(company=company)
    qs2 = ldstckcb.aggregate(the_sum=Coalesce(
        Sum('closing_stock'), Value(0)))['the_sum']

    # All primary groups with nature of group is 'Assets'
    group_ast = LedgerGroup.objects.filter(
        company=company,
        # , self_group__group_name__iexact='Primary', Nature_of_LedgerGroup__iexact='Assets')
        base__is_revenue__exact='No',
        base__is_debit__exact='Yes')

    # Getting the positive closing balances of all groups with nature of group is 'Assets'

    group_ast_clo = group_ast.annotate(
        closing_positive=Coalesce(Sum('positive_closing'), 0),
        closing_negative=Coalesce(Sum('negative_closing'), 0))

    # Closing balances of all groups with nature of group is 'Assets'
    ast_particular = group_ast_clo.annotate(
        difference=ExpressionWrapper(
            F('closing_positive') - F('closing_negative'), output_field=DecimalField()),
    )

    # Total of positive Assets
    total_ast_positive = ast_particular.filter(difference__gte=0).aggregate(
        the_sum=Coalesce(Sum('difference'), Value(0)))['the_sum']

    # Total of negative Assets
    total_ast_negative = ast_particular.filter(difference__lt=0).aggregate(
        the_sum=Coalesce(Sum('difference'), Value(0)))['the_sum']

    # Current asset calculation
    ca_group = LedgerGroup.objects.get(
        company=company, group_base__name__exact='Current Assets')
    total_ca = (ca_group.positive_closing -
                ca_group.negative_closing) + abs(qs2)

    # Net profit/loss
    ledger_pl = LedgerMaster.objects.get(
        company=company, ledger_name__iexact="Profit & Loss A/c")

    # From Profit and Loss
    #################################################

    # opening stock
    ldstck = StockBalance.objects.filter(company=company)
    qo2 = ldstck.aggregate(the_sum=Coalesce(
        Sum('opening_stock'), Value(0)))['the_sum']

    # purchases #debit
    ld = LedgerGroup.objects.filter(
        company=company, group_base__name__exact='Purchase Accounts')
    ldc = ld.aggregate(the_sum=Coalesce(
        Sum('group_ledger__closing_balance'), Value(0)))['the_sum']

    # Direct Expense #debit
    ldd = LedgerGroup.objects.filter(
        company=company, group_base__name__exact='Direct Expenses')
    lddt = ldd.aggregate(the_sum=Coalesce(
        Sum('group_ledger__closing_balance'), Value(0)))['the_sum']

    # Direct Income #credit
    ldii = LedgerGroup.objects.filter(
        company=company, group_base__name__exact='Direct Incomes')
    lddi = ldii.aggregate(the_sum=Coalesce(
        Sum('group_ledger__closing_balance'), Value(0)))['the_sum']

    # sales #credit
    lds = LedgerGroup.objects.filter(
        company=company, group_base__name__exact='Sales Account')
    ldsc = lds.aggregate(the_sum=Coalesce(
        Sum('group_ledger__closing_balance'), Value(0)))['the_sum']

    # Indirect Expense  #debit
    lde = LedgerGroup.objects.filter(
        company=company, group_base__name__exact='Indirect Expenses')
    ldse = lde.aggregate(the_sum=Coalesce(
        Sum('positive_closing'), Value(0)))['the_sum']
    ldsecr = lde.aggregate(the_sum=Coalesce(
        Sum('negative_closing'), Value(0)))['the_sum']
    if ldse == 0 or ldse == None:
        total = - ldsecr
    elif ldsecr == 0 or ldsecr == None:
        total = ldse
    else:
        total = ldse - ldsecr

    # Indirect Income #credit
    ldi = LedgerGroup.objects.filter(
        company=company, group_base__name__exact='Indirect Incomes')
    ldsi = ldi.aggregate(the_sum=Coalesce(
        Sum('group_ledger__closing_balance'), Value(0)))['the_sum']
    # qo1 means opening stock exists

    # lddt = Direct Expenses
    # lddi = Direct Incomes

    if lddi < 0 and lddt < 0:
        gp = abs(ldsc) + abs(qs2) + abs(lddt) - abs(qo2) - abs(ldc) - abs(lddi)
    elif lddt < 0:
        gp = abs(ldsc) + abs(qs2) + abs(lddi) + abs(lddt) - abs(qo2) - abs(ldc)
    elif lddi < 0:
        gp = abs(ldsc) + abs(qs2) - abs(lddi) - abs(qo2) - abs(ldc) - abs(lddt)
    else:
        gp = abs(ldsc) + abs(qs2) + abs(lddi) - abs(qo2) - abs(ldc) - abs(lddt)

    # total = Indirect Expense
    # ldsi = Indirect Income

    if gp >= 0:
        if ldsi < 0 and total < 0:
            np = (gp) + abs(total) - abs(ldsi)
        elif total < 0:
            np = (gp) + abs(ldsi) + abs(total)
        elif ldsi < 0:
            np = (gp) - abs(ldsi) - abs(total)
        else:
            np = (gp) + abs(ldsi) - abs(total)
    else:
        if ldsi < 0 and total < 0:
            np = abs(total) - abs(ldsi) - abs(gp)
        elif ldsi < 0:
            np = abs(ldsi) + abs(total) + abs(gp)
        elif total < 0:
            np = abs(ldsi) + abs(total) - abs(gp)
        else:
            np = abs(ldsi) - abs(total) - abs(gp)

    # Net profit/loss opening balance
    ledger_pl = LedgerMaster.objects.get(
        company=company, ledger_name__iexact="Profit & Loss A/c")
    ledger_pl_closing = ledger_pl.Balance_opening

    total_pl = np + ledger_pl_closing

    # From Trial Balance
    #################################################

    grp_debit = LedgerGroup.objects.filter(
        company=company, self_group__group_name__iexact='Primary', group_base__is_debit=True)
    grp_credit = LedgerGroup.objects.filter(
        company=company, self_group__group_name__iexact='Primary', group_base__is_debit=False)

    grp_debit_co = LedgerGroup.objects.filter(
        company=company, self_group__group_name__iexact='Primary', group_base__is_debit=True)
    grp_credit_co = LedgerGroup.objects.filter(
        company=company, self_group__group_name__iexact='Primary', group_base__is_debit=False)

    gs_debit_open = grp_debit.aggregate(the_sum=Coalesce(
        Sum('positive_opening'), Value(0)))['the_sum']
    gs_credit_op = grp_credit.aggregate(the_sum=Coalesce(
        Sum('negative_opening'), Value(0)))['the_sum']

    gs_credit_open = gs_credit_op + ledger_pl_closing

    if qo2 > 0:
        gs_debit_opening = gs_debit_open + qo2
    else:
        gs_debit_opening = gs_debit_open

    if qo2 > 0:
        gs_credit_opening = gs_credit_open
    else:
        gs_credit_opening = gs_credit_open + qo2

    gs_debit_opening_co = grp_debit_co.aggregate(
        the_sum=Coalesce(Sum('positive_opening'), Value(0)))['the_sum']
    gs_credit_opening_co = grp_credit_co.aggregate(
        the_sum=Coalesce(Sum('negative_opening'), Value(0)))['the_sum']

    gs_opening = LedgerGroup.objects.filter(
        company=company, self_group__group_name__iexact='Primary')

    gs_deb_opening = gs_opening.aggregate(the_sum=Coalesce(
        Sum('positive_opening'), Value(0)))['the_sum']
    gs_cre_opening = gs_opening.aggregate(the_sum=Coalesce(
        Sum('negative_opening'), Value(0)))['the_sum']

    if gs_debit_opening > gs_credit_opening:
        dif_ob = gs_debit_opening - gs_credit_opening
    else:
        dif_ob = gs_credit_opening - gs_debit_opening

    #######################################

    # Balance sheet total of liabilities side
    if total_lia_positive or total_ast_negative:
        if total_ca < 0:
            if total_pl >= 0:
                total_liabilities_1 = abs(
                    total_lia_positive) + abs(total_ast_negative) + abs(total_pl) + abs(qs2)
            else:
                total_liabilities_1 = abs(
                    total_lia_positive) + abs(total_ast_negative)
        else:
            if total_pl >= 0:
                total_liabilities_1 = abs(
                    total_lia_positive) + abs(total_pl) + abs(total_ast_negative)
            else:
                total_liabilities_1 = abs(
                    total_lia_positive) + abs(total_ast_negative) + abs(qs2)

    else:
        total_liabilities_1 = 0

    # Balance sheet total of assets side
    if total_lia_negative or total_ast_positive:
        if total_ca > 0:
            if total_pl < 0:
                total_asset_1 = abs(total_lia_negative) + \
                    abs(total_ast_positive) + abs(total_pl)
            else:
                total_asset_1 = abs(total_lia_negative) + \
                    abs(total_ast_positive) + abs(qs2)
        else:
            if total_pl < 0:
                total_asset_1 = abs(
                    total_lia_negative) + abs(total_ast_positive) + abs(total_pl) + abs(qs2)
            else:
                total_asset_1 = abs(total_lia_negative) + \
                    abs(total_ast_positive)
    else:
        total_asset_1 = 0

    if gs_debit_opening > gs_credit_opening:
        dif_ob = gs_debit_opening - gs_credit_opening
        total_liabilities = total_liabilities_1 + dif_ob
        total_asset = total_asset_1
    else:
        dif_ob = gs_debit_opening - gs_credit_opening
        total_liabilities = total_liabilities_1
        total_asset = total_asset_1 + dif_ob

    inbox = Message.objects.filter(reciever=request.user)
    inbox_count = inbox.aggregate(
        the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
    send_count = Message.objects.filter(sender=request.user).aggregate(
        the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

    context = {

        'company': company,
        'period_selected': period_selected,

        'lia_particular': lia_particular,
        'ast_particular': ast_particular,
        'closing_stock': abs(qs2),
        'total_ca': total_ca,

        'ledger_pl': ledger_pl,

        'dif_ob': dif_ob,
        'gs_debit_opening': gs_debit_opening,
        'gs_credit_opening': gs_credit_opening,

        'np': np,
        'total_pl': total_pl,

        'total_asset': total_asset,
        'total_liabilities': total_liabilities,

        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count
    }

    return render(request, 'accounting_entry/balance_sheet.html', context)


@login_required
@product_1_activation
def trial_balance_condensed_view(request, company_pk, period_selected_pk):
    """
    View to calculate trial balance for selected date range
    """

    company = get_object_or_404(Company, pk=company_pk)
    period_selected = get_object_or_404(PeriodSelected, pk=period_selected_pk)

    # Opening Stock
    Stock_item_list = StockItem.objects.filter(company=company)
    total_purchase_stock_in_range = PurchaseStock.objects.filter(purchase_voucher__voucher_date__lt=period_selected.start_date).values('stock_item')
    total_sales_stock_in_range = SaleStock.objects.filter(sale_voucher__voucher_date__lt=period_selected.start_date).values('stock_item')
    total_debit_note_stock_in_range = DebitNoteStock.objects.filter(debit_note__voucher_date__lt=period_selected.start_date).values('stock_item')
    total_credit_note_stock_in_range = CreditNoteStock.objects.filter(credit_note__voucher_date__lt=period_selected.start_date).values('stock_item')

    stock_item_quantity = Stock_item_list.aggregate(the_sum=Coalesce(Sum('quantity'), Value(0)))['the_sum']

    stock_item_opening = Stock_item_list.aggregate(the_sum=Coalesce(Sum('opening'), Value(0)))['the_sum']

    total_purchase_quantity = total_purchase_stock_in_range.aggregate(the_sum=Coalesce(Sum('quantity'), Value(0)))['the_sum']

    total_purchase_stock = total_purchase_stock_in_range.aggregate(the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']

    total_sales_quantity = total_sales_stock_in_range.aggregate(the_sum=Coalesce(Sum('quantity'), Value(0)))['the_sum']

    total_debitnote_quantity = total_debit_note_stock_in_range.aggregate(the_sum=Coalesce(Sum('quantity'), Value(0)))['the_sum']

    total_debit_note = total_debit_note_stock_in_range.aggregate(the_sum=Coalesce(Sum('total'), Value(0)))['the_sum']

    total_creditnote_quantity = total_credit_note_stock_in_range.aggregate(the_sum=Coalesce(Sum('quantity'), Value(0)))['the_sum']

    if not total_purchase_quantity:
        total_purchase_quantity = 0

    if not total_purchase_stock:
        total_purchase_stock = 0

    if not total_sales_quantity:
        total_sales_quantity = 0

    if not total_debitnote_quantity:
        total_debitnote_quantity = 0

    if not total_debit_note:
        total_debit_note = 0

    if not total_debit_note:
        total_debit_note = 0

    if not total_creditnote_quantity:
        total_creditnote_quantity = 0

    total_purchase_quantity_os = total_purchase_quantity - total_debitnote_quantity
    total_purchase_os = total_purchase_stock - total_debit_note

    total_sales_quantity_os = total_sales_quantity - total_creditnote_quantity

    if not stock_item_quantity:
        opening_quantity = (total_purchase_quantity - (total_debitnote_quantity + total_sales_quantity_os))
    else:
        opening_quantity = stock_item_quantity + (total_purchase_quantity - (total_debitnote_quantity + total_sales_quantity_os))

    if total_purchase_quantity_os != 0 and opening_quantity != 0 and total_purchase_os != 0:
        opening_stock = stock_item_opening + (((total_purchase_os) / (total_purchase_quantity_os)) * opening_quantity)  # for weighted average
    else:
        # opening_stock = stock_item_opening + (((total_purchase_os) / (total_purchase_quantity_os)) * opening_quantity)  # for weighted average
        opening_stock = stock_item_opening

    if not opening_stock:
        opening_stock = 0


    # All Journal Queries for groups
    journals_debit_opening = JournalVoucher.objects.filter(company=company, dr_ledger__ledger_group=OuterRef(
        'pk'), voucher_date__lt=period_selected.start_date).values('dr_ledger__ledger_group')

    journals_credit_opening = JournalVoucher.objects.filter(company=company, cr_ledger__ledger_group=OuterRef(
        'pk'), voucher_date__lt=period_selected.start_date).values('cr_ledger__ledger_group')

    journals_debit_opening_master = JournalVoucher.objects.filter(company=company, dr_ledger__ledger_group__self_group=OuterRef(
        'pk'), voucher_date__lt=period_selected.start_date).values('dr_ledger__ledger_group__self_group')

    journals_credit_opening_master = JournalVoucher.objects.filter(company=company, cr_ledger__ledger_group__self_group=OuterRef(
        'pk'), voucher_date__lt=period_selected.start_date).values('cr_ledger__ledger_group__self_group')

    journals_debit = JournalVoucher.objects.filter(company=company, dr_ledger__ledger_group=OuterRef(
        'pk'), voucher_date__gte=period_selected.start_date, voucher_date__lte=period_selected.end_date).values('dr_ledger__ledger_group')

    journals_credit = JournalVoucher.objects.filter(company=company, cr_ledger__ledger_group=OuterRef(
        'pk'), voucher_date__gte=period_selected.start_date, voucher_date__lte=period_selected.end_date).values('cr_ledger__ledger_group')

    # All Journal Queries for all master groups
    journals_debit_master = JournalVoucher.objects.filter(company=company, dr_ledger__ledger_group__self_group=OuterRef(
        'pk'), voucher_date__gte=period_selected.start_date, voucher_date__lte=period_selected.end_date).values('dr_ledger__ledger_group__self_group')
    journals_credit_master = JournalVoucher.objects.filter(company=company, cr_ledger__ledger_group__self_group=OuterRef(
        'pk'), voucher_date__gte=period_selected.start_date, voucher_date__lte=period_selected.end_date).values('cr_ledger__ledger_group__self_group')

    # Annotating values of every journal query for Group Value
    total_debit_opening = journals_debit_opening.annotate(
        total=Coalesce(Sum('amount'), Value(0))).values('total')
    total_credit_opening = journals_credit_opening.annotate(
        total=Sum('amount')).values('total')
    total_debit = journals_debit.annotate(total=Coalesce(Sum('amount'), Value(0))).values('total')
    total_credit = journals_credit.annotate(
        total=Sum('amount')).values('total')


    # Annotating values of every journal query for Master Group Value
    total_debit_master = journals_debit_master.annotate(
        total=Sum('amount')).values('total')
    total_credit_master = journals_credit_master.annotate(
        total=Sum('amount')).values('total')
    total_debit_opening_master = journals_debit_opening_master.annotate(
        total=Sum('amount')).values('total')
    total_credit_opening_master = journals_credit_opening_master.annotate(
        total=Sum('amount')).values('total')


    # All ledger queries for finding the opening balance
    ledgers_debit = LedgerMaster.objects.filter(
        company=company, ledger_group=OuterRef('pk'),ledger_group__group_base__is_debit='Yes').values('ledger_group')
    ledgers_credit = LedgerMaster.objects.filter(
        company=company, ledger_group=OuterRef('pk'),ledger_group__group_base__is_debit='No').values('ledger_group')

    ledgers_debit_self_master = LedgerMaster.objects.filter(
        company=company, ledger_group__self_group=OuterRef('pk'),ledger_group__group_base__is_debit='Yes').values('ledger_group__self_group')
    ledgers_credit_self_master = LedgerMaster.objects.filter(
        company=company, ledger_group__self_group=OuterRef('pk'),ledger_group__group_base__is_debit='No').values('ledger_group__self_group')

    total_ledger_debit = ledgers_debit.annotate(
        total=Sum('opening_balance')).values('total')

    total_ledger_credit = ledgers_credit.annotate(
        total=Sum('opening_balance')).values('total')

    total_ledger_debit_master = ledgers_debit_self_master.annotate(
        total=Sum('opening_balance')).values('total')

    total_ledger_credit_master = ledgers_credit_self_master.annotate(
        total=Sum('opening_balance')).values('total')



    # Quering all the Primary Groups with their respective Debit and Credit Balances
    groups = LedgerGroup.objects.filter(company=company, self_group__group_name__iexact='Primary').annotate(
        debit_balance=Coalesce(Subquery(total_debit,
                               output_field=FloatField()),Value(0)),
        debit_balance_master=Coalesce(Subquery(total_debit_master,
                                      output_field=FloatField()),Value(0)),
        credit_balance=Coalesce(Subquery(total_credit,
                                output_field=FloatField()),Value(0)),
        credit_balance_master=Coalesce(Subquery(total_credit_master,
                                       output_field=FloatField()),Value(0)),
        credit_balance_opening=Coalesce(Subquery(total_credit_opening,
                                        output_field=FloatField()),Value(0)),
        credit_balance_opening_master=Coalesce(Subquery(total_credit_opening_master,
                                       output_field=FloatField()),Value(0)),
        debit_balance_opening=Coalesce(Subquery(total_debit_opening,
                                       output_field=FloatField()),Value(0)),
        debit_balance_opening_master=Coalesce(Subquery(total_debit_opening_master,
                                       output_field=FloatField()),Value(0)),
        opening_total=Coalesce(Sum('group_ledger__opening_balance'), Value(0)),
        opening_total_master=Coalesce(Sum('master_group__group_ledger__opening_balance'), Value(0)),

    )

    group_list = groups.annotate(
        total_debit_opening_final = Case(
            When(group_base__is_debit='Yes', then=F('debit_balance_opening_master') + F('debit_balance_opening') + F('opening_total') + F('opening_total_master')),
            When(group_base__is_debit='No', then=F('debit_balance_opening_master') + F('debit_balance_opening')),
            default=None,
            output_field=FloatField()
            ),
        total_credit_opening_final = Case(
            When(group_base__is_debit='Yes', then=F('credit_balance_opening_master') + F('credit_balance_opening')),
            When(group_base__is_debit='No', then=F('credit_balance_opening_master') + F('credit_balance_opening') + F('opening_total') + F('opening_total_master')),
            default=None,
            output_field=FloatField()
            ),
        total_debit_closing_final = Case(
            When(group_base__is_debit='Yes', then=F('debit_balance') + F('debit_balance_master') + F('opening_total') + F('opening_total_master')),
            When(group_base__is_debit='No', then=F('debit_balance') + F('debit_balance_master')),
            default=None,
            output_field=FloatField()
            ),
        total_credit_closing_final = Case(
            When(group_base__is_debit='No', then=F('credit_balance') + F('credit_balance_master') + F('opening_total') + F('opening_total_master')),
            When(group_base__is_debit='Yes', then=F('credit_balance') + F('credit_balance_master')),
            default=None,
            output_field=FloatField()
            ),
        )
    # Aggregating the Total Balances With their respective positive and negative balances
    grand_total_debit_opening_positive = group_list.filter(total_debit_opening_final__gt=0).aggregate(the_sum=Coalesce(Sum('total_debit_opening_final'), Value(0)))['the_sum']
    grand_total_debit_opening_negative = group_list.filter(total_debit_opening_final__lt=0).aggregate(the_sum=Coalesce(Sum('total_debit_opening_final'), Value(0)))['the_sum']
    grand_total_credit_opening_positive = group_list.filter(total_credit_opening_final__gt=0).aggregate(the_sum=Coalesce(Sum('total_credit_opening_final'), Value(0)))['the_sum']
    grand_total_credit_opening_negative = group_list.filter(total_credit_opening_final__lt=0).aggregate(the_sum=Coalesce(Sum('total_credit_opening_final'), Value(0)))['the_sum']

    grand_total_debit_closing_positive = group_list.filter(total_debit_closing_final__gt=0).aggregate(the_sum=Coalesce(Sum('total_debit_closing_final'), Value(0)))['the_sum']
    grand_total_debit_closing_negative = group_list.filter(total_debit_closing_final__lt=0).aggregate(the_sum=Coalesce(Sum('total_debit_closing_final'), Value(0)))['the_sum']
    grand_total_credit_closing_positive = group_list.filter(total_credit_closing_final__gt=0).aggregate(the_sum=Coalesce(Sum('total_credit_closing_final'), Value(0)))['the_sum']
    grand_total_credit_closing_negative = group_list.filter(total_credit_closing_final__lt=0).aggregate(the_sum=Coalesce(Sum('total_credit_closing_final'), Value(0)))['the_sum']

    grand_total_debit_opening = decimal.Decimal(grand_total_debit_opening_positive) + decimal.Decimal(abs(grand_total_credit_opening_negative))
    grand_total_credit_opening = decimal.Decimal(grand_total_credit_opening_positive) + decimal.Decimal(abs(grand_total_debit_opening_negative))
    grand_total_debit_closing = decimal.Decimal(grand_total_debit_closing_positive) + decimal.Decimal(abs(grand_total_credit_closing_negative))
    grand_total_credit_closing = decimal.Decimal(grand_total_credit_closing_positive) + decimal.Decimal(abs(grand_total_debit_closing_negative))


    # Grand Total For Current Asset Group calculated for Opening Stock Calculation
    total_current_asset_debit_before_stock_opening = group_list.filter(group_name__exact='Current Assets').aggregate(the_sum=Coalesce(Sum('total_debit_opening_final'), Value(0)))['the_sum']
    total_current_asset_credit_before_stock_opening = group_list.filter(group_name__exact='Current Assets').aggregate(the_sum=Coalesce(Sum('total_credit_opening_final'), Value(0)))['the_sum']
    total_current_asset_debit_before_stock_closing = group_list.filter(group_name__exact='Current Assets').aggregate(the_sum=Coalesce(Sum('total_debit_closing_final'), Value(0)))['the_sum']
    total_current_asset_credit_before_stock_closing = group_list.filter(group_name__exact='Current Assets').aggregate(the_sum=Coalesce(Sum('total_credit_closing_final'), Value(0)))['the_sum']

    # Current Asset Totals for template rendering
    if opening_stock > 0:
        total_current_asset_opening_debit = decimal.Decimal(total_current_asset_debit_before_stock_opening) + opening_stock
        total_current_asset_opening_credit = decimal.Decimal(total_current_asset_credit_before_stock_opening)
        total_current_asset_closing_debit = decimal.Decimal(total_current_asset_debit_before_stock_closing) + opening_stock
        total_current_asset_closing_credit = decimal.Decimal(total_current_asset_credit_before_stock_closing)
    else:
        total_current_asset_opening_debit = decimal.Decimal(total_current_asset_debit_before_stock_opening) 
        total_current_asset_opening_credit = decimal.Decimal(total_current_asset_credit_before_stock_opening) + opening_stock
        total_current_asset_closing_debit = decimal.Decimal(total_current_asset_debit_before_stock_closing) 
        total_current_asset_closing_credit = decimal.Decimal(total_current_asset_credit_before_stock_closing) + opening_stock

    # Grand total before Diffrence in opening balance calculation
    if opening_stock > 0:
        grand_total_debit_opening_with_stock = decimal.Decimal(grand_total_debit_opening) + opening_stock
        grand_total_credit_opening_with_stock = decimal.Decimal(grand_total_credit_opening) 
        grand_total_debit_closing_with_stock = decimal.Decimal(grand_total_debit_closing) + opening_stock
        grand_total_credit_closing_with_stock = decimal.Decimal(grand_total_credit_closing)
    else:
        grand_total_debit_opening_with_stock = decimal.Decimal(grand_total_debit_opening) 
        grand_total_credit_opening_with_stock = decimal.Decimal(grand_total_credit_opening) + opening_stock
        grand_total_debit_closing_with_stock = decimal.Decimal(grand_total_debit_closing) 
        grand_total_credit_closing_with_stock = decimal.Decimal(grand_total_credit_closing) + opening_stock


    # Diffrence in opening balance calculation
    if grand_total_debit_opening_with_stock > grand_total_credit_opening_with_stock:
        difference_in_opening_balance = decimal.Decimal(grand_total_debit_opening_with_stock) - decimal.Decimal(grand_total_credit_opening_with_stock)
        grand_total_debit_opening_final = decimal.Decimal(grand_total_debit_opening_with_stock)
        grand_total_credit_opening_final = decimal.Decimal(grand_total_credit_opening_with_stock) + decimal.Decimal(abs(difference_in_opening_balance))
        grand_total_debit_closing_final = decimal.Decimal(grand_total_debit_closing_with_stock)
        grand_total_credit_closing_final = decimal.Decimal(grand_total_credit_closing_with_stock) + decimal.Decimal(abs(difference_in_opening_balance))
    else:
        difference_in_opening_balance = decimal.Decimal(grand_total_debit_opening_with_stock) - decimal.Decimal(grand_total_credit_opening_with_stock)
        grand_total_debit_opening_final = decimal.Decimal(grand_total_debit_opening_with_stock) + decimal.Decimal(abs(difference_in_opening_balance))
        grand_total_credit_opening_final = decimal.Decimal(grand_total_credit_opening_with_stock) 
        grand_total_debit_closing_final = decimal.Decimal(grand_total_debit_closing_with_stock) + decimal.Decimal(abs(difference_in_opening_balance))
        grand_total_credit_closing_final = decimal.Decimal(grand_total_credit_closing_with_stock)

    

    
    context = {
        'company': company,
        'period_selected': period_selected,
        'groups': group_list,
        'opening_stock' : opening_stock,
        'grand_total_debit_opening_with_stock' : grand_total_debit_opening_with_stock,
        'grand_total_credit_opening_with_stock' : grand_total_credit_opening_with_stock,
        'difference_in_opening_balance' : difference_in_opening_balance,
        'grand_total_debit_opening_final' : grand_total_debit_opening_final,
        'grand_total_credit_opening_final' : grand_total_credit_opening_final,
        'grand_total_debit_closing_final' : grand_total_debit_closing_final,
        'grand_total_credit_closing_final' : grand_total_credit_closing_final,
        'total_current_asset_opening_debit' : total_current_asset_opening_debit,
        'total_current_asset_opening_credit' : total_current_asset_opening_credit,
        'total_current_asset_closing_debit' : total_current_asset_closing_debit,
        'total_current_asset_closing_credit' : total_current_asset_closing_credit

    }

    return render(request, 'accounting_entry/trial_bal_condendensed.html', context)
