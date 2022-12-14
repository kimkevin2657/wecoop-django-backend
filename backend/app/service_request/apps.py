from django.apps import AppConfig


class ServiceRequestConfig(AppConfig):
    name = "app.service_request"

    def ready(self):
        import app.service_request.signals
