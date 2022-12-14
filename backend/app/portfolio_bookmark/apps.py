from django.apps import AppConfig


class PortfolioBookmarkConfig(AppConfig):
    name = "app.portfolio_bookmark"

    def ready(self):
        import app.portfolio_bookmark.signals
