from rest_framework import serializers

from django.db.models import Sum

from app.service_payment.models import ServicePayment
from app.service_request.models import ServicePlusOption
from app.service.models import Service
from app.service_review.models import ServiceReview


class ServicePaymentListCreateSerializer(serializers.ModelSerializer):
    service_title = serializers.CharField(source="service.title", read_only=True)
    service_category = serializers.CharField(source="service.sub_category", read_only=True)
    service_price = serializers.IntegerField(source="service_info.price", read_only=True)
    total_option_price = serializers.SerializerMethodField(read_only=True)

    freelancer_has_career_mark = serializers.BooleanField(source="service.user.has_career_mark", read_only=True)
    user_nickname = serializers.CharField(source="user.nickname", read_only=True)
    freelancer_nickname = serializers.CharField(source="service.user.nickname", read_only=True)
    freelancer_score_info = serializers.SerializerMethodField(read_only=True)
    service_thumbnail = serializers.CharField(source="service.thumbnail.url", read_only=True)
    is_client = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ServicePayment
        fields = [
            "id",
            "user_nickname",
            "is_client",
            "freelancer_has_career_mark",
            "freelancer_nickname",
            "freelancer_score_info",
            "service_thumbnail",
            "payment_number",
            "service",
            "service_info",
            "service_price",
            "total_option_price",
            "service_info_count",
            "price",
            "type",
            "status",
            "has_tax_bill",
            "ceo_number",
            "company_name",
            "ceo_name",
            "manager_name",
            "manager_phone",
            "main_category",
            "sub_category",
            "address",
            "tax_email",
            "created",
            "updated",
            "service_title",
            "service_category",
        ]

    def get_total_option_price(self, obj):
        service_request = obj.service_request
        total_options = ServicePlusOption.objects.filter(service_request=service_request)
        total_price = 0
        if total_options:
            for option in total_options:
                total_price += option.quantity * option.price
        return total_price

    def get_is_client(self, obj):
        me = self.context["request"].user
        if not me.is_authenticated:
            return False
        return me == obj.service_request.client

    def get_freelancer_score_info(self, obj):
        user_services = Service.objects.select_related("user").exclude(is_deleted=True).filter(user=obj.service.user)
        avg_score = 0
        if user_services:
            avg_score = user_services.aggregate(Sum("score"))["score__sum"] / user_services.count()
        score_count = ServiceReview.objects.select_related("user").filter(service__user=obj.service.user).count()

        return {
            "score": avg_score,
            "score_count": score_count,
        }

    def validate(self, attrs):
        return super().validate(attrs)

    def create(self, validated_data):
        return super().create(validated_data)


class ServicePaymentDetailUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicePayment
        exclude = ["user"]

    def validate(self, attrs):
        return super().validate(attrs)

    def create(self, validated_data):
        return super().create(validated_data)
