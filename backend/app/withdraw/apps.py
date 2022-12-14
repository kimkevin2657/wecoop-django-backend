from django.apps import AppConfig


class WithdrawConfig(AppConfig):
    name = "app.withdraw"

    def ready(self):
        import app.withdraw.signals
