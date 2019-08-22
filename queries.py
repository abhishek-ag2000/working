from accounting_entry.models import LedgerMaster,JournalVoucher
from django.db.models import Case, When, CharField, Value, Sum, F, Q, ExpressionWrapper, Subquery, OuterRef, Count,FloatField



qs = LedgerMaster.objects.filter(Company__Name='Guwahati Tyres')

# ...
qs1 = qs.annotate(
	debit_sum = Subquery(
		JournalVoucher.objects.filter(Company__Name='Guwahati Tyres',
			By = OuterRef('pk')
			).values(
				'By'
			).annotate(
				the_sum = Sum('Debit')
			).values('the_sum'),
		output_field=FloatField()),
	Credit_sum =  Subquery(
		JournalVoucher.objects.filter(Company__Name='Guwahati Tyres',
			To = OuterRef('pk')
			).values(
				'To'
			).annotate(
				the_sum = Sum('Credit')
			).values(
				'the_sum'
			),
		output_field=FloatField()),
)

qs2 = qs1.annotate(
	    diffrence = Case(
	        When(Q(Credit_sum__gte=0), then=F('debit_sum') - F('Credit_sum')),
	        When(debit_sum__lt=0, then=F('Credit_sum')),
	        When(Credit_sum__lt=0, then=F('debit_sum')),
	        default=None,
	        output_field=FloatField()
	    ),
)

for q in qs2:
	print(q.ledger_name,q.diffrence)

print('Hello')