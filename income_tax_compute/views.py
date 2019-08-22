"""
Income Tax Computaion View
"""
import math
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models.functions import Coalesce
from django.db.models import Count, Value, Sum
from django.template.loader import render_to_string
from django.http import JsonResponse, Http404
from django.urls import reverse
from django.shortcuts import redirect
from accounting_entry.models import JournalVoucher, LedgerMaster, PeriodSelected
from messaging.models import Message
from company.models import Company
from ecommerce_integration.decorators import product_1_activation
from .models import IncomeTax, get_default_assesment_year, get_choice_assesment_year
from .forms import get_income_tax_choose_ledger_dynamic_form, IncomeTaxChooseYearForm


@login_required
@product_1_activation
def income_tax_detail_view(request, company_pk, period_selected_pk, period):
    """
    Income Tax Details View (Primary View)
    """
    company = get_object_or_404(Company, pk=company_pk)
    period_selected = get_object_or_404(PeriodSelected, pk=period_selected_pk)
    # returning financial year instead of assesment year as requested
    if period == "0000-0000":
        assesment_year = get_default_assesment_year()
    else:
        assesment_year = period

    if (assesment_year, assesment_year) not in get_choice_assesment_year():
        raise Http404("Not a valid period supplied")

    if not IncomeTax.objects.filter(company=company, assesment_year=assesment_year).exists():
        instance = IncomeTax(
            user=request.user,
            company=company,
            assesment_year=assesment_year
        )
        instance.save()

    record = IncomeTax.objects.get(
        company=company, assesment_year=assesment_year)
    record.salary_gross = record.salary + \
        record.salary_allowence + record.salary_taxable_perqisite
    record.salary_deduction_us16 = record.salary_prof_tax + record.salary_entmnt_allowance
    record.salary_total = record.salary_gross - record.salary_deduction_us16
    record.house_property_total = record.house_property_net_adjusted - \
        record.house_property_deduction_us24
    record.profit_gain_total = record.profit_gain_net_profit + \
        record.profit_gain_income_not_allowable - \
        record.profit_gain_expense_not_allowable - \
        record.profit_gain_income_exempt + \
        record.profit_gain_income_skiped
    record.capital_gain_total = record.capital_gain_net - record.capital_gain_exempt
    record.other_income_total = record.other_income_gross - \
        record.other_income_deduction_us57
    record.total_income_1_2_3_4_5 = record.salary_total + \
        record.house_property_total + \
        record.profit_gain_total + \
        record.capital_gain_total + \
        record.other_income_total
    record.gross_total_income = record.total_income_1_2_3_4_5 - \
        record.adjustment_setoff_loss
    net_income_rounded_10 = math.floor(
        record.gross_total_income - record.deduction_80c_80u)
    mod_val = net_income_rounded_10 % 10
    if mod_val < 5:
        net_income_rounded_10 -= mod_val
    else:
        net_income_rounded_10 += 10-mod_val
    record.net_income = net_income_rounded_10

    record.Balance = record.tax_on_net_income - record.rebate
    record.tax_and_surcharge = record.Balance + record.surcharge
    record.prepaid_taxes = record.tds + \
        record.advance_tax + record.self_assessment_tax
    record.tax_liability_refund = record.tax_and_surcharge + \
        record.education_cess - record.prepaid_taxes
    record.save()

    inbox = Message.objects.filter(reciever=request.user)
    inbox_count = inbox.aggregate(
        the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
    send_count = Message.objects.filter(sender=request.user).aggregate(
        the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

    context = {
        'IncomeTaxRecord': record,
        'company': company,
        'period_selected': period_selected,
        'last_period': period,
        'inbox': inbox,
        'inbox_count': inbox_count,
        'send_count': send_count,
        'selectdate': PeriodSelected.objects.filter(user=request.user),
    }

    return render(request, 'income_tax_compute/income_tax_details.html', context)


@login_required
@product_1_activation
def income_tax_value_update(request, company_pk, period_selected_pk, instance_id, field):
    """
    View for ledger selection along with amount for a particular item in income tax computation head
    """
    company = get_object_or_404(Company, pk=company_pk)
    period_selected = get_object_or_404(PeriodSelected, pk=period_selected_pk)
    income_tax_instance = get_object_or_404(IncomeTax, id=instance_id)
    data = dict()

    if request.method == 'POST':
        IncomeTaxChooseLedgerForm = get_income_tax_choose_ledger_dynamic_form(
            field)
        form = IncomeTaxChooseLedgerForm(
            request.POST, instance=income_tax_instance, company=company)
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    else:
        IncomeTaxChooseLedgerForm = get_income_tax_choose_ledger_dynamic_form(
            field)
        form = IncomeTaxChooseLedgerForm(
            instance=income_tax_instance, company=company)

    # ledger balance voucher_date
    ledger_bal_date = income_tax_instance.assesment_year[5:]+'-03-31'  # last voucher_date of the period
    # ledger_bal_date = period_selected.end_date.strftime("%Y-%m-%d")
    context = {
        'form': form,
        'company': company,
        'period_selected': period_selected,
        'ledger_bal_date': ledger_bal_date,
        'field': field
    }
    data['html_form'] = render_to_string(
        'income_tax_compute/choose_ledger.html', context, request=request)

    return JsonResponse(data)


@login_required
@product_1_activation
def get_ledger_value(request):
    """
    View to handle AJAX call to return ledger balance based on the parameter supplied
    """
    company_id = request.GET.get('company_id', None)
    ledger_bal_date = request.GET.get('ledger_bal_date', None)
    ledger_id = request.GET.get('ledger_id', None)

    company = get_object_or_404(Company, pk=company_id)
    ledger_master = get_object_or_404(LedgerMaster, pk=ledger_id)

    dr_tran = JournalVoucher.objects.filter(
        company=company, dr_ledger=ledger_master.pk, voucher_date__lte=ledger_bal_date).order_by('voucher_date')
    cr_tran = JournalVoucher.objects.filter(
        company=company, cr_ledger=ledger_master.pk, voucher_date__lte=ledger_bal_date).order_by('voucher_date')

    total_debit = dr_tran.aggregate(
        the_sum=Coalesce(Sum('amount'), Value(0)))['the_sum']
    total_credit = cr_tran.aggregate(
        the_sum=Coalesce(Sum('amount'), Value(0)))['the_sum']

    if ledger_master.ledger_group.base.is_debit == 'Yes':
        opening_balance = ledger_master.opening_balance + total_debit - total_credit
    else:
        opening_balance = ledger_master.opening_balance + total_credit - total_debit

    data = {
        'balance': opening_balance
    }
    return JsonResponse(data)


@login_required
@product_1_activation
def income_tax_year_update(request, company_pk, period_selected_pk, last_period):
    """
    View for financial/assesment year selection
    """
    company = get_object_or_404(Company, pk=company_pk)
    period_selected = get_object_or_404(PeriodSelected, pk=period_selected_pk)
    data = dict()
    data['form_is_valid'] = False

    if request.method == 'POST':
        # form is not expected to be submitted; AJAX is used to directly call details view
        form = IncomeTaxChooseYearForm(request.POST, last_period=last_period)
        if form.is_valid():
            period = form.cleaned_data['Choose_Year']
            if len(period) == 9:  # basic validation
                return redirect(reverse('income_tax_compute:incometaxdetailview', kwargs={'company_pk': company.pk, 'period_selected_pk': period_selected_pk, 'period': period}))
    else:
        form = IncomeTaxChooseYearForm(last_period=last_period)

    context = {
        'form': form,
        'company': company,
        'period_selected': period_selected,
        'last_period': last_period
    }
    data['html_form'] = render_to_string(
        'income_tax_compute/choose_year.html', context, request=request)

    return JsonResponse(data)
