from __future__ import absolute_import, unicode_literals
import random
from celery.decorators import task
from django.shortcuts import get_object_or_404
from stockkeeping.models import Stockgroup,Simpleunits,Compoundunits,Stockdata,Purchase,Sales,Stock_Total,Stock_Total_sales,stock_journal
from accounting_double_entry.models import selectdatefield
from company.models import company
from django.db.models.functions import Coalesce 
from django.db.models import Case, When, CharField, Value, Sum, F, Q, ExpressionWrapper, Subquery, OuterRef, Count
from django.db.models.fields import DecimalField
from decimal import Decimal,DecimalException



@task()
def user_created_stock_ledger_task(stock_id):
	stock_details = get_object_or_404(Stockdata, pk=stock_id)
	selectdatefield_details = get_object_or_404(selectdatefield,User=stock_details.User)

	total_purchase_quantity_in_range = stock_details.purchasestock.filter(purchases__date__lt=selectdatefield_details.Start_Date)
	total_sales_quantity_in_range 	 = stock_details.salestock.filter(sales__date__lt=selectdatefield_details.Start_Date)

	total_purchase_quantity_os = total_purchase_quantity_in_range.aggregate(the_sum=Coalesce(Sum('Quantity_p'), Value(0)))['the_sum']  
	#total_purchase_quantity_in_range = stock_details.purchasestock.filter(Date__gte=selectdatefield_details.Start_Date, Date__lte=selectdatefield_details.End_Date)
	total_purchase_os = total_purchase_quantity_in_range.aggregate(the_sum=Coalesce(Sum('Total_p'), Value(0)))['the_sum']
	total_sales_quantity_os = total_sales_quantity_in_range.aggregate(the_sum=Coalesce(Sum('Quantity'), Value(0)))['the_sum']
	total_sales_os = total_sales_quantity_in_range.aggregate(the_sum=Coalesce(Sum('Total'), Value(0)))['the_sum']

	if total_purchase_quantity_os == None:
		total_purchase_quantity_os = 0

	if total_sales_quantity_os == None:
		total_sales_quantity_os = 0

	if stock_details.Quantity == None:
		opening_quantity =  (total_purchase_quantity_os - total_sales_quantity_os)
	else:
		opening_quantity =  stock_details.Quantity + (total_purchase_quantity_os - total_sales_quantity_os)

	if total_purchase_quantity_os == 0:
		os = stock_details.opening 
	else:
		os = stock_details.opening + ((Decimal(total_purchase_os) / Decimal(total_purchase_quantity_os)) * opening_quantity) # for weighted average

# closing stock calculations
	total_purchase_quantity_in_range_cs = stock_details.purchasestock.filter(purchases__date__gte=selectdatefield_details.Start_Date, purchases__date__lte=selectdatefield_details.End_Date)
	total_sales_quantity_in_range_cs 	 = stock_details.salestock.filter(sales__date__gte=selectdatefield_details.Start_Date,  sales__date__lte=selectdatefield_details.End_Date)

	total_purchase_quantity = total_purchase_quantity_in_range_cs.aggregate(the_sum=Coalesce(Sum('Quantity_p'), Value(0)))['the_sum']  
	total_purchase = total_purchase_quantity_in_range_cs.aggregate(the_sum=Coalesce(Sum('Total_p'), Value(0)))['the_sum']
	total_sales_quantity = total_sales_quantity_in_range_cs.aggregate(the_sum=Coalesce(Sum('Quantity'), Value(0)))['the_sum']
	total_sales = total_sales_quantity_in_range_cs.aggregate(the_sum=Coalesce(Sum('Total'), Value(0)))['the_sum']

	if total_purchase_quantity == None:
		total_purchase_quantity = 0

	if total_sales_quantity == None:
		total_sales_quantity = 0

	closing_quantity =  total_purchase_quantity - total_sales_quantity
	
	if stock_details.Quantity == None:
		closing_quantity_real = (total_purchase_quantity - total_sales_quantity)
	else:
		closing_quantity_real = stock_details.Quantity + (total_purchase_quantity - total_sales_quantity)

# weighted average calculations
	total_purchase_quantity_in_range_wavg = stock_details.purchasestock.filter(purchases__date__lte=selectdatefield_details.End_Date)

	total_purchase_quantity_wavg = total_purchase_quantity_in_range_wavg.aggregate(the_sum=Coalesce(Sum('Quantity_p'), Value(0)))['the_sum']  
	total_purchase_wavg = total_purchase_quantity_in_range_wavg.aggregate(the_sum=Coalesce(Sum('Total_p'), Value(0)))['the_sum']


	if total_purchase_quantity_wavg == 0 and total_purchase_wavg == 0 and os == 0 and closing_quantity == 0:
		cs = 0
	elif total_purchase_quantity_wavg == None and total_purchase_wavg == None and os == None and closing_quantity == None:
		cs = 0
	else:
		if total_purchase_wavg == None:
			cs = 0 
		elif total_purchase_quantity_wavg == None:
			cs = 0
		elif closing_quantity == None:
			cs = 0
		elif os == None:
			cs = 0
		else:
			try:
				cs = ((Decimal(total_purchase_wavg + stock_details.opening) / Decimal(total_purchase_quantity_wavg + stock_details.Quantity)) * (closing_quantity + stock_details.Quantity)) # for weighted average
			except DecimalException: # handle empty transactions
				return None
		
	stock_journal.objects.filter(
		User=stock_details.User,
		Company=stock_details.Company,
		stockitem=stock_details).update(date=selectdatefield_details.Start_Date,opening_stock=os,closing_quantity=closing_quantity_real,closing_stock=cs)



