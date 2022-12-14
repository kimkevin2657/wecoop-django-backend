from django_filters import rest_framework as filters, CharFilter
from app.service.models import Service
from django.db.models import Q


class ServiceFilter(filters.FilterSet):
    search = CharFilter(method="get_search")
    ordering = CharFilter(method="get_ordering")

    class Meta:
        model = Service
        fields = [
            "search",
            "category",
            "sub_category",
            "title",
        ]

    def get_search(self, queryset, name, value):
        return queryset.filter(title__icontains=value).distinct()

    def get_ordering(self, queryset, name, value):
        if value == "recommand":
            return queryset.order_by("created")
        elif value == "score":
            return queryset.order_by("-score")
        elif value == "latest":
            return queryset.order_by("-created")
        elif value == "high_price":
            return queryset.filter(infos__type="basic").order_by("-infos__price")
        elif value == "low_price":
            return queryset.filter(infos__type="basic").order_by("infos__price")
        else:
            return queryset.distinct()
