from rest_framework import serializers

from app.portfolio.models import Portfolio, PortfolioImage

from drf_spectacular.utils import extend_schema_serializer
from .examples import portfolio_create_examples


class PortfolioImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioImage
        fields = (
            "id",
            "image",
            "portfolio",
        )


@extend_schema_serializer(examples=portfolio_create_examples)
class PortfolioListCreateSerializer(serializers.ModelSerializer):
    # images = PortfolioImageSerializer(read_only=True, many=True)

    class Meta:
        model = Portfolio
        fields = (
            "id",
            "title",
            "category",
            "video_url",
            "work_start_year",
            "work_start_month",
            "work_end_year",
            "work_end_month",
            "main_image",
            "images",
            "is_visible",
            "price",
        )

    def validate(self, attrs):
        return super().validate(attrs)

    def create(self, validated_data):
        return super().create(validated_data)


class PortfolioDetailSerializer(serializers.ModelSerializer):
    # images = PortfolioImageSerializer(read_only=True, many=True)

    class Meta:
        model = Portfolio
        fields = (
            "id",
            "title",
            "category",
            "video_url",
            "work_start_year",
            "work_start_month",
            "work_end_year",
            "work_end_month",
            "main_image",
            "images",
            "is_visible",
            "price",
        )

    def validate(self, attrs):
        return super().validate(attrs)

    def create(self, validated_data):
        return super().create(validated_data)
