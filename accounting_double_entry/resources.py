from import_export import fields, resources
from .models import Pl_journal,journal,ledger1
from import_export.widgets import ForeignKeyWidget

class journalResource(resources.ModelResource):
	By = fields.Field(
			column_name='By',
			attribute='By',
			widget=ForeignKeyWidget(ledger1, 'name'))

	To = fields.Field(
			column_name='To',
			attribute='To',
			widget=ForeignKeyWidget(ledger1, 'name'))

	class Meta:
		model = journal
		fields = ('id','Company','By','To','By__group1_Name__group_Name','To__group1_Name__group_Name','Date','Debit','Credit')


class Pl_journalResource(resources.ModelResource):
	class Meta:
		model = Pl_journal
		exclude = ('Company',)