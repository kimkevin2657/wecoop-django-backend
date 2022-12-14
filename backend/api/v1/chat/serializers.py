from django.db.models import Q, Sum
from rest_framework import serializers

from app.service.models import ServiceInfo, Service
from app.service_review.models import ServiceReview
from app.service_payment.models import ServicePayment
from app.chat.models import Chat, Message
from api.v1.service.serializers import ServiceInfoListSerializer
from api.v1.service_request.serializers import ServiceRequestListCreateSerializer


class ChatListCreateSerializer(serializers.ModelSerializer):
    is_client = serializers.SerializerMethodField(read_only=True)
    client = serializers.SerializerMethodField(read_only=True)
    freelancer = serializers.SerializerMethodField(read_only=True)
    service_name = serializers.CharField(source="service.title", read_only=True)
    service_code = serializers.CharField(source="service.code", read_only=True)
    service_root_category = serializers.CharField(source="service.menu", read_only=True)
    service_category = serializers.CharField(source="service.sub_category", read_only=True)
    payment = serializers.SerializerMethodField(read_only=True)
    service_price = serializers.SerializerMethodField(read_only=True)
    service_image = serializers.SerializerMethodField(read_only=True)
    service_infos = serializers.SerializerMethodField(read_only=True)
    service_request = ServiceRequestListCreateSerializer(read_only=True)
    client_status = serializers.CharField(source="service_request.client_status", read_only=True, allow_null=True)
    freelancer_status = serializers.CharField(
        source="service_request.freelancer_status", read_only=True, allow_null=True
    )

    class Meta:
        model = Chat
        fields = [
            "id",
            "is_client",
            "client_status",
            "freelancer_status",
            "client",
            "freelancer",
            "service",
            "payment",
            "service_name",
            "service_image",
            "service_code",
            "service_root_category",
            "service_category",
            "service_price",
            "service_infos",
            "service_request",
            "last_message",
            "updated",
            "created",
            "service_option_id",
        ]

    def get_service_image(self, obj):
        if not hasattr(obj, "service"):
            return None
        service = obj.service
        return service.thumbnail.url if service.thumbnail else None

    def get_payment(self, obj):
        if not hasattr(obj, "service_request"):
            return None
        payment = ServicePayment.objects.select_related("user", "service", "service_info", "service_request").filter(
            service_request=obj.service_request
        )
        if not payment:
            return None
        last_payment = payment.first()
        payment = payment.last()
        return {
            "payment_number": last_payment.payment_number,
            "ceo_number": payment.ceo_number,
            "payment_status": last_payment.status,
            "has_tax_bill": payment.has_tax_bill,
            "payment_date": last_payment.created,
            "service_info_count": last_payment.service_info_count,
            "company_name": payment.company_name,
            "ceo_name": payment.ceo_name,
            "manager_name": payment.manager_name,
            "manager_phone": payment.manager_phone,
            "main_category": payment.main_category,
            "sub_category": payment.sub_category,
            "address": payment.address,
            "tax_email": payment.tax_email,
        }

    def get_service_infos(self, obj):
        if not hasattr(obj, "service"):
            return []
        infos = ServiceInfo.objects.select_related("service").filter(service=obj.service)
        return ServiceInfoListSerializer(infos, many=True).data

    def get_service_price(self, obj):
        if not hasattr(obj, "service"):
            return 0
        infos = ServiceInfo.objects.select_related("service").filter(Q(service=obj.service) & Q(type="basic"))
        if not infos:
            return 0
        info = infos.first()
        return info.price

    def get_client(self, obj):
        if not hasattr(obj, "client"):
            return None
        client = obj.client
        if client is None:
            return None

        return {
            "id": client.id,
            "nickname": client.nickname,
            "profile_image": client.profile_image,
            "is_safe_phone_open": client.is_safe_phone_open,
            "safe_phone": client.safe_phone,
            "is_email_receive": client.is_email_receive,
        }

    def get_freelancer(self, obj):
        if not hasattr(obj, "freelancer"):
            return None
        freelancer = obj.freelancer
        if freelancer is None:
            return None

        user_services = Service.objects.select_related("user").exclude(is_deleted=True).filter(user=freelancer)
        avg_score = 0
        if user_services:
            avg_score = user_services.aggregate(Sum("score"))["score__sum"] / user_services.count()
        score_count = (
            ServiceReview.objects.select_related("user", "service", "service_request")
            .filter(service__user=freelancer)
            .count()
        )

        return {
            "id": freelancer.id,
            "nickname": freelancer.nickname,
            "profile_image": freelancer.profile_image,
            "safe_phone": freelancer.safe_phone,
            "has_career_mark": freelancer.has_career_mark,
            "score": avg_score,
            "score_count": score_count,
            "is_email_receive": freelancer.is_email_receive,
        }

    def get_is_client(self, obj):
        if not hasattr(obj, "client"):
            return False
        return self.context["request"].user == obj.client


class ChatUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        exclude = ["client"]
