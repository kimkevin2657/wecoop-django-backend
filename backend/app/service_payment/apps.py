from django.apps import AppConfig


class ServicePaymentConfig(AppConfig):
    name = "app.service_payment"

    def ready(self):
        import app.service_payment.signals
