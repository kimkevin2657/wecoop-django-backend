from rest_framework import serializers

from app.portfolio.models import Portfolio
from app.portfolio_bookmark.models import PortfolioBookmark


class BookmarkedPortfolioSerializer(serializers.ModelSerializer):
    has_bookmark = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Portfolio
        fields = [
            "id",
            "title",
            "category",
            "main_image",
            "has_bookmark",
            "video_url",
            "price",
        ]

    def get_has_bookmark(self, obj):
        me = self.context["request"].user
        if not me.is_authenticated:
            return False
        return PortfolioBookmark.objects.select_related("user", "portfolio").filter(user=me, portfolio=obj).exists()


class PortfolioBookmarkListCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioBookmark
        exclude = ["user"]

    def validate(self, attrs):
        return super().validate(attrs)

    def create(self, validated_data):
        return super().create(validated_data)
