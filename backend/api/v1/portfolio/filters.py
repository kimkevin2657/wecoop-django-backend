from django_filters import rest_framework as filters, CharFilter

from app.portfolio.models import Portfolio


class PortfolioFilter(filters.FilterSet):
    class Meta:
        model = Portfolio
        fields = [
            "category",
        ]
