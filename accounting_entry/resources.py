"""
Resources for import / export
"""
from import_export import fields, resources
from import_export.widgets import ForeignKeyWidget
from .models import JournalVoucher, LedgerMaster, LedgerGroup


class JournalResource(resources.ModelResource):
    """
    Journal Resource
    """
    dr_ledger = fields.Field(
        column_name='Dr_Ledger',
        attribute='dr_ledger',
        widget=ForeignKeyWidget(LedgerMaster, 'name'))

    cr_ledger = fields.Field(
        column_name='Dr_Ledger',
        attribute='cr_ledger',
        widget=ForeignKeyWidget(LedgerMaster, 'name'))

    class Meta:
        """
        Meta
        """
        model = JournalVoucher
        fields = ('id', 'company', 'dr_ledger', 'cr_ledger', 'dr_ledger__ledger_group__group_name',
                  'cr_ledger__ledger_group__group_name', 'date', 'amount')


class LedgerResource(resources.ModelResource):
    """
    Ledger Resource
    """
    ledger_group = fields.Field(
        column_name='Group_Name',
        attribute='ledger_group',
        widget=ForeignKeyWidget(LedgerGroup, 'group_name'))

    name = fields.Field(
        column_name='Ledger_Name',
        attribute='ledger_name',)

    party_name = fields.Field(column_name='Contact_Name', attribute='party_name',)
    pin_code = fields.Field(column_name='PIN', attribute='pin_code',)
    pan_no = fields.Field(column_name='PAN', attribute='pan_no',)
    balance_opening = fields.Field(column_name='Opening', attribute='balance_opening',)

    class Meta:
        """
        Meta
        """
        model = LedgerMaster
        fields = ('id', 'ledger_name', 'ledger_group', 'balance_opening',
                  'party_name', 'address', 'state', 'pin_code', 'pan_no', 'gst_no')
