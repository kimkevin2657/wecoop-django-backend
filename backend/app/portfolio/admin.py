from django.contrib import admin

from .models import Portfolio, PortfolioImage


@admin.register(Portfolio)
class Portfolio(admin.ModelAdmin):
    list_display = ["user", "title", "category", "created", "id"]
    search_fields = ["user__nickname", "title", "category"]
