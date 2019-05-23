# import all models


# run for lopp accessing each model instance with id
# save the list in another list
# update with the same elements

from accounting_double_entry.models import journal,ledger1,group1

jc = journal.objects.all().count()
gc = group1.objects.all().count()
lc = ledger1.objects.all().count()

while i <= lc:
	i.save()
	