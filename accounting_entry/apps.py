"""
Config
"""
from django.apps import AppConfig


class AccountingEntryConfig(AppConfig):
    """
    Configuration for the app; (this settng may not be applied without further congiration in __init__.py)
    """
    name = 'accounting_entry'
    verbose_name = "Accounting Entry Module"

    def ready(self):
        import accounting_entry.signals
