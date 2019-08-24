"""
Apps
"""
from django.apps import AppConfig


class StockkeepingConfig(AppConfig):
    """
    App Config
    """
    name = 'stock_keeping'
    verbose_name = 'Stock Keeping Module'

    def ready(self):
        import stock_keeping.models_sale_signals
        import stock_keeping.models_purchase_signals
        import stock_keeping.models_debit_note_signals
        import stock_keeping.models_credit_note_signals
