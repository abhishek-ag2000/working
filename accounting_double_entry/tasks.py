from __future__ import absolute_import, unicode_literals
import random
from celery.decorators import task
from django.shortcuts import get_object_or_404
from accounting_double_entry.models import group1,ledger1,journal,selectdatefield,Pl_journal
from company.models import company
from django.db.models.functions import Coalesce 
from django.db.models import Case, When, CharField, Value, Sum, F, Q, ExpressionWrapper, Subquery, OuterRef, Count
from django.db.models.fields import DecimalField



@task()
def create_ledger_openingclosing_task(company_id,ledger_id,selectdatefield_id):
	company_details = get_object_or_404(company, pk=company_id)
	ledger1_details = get_object_or_404(ledger1, pk=ledger_id)
	selectdatefield_details = get_object_or_404(selectdatefield, pk=selectdatefield_id)

	
	# opening balance
	if company_details.gst_enabled == True:
		qsob  = journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk,  Date__lt=selectdatefield_details.Start_Date).order_by('Date')
		qsob2 = journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk,  Date__lt=selectdatefield_details.Start_Date).order_by('Date')
	else:
		qsob  = journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk,  Date__lt=selectdatefield_details.Start_Date).exclude(To__group1_Name__group_Name__icontains='GST').order_by('Date')
		qsob2 = journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk,  Date__lt=selectdatefield_details.Start_Date).exclude(By__group1_Name__group_Name__icontains='GST').order_by('Date')


	total_debitob = qsob.aggregate(the_sum=Coalesce(Sum('Debit'), Value(0)))['the_sum']
	total_creditob = qsob2.aggregate(the_sum=Coalesce(Sum('Credit'), Value(0)))['the_sum']

	# if(ledger1_details.Creation_Date!=selectdatefield_details.Start_Date):
	if(ledger1_details.group1_Name.balance_nature == 'Debit'):
		opening_balance = abs(ledger1_details.Opening_Balance) + abs(total_debitob) - abs(total_creditob)
	else:
		opening_balance = abs(ledger1_details.Opening_Balance) + abs(total_creditob) - abs(total_debitob) 
	# else:
	# 	opening_balance = abs(ledger1_details.Opening_Balance)

	if company_details.gst_enabled == True:
		# closing balance
		qscb  = journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).order_by('Date')
		qscb2 = journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).order_by('Date')	

	else:
		# closing balance
		qscb  = journal.objects.filter(Company=company_details.pk, By=ledger1_details.pk, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).exclude(To__group1_Name__group_Name__icontains='GST').order_by('Date')
		qscb2 = journal.objects.filter(Company=company_details.pk, To=ledger1_details.pk, Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date).exclude(By__group1_Name__group_Name__icontains='GST').order_by('Date')	



	total_debitcb = qscb.aggregate(the_sum=Coalesce(Sum('Debit'), Value(0)))['the_sum']
	total_creditcb = qscb2.aggregate(the_sum=Coalesce(Sum('Credit'), Value(0)))['the_sum']

	if (ledger1_details.name != 'Profit & Loss A/c'):
		if(ledger1_details.group1_Name.balance_nature == 'Debit'):
			closing_balance = abs(opening_balance) + abs(total_debitcb) - abs(total_creditcb)
		else:
			closing_balance = abs(opening_balance) + abs(total_creditcb) - abs(total_debitcb)
	else:
		if(ledger1_details.group1_Name.balance_nature == 'Debit'):
			closing_balance = abs(opening_balance) + abs(total_debitcb) - abs(total_creditcb) 
		else:
			closing_balance = abs(opening_balance) + abs(total_creditcb) - abs(total_debitcb)

	ledger1.objects.filter(
		Company=company_details.pk,id=ledger1_details.id).update(Balance_opening=opening_balance,Closing_balance=closing_balance) 
