from rest_framework import serializers

from app.inquiry.models import Inquiry


class InquiryListCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inquiry
        exclude = ["user"]

    def validate(self, attrs):
        return super().validate(attrs)

    def create(self, validated_data):
        return super().create(validated_data)
