from datetime import datetime
import arrow
import collections
from company.models import company
from django.db.models import Case, When, CharField, Value, Sum, Count, F,Q, ExpressionWrapper, Subquery, OuterRef, FloatField
from django.db.models.fields import DecimalField
from django.db.models.functions import Coalesce


# results = collections.OrderedDict()
# start = datetime(2019, 1, 1)
# end = datetime(2020, 6, 20)

# result = Purchase.objects.filter(date__gte=start, date__lt=end).annotate(real_total = Case(When(sub_total__isnull=True, then=0),default=F('sub_total')))
# z = 0

# for d in arrow.Arrow.range('month', start, end):
# 	month_partial_total = result.filter(date__month=d.month).aggregate(partial_total=Sum('real_total'))['partial_total']

# 	if month_partial_total == None:
# 		month_partial_total = int(0)
# 		e = month_partial_total
# 	else:
# 		e = month_partial_total

# 	z = z + e

# 	results[d.format('MMMM')] =  [e,z]	

# 	for key, value in results.items():
# 		print (key, + '-' +  value.1, + '-' + value.2)


# from datetime import datetime,timedelta

# def months_between(start,end):
# 	months = []
# 	cursor = start
# 	while cursor <= end:
# 		if cursor.month not in months:
# 			months.append(cursor.month)
# 		cursor += timedelta(weeks=1)
# 	return months

# start = datetime.now() - timedelta(days=685)
# end = datetime.now()
# print(months_between(start,end))


# import datetime
# from dateutil.rrule import rrule, MONTHLY

# strt_dt = datetime.date(2001,1,1)
# end_dt = datetime.date(2002,6,1)

# dates = [dt.month for dt in rrule(MONTHLY, dtstart=strt_dt, until=end_dt)]
# print (dates)


company_details = company.objects.get(Name='Mira Tyres')

ls = company_details.Companys.filter(group1_Name__group_Name__icontains='Sundry Debtors')
ls_tot = ls.annotate(total = Coalesce(Sum('partyledgersales__sub_total'), 0)).order_by('-total') ## all ledger sales total

# TOTAL OF ALL SUNDRY DEBTOR
total_sundry = ls_tot.aggregate(partial_total=Sum('total'))['partial_total']


# FOR TEMPLATE
for ln in ls_tot:
	# party name
	ls_name = ln.partyledgersales.all()
	ls_name.first().billname
	# save total also
	x = ls_name.aggregate(partial_total=Sum('sub_total'))['partial_total']
	# adress
	ls_name.first().Address
	# TOTAL
	total_sundry
	# CALCULATE THIS LEDGER TOTAL /TOTAL
	x / total_sundry * 100









#____________________________________________________________________________________
#sales_led = company_details.companysales.filter(Party_ac__group1_Name__group_Name__icontains='Sundry Debtors')

#ls_tot_sales = sales_led.annotate(total = Coalesce(Sum('sub_total'), 0))


for l in ls_tot_sales:
	print('From sales  -',l.Party_ac)