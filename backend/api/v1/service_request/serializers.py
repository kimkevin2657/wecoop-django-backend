from rest_framework import serializers

from app.service_request.models import ServiceRequest, ServicePlusOption


class ServicePlusOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicePlusOption
        exclude = ["service_request"]

    def validate(self, attrs):
        return super().validate(attrs)

    def create(self, validated_data):
        return super().create(validated_data)


class ServiceRequestListCreateSerializer(serializers.ModelSerializer):
    plus_options = ServicePlusOptionSerializer(read_only=True, many=True)

    class Meta:
        model = ServiceRequest
        fields = [
            "id",
            "created",
            "updated",
            "client_status",
            "freelancer_status",
            "has_review_write",
            "refund_type",
            "refund_content",
            "freelancer",
            "service",
            "service_info",
            "plus_options",
            "cancel_user_type",
        ]

    def validate(self, attrs):
        return super().validate(attrs)

    def create(self, validated_data):
        return super().create(validated_data)


class ServiceRequestDetailUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRequest
        exclude = ["client"]

    def validate(self, attrs):
        return super().validate(attrs)

    def create(self, validated_data):
        return super().create(validated_data)
