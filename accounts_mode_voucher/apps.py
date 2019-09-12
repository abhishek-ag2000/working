from django.apps import AppConfig


class AccountsModeVoucherConfig(AppConfig):
    name = 'accounts_mode_voucher'
    verbose_name = 'Accounts Mode Voucher Module'

    def ready(self):
        import accounts_mode_voucher.models_sale_accounts_signals
        import accounts_mode_voucher.model_purchase_account_signal
        import accounts_mode_voucher.models_debit_note_signals
        import accounts_mode_voucher.model_credit_note_accounts_signals
