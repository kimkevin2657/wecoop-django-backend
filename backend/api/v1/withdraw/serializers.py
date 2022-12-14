from rest_framework import serializers

from app.withdraw.models import Withdraw


class WithdrawListCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdraw
        exclude = ["user"]

    def validate(self, attrs):
        return super().validate(attrs)

    def create(self, validated_data):
        return super().create(validated_data)
