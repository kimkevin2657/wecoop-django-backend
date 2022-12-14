from rest_framework import serializers

from app.service_review.models import ServiceReview
from app.service.models import ServiceInfo


class ServiceInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceInfo
        fields = "__all__"


class ServiceReviewListCreateSerializer(serializers.ModelSerializer):
    user_nickname = serializers.CharField(read_only=True, source="user.nickname")
    service_info = ServiceInfoSerializer(read_only=True)
    service_category = serializers.CharField(source="service.sub_category", read_only=True)
    service_image = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ServiceReview
        fields = [
            "id",
            "user_nickname",
            "content",
            "score",
            "service",
            "service_category",
            "service_image",
            "service_info",
            "updated",
            "created",
            "service_request",
        ]

    def get_service_image(self, obj):
        service = obj.service
        return service.thumbnail.url if service.thumbnail else None

    def validate(self, attrs):
        return super().validate(attrs)

    def create(self, validated_data):
        return super().create(validated_data)


class ServiceReviewDetailUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceReview
        exclude = ["user"]

    def validate(self, attrs):
        return super().validate(attrs)

    def create(self, validated_data):
        return super().create(validated_data)
