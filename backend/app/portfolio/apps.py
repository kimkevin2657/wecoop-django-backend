from django.apps import AppConfig


class PortfolioConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.portfolio"

    def ready(self):
        import app.portfolio.signals
