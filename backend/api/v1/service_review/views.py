from app.alert.models import Alert
from app.service_review.models import ServiceReview
from django.db.models import Avg
from rest_framework import generics

from config.mail_send import send_mail, send_sms

from .filters import ServiceReviewFilter
from .permissions import ServiceReviewPermission
from .serializers import (
    ServiceReviewDetailUpdateSerializer,
    ServiceReviewListCreateSerializer,
)


class ServiceReviewListCreateView(generics.ListCreateAPIView):
    queryset = ServiceReview.objects.select_related("user", "service")
    serializer_class = ServiceReviewListCreateSerializer
    permission_classes = [ServiceReviewPermission]
    filterset_class = ServiceReviewFilter

    def perform_create(self, serializer):
        service_review = serializer.save(user=self.request.user, service_info_id=self.request.data["service_info"])
        service_request = service_review.service_request
        service_request.has_review_write = True
        service_request.save()

        service = service_review.service
        service.score = service.reviews.all().aggregate(avg=Avg("score"))["avg"]
        service.save()

        service_user = service.user
        alert_content = f"({service.title}) 새로운 리뷰가 등록됐어요."
        Alert.objects.create(user=service_user, type="리뷰 작성 완료", content=alert_content)

        if service_user.is_email_receive:
            send_mail(service_user.email, "리뷰 작성 완료", alert_content)
        if service_user.is_sms_receive and service_user.phone:
            send_sms(service_user.phone, f"리뷰 작성 완료 - {alert_content}")


class ServiceReviewDetailUpdateView(generics.RetrieveUpdateAPIView):
    queryset = ServiceReview.objects.select_related("user", "service")
    serializer_class = ServiceReviewDetailUpdateSerializer
    permission_classes = [ServiceReviewPermission]
