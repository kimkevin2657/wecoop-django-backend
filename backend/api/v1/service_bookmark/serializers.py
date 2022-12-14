from rest_framework import serializers

from app.service_bookmark.models import ServiceBookmark


class ServiceBookmarkListCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceBookmark
        fields = ["service", "user_id"]

    def validate(self, attrs):
        return super().validate(attrs)

    def create(self, validated_data):
        return super().create(validated_data)
