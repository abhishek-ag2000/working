from import_export import fields, resources
from .models import Pl_journal,journal,ledger1,group1
from company.models import company
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


class ledgerResource(resources.ModelResource):
	group1_Name = fields.Field(
			column_name='Group_Name',
			attribute='group1_Name',
			widget=ForeignKeyWidget(group1, 'group_Name'))

	name = fields.Field(
			column_name='Ledger_Name',
			attribute='group1_Name',)
	User_Name = fields.Field(column_name='Contact_Name',
							 attribute='User_Name',)
	Pin_Code = fields.Field(column_name='PIN',
							attribute='Pin_Code',)
	PanIt_No = fields.Field(column_name='PAN',
							 attribute='PanIt_No',)
	Balance_opening = fields.Field(column_name='Opening',
									attribute='Balance_opening',)

	class Meta:
		model = ledger1
		fields = ('id','name','group1_Name','Balance_opening','User_Name','Address','State','Pin_Code','PanIt_No','GST_No')

