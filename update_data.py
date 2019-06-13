# import all models


# run for lopp accessing each model instance with id
# save the list in another list
# update with the same elements
from stockkeeping.models import stock_journal,Stockgroup,Simpleunits,Compoundunits,Stockdata,Purchase,Sales,Stock_Total,Stock_Total_sales
from accounting_double_entry.models import journal,ledger1,group1

jc = journal.objects.filter(Company__Name__icontains='Hindustan Co. Ltd',voucher_type__icontains='Journal')
pur = Purchase.objects.filter(Company__Name__icontains='Hindustan Co. Ltd')
sal = Sales.objects.filter(Company__Name__icontains='Hindustan Co. Ltd')


for j in jc:
	j.delete()

# for p in pur:
# 	p.save()

# for s in sal:
# 	s.save()