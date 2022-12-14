from django.apps import AppConfig


class ServiceReviewConfig(AppConfig):
    name = "app.service_review"

    def ready(self):
        import app.service_review.signals
