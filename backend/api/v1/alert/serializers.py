from rest_framework import serializers

from app.alert.models import Alert


class AlertListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = "__all__"

    def validate(self, attrs):
        return super().validate(attrs)

    def create(self, validated_data):
        return super().create(validated_data)
