from django.contrib import admin

from app.portfolio_bookmark.models import PortfolioBookmark


@admin.register(PortfolioBookmark)
class PortfolioBookmarkAdmin(admin.ModelAdmin):
    pass
