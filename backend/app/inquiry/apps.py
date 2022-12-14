from django.apps import AppConfig


class InquiryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.inquiry"

    def ready(self):
        import app.inquiry.signals
