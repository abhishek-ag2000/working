from django.apps import AppConfig


class AccountsModeVoucherConfig(AppConfig):
    name = 'accounts_mode_voucher'
    verbose_name = 'Accounts Mode Voucher Module'

    def ready(self):
        import accounts_mode_voucher.models_sale_accounts_signals
