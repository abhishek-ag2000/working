"""
Views for AJAX
"""
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from company.models import Company
from ecommerce_integration.decorators import product_1_activation
from .models import LedgerGroup, LedgerMaster, JournalVoucher, PeriodSelected, BankReconciliation
from .forms import DateRangeForm, BankJournalForm


@login_required
def period_selected_update(request, period_selected_pk):
    """
    Period selection (Update View)
    """
    data = {'is_error': False, 'error_message': ""}

    period_selected = get_object_or_404(PeriodSelected, pk=period_selected_pk)
    if request.method == 'POST':
        form = DateRangeForm(request.POST, instance=period_selected)

        if form.is_valid():
            form.save()
        else:
            data['is_error'] = True
            data['error_message'] = "Form validation failed!"
    else:
        form = DateRangeForm(instance=period_selected)

    context = {
        'form': form
    }
    data['html_form'] = render_to_string('company/selectdate_update.html', context, request=request)

    return JsonResponse(data)


@login_required
@product_1_activation
def get_group_base_name_json(request):
    """
    Returns the base group name in JSON
    """
    data = {'is_error': False, 'error_message': ""}

    group_id = request.GET.get('group_id', None)
    if not group_id:
        data['is_error'] = True
        data['error_message'] = "Group ID is not supplied"
        return JsonResponse(data)

    ledger_group = LedgerGroup.objects.filter(pk=group_id).first()
    if not ledger_group:
        data['is_error'] = True
        data['error_message'] = "No Group found with the ID supplied"
        return JsonResponse(data)

    data['group_base_name'] = ledger_group.group_base.name
    return JsonResponse(data)


@login_required
@product_1_activation
def is_ledger_group_name_taken_json(request, company_pk):
    """
    Checks if the group name is already exists
    """
    data = {'is_error': False, 'error_message': ""}

    company = Company.objects.filter(pk=company_pk).first()  # returns the object if exists else None
    if not company:
        data['is_error'] = True
        data['error_message'] = "No Company found with the ID supplied"
        return JsonResponse(data)

    group_name = request.GET.get('group_name', None)
    if group_name:
        data['is_taken'] = LedgerGroup.objects.filter(
            company=company,
            group_name__iexact=group_name).exists()
        data['error_message'] = 'This Group name is already exists!'
    else:
        data['is_taken'] = False

    return JsonResponse(data)


@login_required
@product_1_activation
def delete_ledger_group_json(request, company_pk, ledger_group_pk, period_selected_pk):
    """
    Delete Ledger Group and return JSON response
    """
    data = {'is_error': False, 'error_message': ""}

    company = Company.objects.filter(pk=company_pk).first()  # returns the object if exists else None
    if not company:
        data['is_error'] = True
        data['error_message'] = "No Company found with the ID supplied"
        return JsonResponse(data)

    ledger_group = LedgerGroup.objects.filter(pk=ledger_group_pk).first()
    if not ledger_group:
        data['is_error'] = True
        data['error_message'] = "No Group found with the ID supplied"
        return JsonResponse(data)

    # if LedgerGroup.objects.filter(company=company,counter__gte=1,counter__lte=29).first():
    #     data['is_error'] = True
    #     data['error_message'] = "This group cannot be deleted"

    period_selected = PeriodSelected.objects.filter(pk=period_selected_pk).first()
    if not period_selected:
        data['is_error'] = True
        data['error_message'] = "No Period found with the ID supplied"
        return JsonResponse(data)

    if request.method == "POST":
        try:
            ledger_group.delete()
        except IntegrityError:
            data['is_error'] = True
            data['error_message'] = "Cannot delete Group when ledger exists under the group!"
            return JsonResponse(data)

        ledger_group_list = LedgerGroup.objects.filter(
            user=request.user, company=company).order_by('group_name')
        context = {
            'ledgergroup_list': ledger_group_list,
            'company': company,
            'period_selected': period_selected,
        }
        data['group_list'] = render_to_string(
            'accounting_entry/group1_list2.html', context)
    else:
        context = {
            'ledger_group': ledger_group,
            'company': company,
            'period_selected': period_selected,
        }
        data['html_form'] = render_to_string(
            'accounting_entry/ledger_group_confirm_delete.html', context, request=request)

    return JsonResponse(data)


@login_required
@product_1_activation
def is_ledger_name_taken_json(request, company_pk):
    """
    Checks if the ledger name is already exists
    """
    data = {'is_error': False, 'error_message': ""}

    company = Company.objects.filter(pk=company_pk).first()  # returns the object if exists else None
    if not company:
        data['is_error'] = True
        data['error_message'] = "No Company found with the ID supplied"
        return JsonResponse(data)

    ledger_name = request.GET.get('ledger_name', None)
    if ledger_name:
        data['is_taken'] = LedgerMaster.objects.filter(
            company=company,
            ledger_name__iexact=ledger_name).exists()
        data['error_message'] = 'This Ledger name is already exists!'
    else:
        data['is_taken'] = False

    return JsonResponse(data)


@login_required
@product_1_activation
def delete_ledger_master_json(request, company_pk, ledger_master_pk, period_selected_pk):
    """
    Delete Ledger and return JSON response
    """
    data = {'is_error': False, 'error_message': ""}

    company = Company.objects.filter(pk=company_pk).first()  # returns the object if exists else None
    if not company:
        data['is_error'] = True
        data['error_message'] = "No Company found with the ID supplied"
        return JsonResponse(data)

    ledger_master = LedgerMaster.objects.filter(pk=ledger_master_pk).first()
    if not ledger_master:
        data['is_error'] = True
        data['error_message'] = "No Ledger found with the ID supplied"
        return JsonResponse(data)

    period_selected = PeriodSelected.objects.filter(pk=period_selected_pk).first()
    if not period_selected:
        data['is_error'] = True
        data['error_message'] = "No Period found with the ID supplied"
        return JsonResponse(data)

    if request.method == "POST":
        if ledger_master.ledger_group.group_base.name == 'Primary':
            data['is_error'] = True
            data['error_message'] = "Ledger under group Primary cannot be deleted"
            return JsonResponse(data)

        try:
            ledger_master.delete()
        except IntegrityError:
            data['is_error'] = True
            data['error_message'] = "Cannot delete Ledger when it is in use!"
            return JsonResponse(data)

        ledger_master_list = LedgerMaster.objects.filter(
            user=request.user, company=company.pk).order_by('ledger_name')

        context = {
            'ledgermaster_list': ledger_master_list,
            'company': company,
            'period_selected': period_selected,
        }
        data['ledger_list'] = render_to_string(
            'accounting_entry/ledger_list_2.html', context)
    else:
        context = {
            'ledger_master': ledger_master,
            'company': company,
            'period_selected': period_selected,
        }
        data['html_form'] = render_to_string(
            'accounting_entry/ledger_master_confirm_delete.html', context, request=request)

    return JsonResponse(data)


@login_required
@product_1_activation
def delete_journal_voucher_json(request, company_pk, journal_voucher_pk, period_selected_pk):
    """
    Delete Journal Voucher and return JSON response
    """
    data = {'is_error': False, 'error_message': ""}

    company = Company.objects.filter(pk=company_pk).first()  # returns the object if exists else None
    if not company:
        data['is_error'] = True
        data['error_message'] = "No Company found with the ID supplied"
        return JsonResponse(data)

    journal_voucher = JournalVoucher.objects.filter(pk=journal_voucher_pk).first()
    if not journal_voucher:
        data['is_error'] = True
        data['error_message'] = "No Journal Voucher found with the ID supplied"
        return JsonResponse(data)

    period_selected = PeriodSelected.objects.filter(pk=period_selected_pk).first()
    if not period_selected:
        data['is_error'] = True
        data['error_message'] = "No Period found with the ID supplied"
        return JsonResponse(data)

    if request.method == "POST":
        try:
            journal_voucher.delete()
        except IntegrityError:
            data['is_error'] = True
            data['error_message'] = "Cannot delete Journal when it is in use!"
            return JsonResponse(data)

        journal_voucher_list = JournalVoucher.objects.filter(
            user=request.user,
            company=company,
            voucher_date__gte=period_selected.start_date,
            voucher_date__lte=period_selected.end_date).order_by('-id')
        context = {
            'journalvoucher_list': journal_voucher_list,
            'company': company,
            'period_selected': period_selected,
        }
        data['journalvoucher_list'] = render_to_string(
            'accounting_entry/journal_list_2.html', context)
    else:
        context = {
            'journal_voucher': journal_voucher,
            'company': company,
            'period_selected': period_selected,
        }
        data['html_form'] = render_to_string(
            'accounting_entry/journal_confirm_delete.html', context, request=request)

    return JsonResponse(data)


@login_required
@product_1_activation
def update_bank_journal_json(request, bank_reconciliation_pk):
    """
    Update Bank Journal and return JSON response
    """
    data = {'is_error': False, 'error_message': ""}

    bank_reconciliation = BankReconciliation.objects.filter(pk=bank_reconciliation_pk).first()
    if not bank_reconciliation:
        data['is_error'] = True
        data['error_message'] = "No Bank Voucher found with the ID supplied"
        return JsonResponse(data)

    if request.method == 'POST':
        form = BankJournalForm(request.POST, instance=bank_reconciliation)
        if form.is_valid():
            form.save()
            bank_journal_voucher_list = BankReconciliation.objects.all().order_by('-id')
            data['bank_journal_voucher_list'] = render_to_string(
                'Bank/bank_list_2.html', {'bank_journal_voucher_list': bank_journal_voucher_list})
        else:
            data['is_error'] = True
            data['error_message'] = "Form validation failed!"
    else:
        form = BankJournalForm(instance=bank_reconciliation)

    context = {
        'form': form,
    }
    data['html_form'] = render_to_string(
        'Bank/bank_update.html', context, request=request)

    return JsonResponse(data)


# @login_required
# @product_1_activation
# def is_asset_loan_group_json(request):
#     """
#     View to handle AJAX call to return Asset and loan groups during ledger creation
#     """
#     group_id = request.GET.get('group_id', None)

#     ledger_group = get_object_or_404(LedgerGroup, pk=group_id)

#     if ledger_group.base.name == 'Current Assets' or ledger_group.base.name == 'Unsecured Loans' or ledger_group.base.name == 'Loans (Liability)' or ledger_group.base.name == 'Secured Loans':
#         is_ast_loan = True
#     else:
#         is_ast_loan = False

#     data = {
#         'is_ast_loan_group': is_ast_loan
#     }
#     return JsonResponse(data)


# @login_required
# @product_1_activation
# def get_parties_group_value(request):
#     """
#     View to handle AJAX call to return Party groups and Asset and loan groups during ledger creation
#     """
#     group_id = request.GET.get('group_id', None)

#     ledger_group = get_object_or_404(LedgerGroup, pk=group_id)

#     if ledger_group.base.name == 'Sundry Creditors' or ledger_group.base.name == 'Sundry Debtors':
#         is_party = True
#         is_ast_loan = False
#     elif ledger_group.base.name == 'Current Assets' or ledger_group.base.name == 'Unsecured Loans' or ledger_group.base.name == 'Loans (Liability)' or ledger_group.base.name == 'Secured Loans':
#         is_ast_loan = True
#         is_party = False
#     else:
#         is_party = False
#         is_ast_loan = False

#     data = {
#         'is_party_group': is_party,
#         'is_ast_loan_group': is_ast_loan
#     }
#     return JsonResponse(data)


# @login_required
# @product_1_activation
# def get_duties_taxes_group_value(request):
#     """
#     View to handle AJAX call to return Duties & Taxes groups during ledger creation
#     """
#     group_id = request.GET.get('group_id', None)

#     ledger_group = get_object_or_404(LedgerGroup, pk=group_id)

#     if ledger_group.base.name == 'Duties & Taxes':
#         is_duty = True
#     else:
#         is_duty = False

#     data = {
#         'is_duty_group': is_duty,
#     }
#     return JsonResponse(data)


# @login_required
# @product_1_activation
# def get_purchases_group_value(request):
#     """
#     View to handle AJAX call to return Purchase and expense groups during ledger creation
#     """
#     group_id = request.GET.get('group_id', None)

#     ledger_group = get_object_or_404(LedgerGroup, pk=group_id)

#     if ledger_group.base.name == 'Direct Expenses' or ledger_group.base.name == 'Indirect Expenses' or ledger_group.base.name == 'Purchase Accounts':
#         is_pur_exp = True
#         is_sal_inc = False
#         is_fxdast = False
#     elif ledger_group.base.name == 'Sales Accounts' or ledger_group.base.name == 'Indirect Incomes' or ledger_group.base.name == 'Direct Incomes':
#         is_sal_inc = True
#         is_pur_exp = False
#         is_fxdast = False
#     elif ledger_group.base.name == 'Fixed Assets':
#         is_fxdast = True
#         is_pur_exp = False
#         is_sal_inc = False
#     else:
#         is_pur_exp = False
#         is_sal_inc = False
#         is_fxdast = False

#     data = {
#         'is_pur_exp_group': is_pur_exp,
#         'is_sal_inc_group': is_sal_inc,
#         'is_fxd_ast_group': is_fxdast,
#     }
#     return JsonResponse(data)
