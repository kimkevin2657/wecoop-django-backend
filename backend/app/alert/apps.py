from django.apps import AppConfig


class AlertConfig(AppConfig):
    name = "app.alert"

    def ready(self):
        import app.alert.signals
