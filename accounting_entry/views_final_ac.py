"""
Views for Final Account and related statements
"""
from django.shortcuts import get_object_or_404, render
from django.db.models.functions import Coalesce
from django.db.models import Count, Value, Sum, ExpressionWrapper, Q, F
from django.db.models.fields import DecimalField
from django.contrib.auth.decorators import login_required
from company.models import Company
from messaging.models import Message
from ecommerce_integration.decorators import product_1_activation
from stock_keeping.models import StockBalance
from .models import PeriodSelected, LedgerGroup, LedgerMaster


@login_required
@product_1_activation
def profit_and_loss_condensed_view(request, company_pk, period_selected_pk):
    company = get_object_or_404(Company, pk=company_pk)
    period_selected = get_object_or_404(PeriodSelected, pk=period_selected_pk)

    # closing stock
    ldstckcb = StockBalance.objects.filter(company=company)
    qs2 = ldstckcb.aggregate(the_sum=Coalesce(
        Sum('closing_stock'), Value(0)))['the_sum']

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
        Sum('negative_closing'), Value(0)))['the_sum']

    # Indirect Expense  #debit
    lde = LedgerGroup.objects.filter(
        company=company, group_base__name__exact='Indirect Expenses')
    total = lde.aggregate(the_sum=Coalesce(
        Sum('group_ledger__closing_balance'), Value(0)))['the_sum']
    # ldsecr = lde.aggregate(the_sum=Coalesce(Sum('negative_closing'), Value(0)))['the_sum']
    # if ldse == 0 or ldse == None:
    #     total = - ldsecr
    # elif ldsecr == 0 or ldsecr == None:
    #     total = ldse
    # else:
    #     total = ldse - ldsecr

    # Indirect Income #credit
    ldi = LedgerGroup.objects.filter(
        company=company, group_base__name__exact='Indirect Incomes')
    ldsi = ldi.aggregate(the_sum=Coalesce(
        Sum('group_ledger__closing_balance'), Value(0)))['the_sum']
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
        'closing_stock_items': ldstckcb,
        'closing_stock': qs2,
        # 'each_closing_stock' : qs1.values(),
        'opening_stock': qo2,
        'opening_stock_items': ldstck,
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
def trial_balance_condensed_view(request, company_pk, period_selected_pk):
    company = get_object_or_404(Company, pk=company_pk)
    period_selected = get_object_or_404(PeriodSelected, pk=period_selected_pk)

    # opening stock
    ldstck = StockBalance.objects.filter(company=company)
    qo2 = ldstck.aggregate(the_sum=Coalesce(
        Sum('opening_stock'), Value(0)))['the_sum']

    grp_debit = LedgerGroup.objects.filter(
        company=company, Master__group_Name__iexact='Primary', balance_nature__iexact='Debit')
    grp_credit = LedgerGroup.objects.filter(
        company=company, Master__group_Name__iexact='Primary', balance_nature__iexact='Credit')

    grp_debit_co = LedgerGroup.objects.filter(
        company=company, Master__group_Name__iexact='Primary', balance_nature__iexact='Debit')
    grp_credit_co = LedgerGroup.objects.filter(
        company=company, Master__group_Name__iexact='Primary', balance_nature__iexact='Credit')

    gs_debit_open = grp_debit.aggregate(the_sum=Coalesce(
        Sum('positive_opening'), Value(0)))['the_sum']
    gs_credit_op = grp_credit.aggregate(the_sum=Coalesce(
        Sum('negative_opening'), Value(0)))['the_sum']

    # Net profit/loss opening balance
    ledger_pl = LedgerMaster.objects.get(
        company=company, ledger_name__iexact="Profit & Loss A/c")
    ledger_pl_closing = ledger_pl.Balance_opening

    gs_credit_open = gs_credit_op + ledger_pl_closing

    print(gs_credit_open)

    if qo2 > 0:
        gs_debit_opening = gs_debit_open + qo2
        gs_credit_opening = gs_credit_open
    else:
        gs_debit_opening = gs_debit_open
        gs_credit_opening = gs_credit_open + qo2

    gs_debit_opening_co = grp_debit_co.aggregate(
        the_sum=Coalesce(Sum('positive_opening'), Value(0)))['the_sum']
    gs_credit_opening_co = grp_credit_co.aggregate(
        the_sum=Coalesce(Sum('negative_opening'), Value(0)))['the_sum']
    print(gs_credit_opening_co)

    gs_opening = LedgerGroup.objects.filter(
        company=company, Master__group_Name__iexact='Primary')

    gs_deb_opening = gs_opening.aggregate(the_sum=Coalesce(
        Sum('positive_opening'), Value(0)))['the_sum']
    gs_cre_opening = gs_opening.aggregate(the_sum=Coalesce(
        Sum('negative_opening'), Value(0)))['the_sum']

    if gs_debit_opening > gs_credit_opening:
        dif_ob = gs_debit_opening - gs_credit_opening
        total_deb = gs_debit_opening
        total_ceb = gs_credit_opening + abs(dif_ob)
    else:
        dif_ob = gs_credit_opening - gs_debit_opening
        total_deb = gs_debit_opening + abs(dif_ob)
        total_ceb = gs_credit_opening

    print(gs_debit_opening)
    print(gs_credit_opening)
    print(dif_ob)

    gs = LedgerGroup.objects.filter(company=company, Master__group_Name__iexact='Primary').exclude(Q(group_Name__iexact="Stock-in-hand") | Q(group_Name__iexact="Sales Accounts") | Q(
        group_base__name__exact="Purchase Accounts") | Q(group_Name__iexact="Indirect Expenses") | Q(group_Name__iexact="Indirect Incomes") | Q(group_Name__iexact="Direct Incomes") | Q(group_Name__iexact="Direct Expenses"))

    gs_deb_notstock = gs.aggregate(the_sum=Coalesce(
        Sum('positive_closing'), Value(0)))['the_sum']
    gs_cre_notstock = gs.aggregate(the_sum=Coalesce(
        Sum('negative_closing'), Value(0)))['the_sum']

    if qo2 > 0:
        gs_deb = gs_deb_notstock + qo2
        gs_cre = gs_cre_notstock
    else:
        gs_deb = gs_deb_notstock
        gs_cre = gs_cre_notstock + qo2

    # purchases
    gs_purchase = LedgerGroup.objects.filter(
        company=company, group_base__name__exact="Purchase Accounts")
    gs_purchase_total = gs_purchase.aggregate(the_sum=Coalesce(
        Sum('group_ledger__closing_balance'), Value(0)))['the_sum']

    # sales
    gs_sales = LedgerGroup.objects.filter(
        company=company, group_base__name__exact="Sales Accounts")
    gs_sales_total = gs_sales.aggregate(the_sum=Coalesce(
        Sum('group_ledger__closing_balance'), Value(0)))['the_sum']

    # Direct Expense
    gs_directexp = LedgerGroup.objects.filter(
        company=company, group_base__name__exact="Direct Expenses")
    gs_directexp_total = gs_directexp.aggregate(the_sum=Coalesce(
        Sum('group_ledger__closing_balance'), Value(0)))['the_sum']

    # Direct Income
    gs_directinc = LedgerGroup.objects.filter(
        company=company, group_base__name__exact="Direct Incomes")
    gs_directinc_total = gs_directinc.aggregate(the_sum=Coalesce(
        Sum('group_ledger__closing_balance'), Value(0)))['the_sum']

    # Indirect Expense
    gs_indirectexp = LedgerGroup.objects.filter(
        company=company, group_base__name__exact="Indirect Expenses")
    gs_indirectexp_total = gs_indirectexp.aggregate(
        the_sum=Coalesce(Sum('positive_closing'), Value(0)))['the_sum']
    gs_indirectexp_total_neg = gs_indirectexp.aggregate(
        the_sum=Coalesce(Sum('negative_closing'), Value(0)))['the_sum']

    # Indirect Income
    gs_indirectinc = LedgerGroup.objects.filter(
        company=company, group_base__name__exact="Indirect Incomes")
    gs_indirectinc_total = gs_indirectinc.aggregate(the_sum=Coalesce(
        Sum('group_ledger__closing_balance'), Value(0)))['the_sum']

    # Net profit/loss
    ledger_pl = LedgerMaster.objects.get(
        company=company, ledger_name__iexact="Profit & Loss A/c")
    ledger_pl_closing = ledger_pl.Balance_opening

    if ledger_pl_closing <= 0:
        gs_debit = gs_deb + abs(ledger_pl_closing) + gs_purchase_total + \
            gs_directexp_total + gs_indirectexp_total
        gs_credit = gs_cre + gs_sales_total + gs_directinc_total + gs_indirectinc_total
    else:
        gs_debit = gs_deb + gs_purchase_total + \
            gs_directexp_total + gs_indirectexp_total
        gs_credit = gs_cre + ledger_pl_closing + gs_sales_total + \
            gs_directinc_total + gs_indirectinc_total

    if gs_debit > gs_credit:
        difference_ob = gs_debit_opening - gs_credit_opening
        total_credit = gs_credit + abs(difference_ob)
        total_debit = gs_debit
    else:
        difference_ob = gs_credit_opening - gs_debit_opening
        total_credit = gs_credit
        total_debit = gs_debit + abs(difference_ob)

    inbox = Message.objects.filter(reciever=request.user)
    inbox_count = inbox.aggregate(
        the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
    send_count = Message.objects.filter(sender=request.user).aggregate(
        the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

    context = {
        'company': company,
        'period_selected': period_selected,
        'qo2': qo2,
        'gs_deb_opening': gs_debit_opening,
        'gs_cre_opening': gs_credit_opening,
        'dif_ob': dif_ob,
        'total_deb': total_deb,
        'total_ceb': total_ceb,
        'groups_list': gs,
        'ledger_pl': ledger_pl,
        'gs_purchase': gs_purchase,
        'gs_purchase_total': gs_purchase_total,
        'gs_sales': gs_sales,
        'gs_sales_total': gs_sales_total,
        'gs_directexp': gs_directexp,
        'gs_directexp_total': gs_directexp_total,
        'gs_directinc': gs_directinc,
        'gs_directinc_total': gs_directinc_total,
        'gs_indirectinc': gs_indirectinc,
        'gs_indirectinc_total': gs_indirectinc_total,
        'gs_indirectexp': gs_indirectexp,
        'gs_indirectexp_total': gs_indirectexp_total,
        'ledger_pl_closing': ledger_pl_closing,
        'difference_ob': difference_ob,
        'gs_debit': gs_debit,
        'gs_credit': gs_credit,
        'total_debit': total_debit,
        'total_credit': total_credit,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count
    }

    return render(request, 'accounting_entry/trial_bal_condendensed.html', context)


@login_required
@product_1_activation
def balance_sheet_condensed_view(request, pk, pk3):
    company = get_object_or_404(Company, pk=pk)
    period_selected = get_object_or_404(PeriodSelected, pk=pk3)

    # All primary groups with nature of group is 'Liabilities'
    group_lia = LedgerGroup.objects.filter(
        company=company,
        # Master__group_Name__iexact='Primary', Nature_of_LedgerGroup__iexact='Liabilities'
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
        # , Master__group_Name__iexact='Primary', Nature_of_LedgerGroup__iexact='Assets')
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
        company=company, Master__group_Name__iexact='Primary', balance_nature__iexact='Debit')
    grp_credit = LedgerGroup.objects.filter(
        company=company, Master__group_Name__iexact='Primary', balance_nature__iexact='Credit')

    grp_debit_co = LedgerGroup.objects.filter(
        company=company, Master__group_Name__iexact='Primary', balance_nature__iexact='Debit')
    grp_credit_co = LedgerGroup.objects.filter(
        company=company, Master__group_Name__iexact='Primary', balance_nature__iexact='Credit')

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
        company=company, Master__group_Name__iexact='Primary')

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
