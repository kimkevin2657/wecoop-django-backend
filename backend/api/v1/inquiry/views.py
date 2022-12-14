from rest_framework import generics

from config.mail_send import send_mail

from api.v1.inquiry.filters import InquiryFilter
from api.v1.inquiry.permissions import InquiryPermission
from api.v1.inquiry.serializers import (
    InquiryListCreateSerializer,
)
from app.inquiry.models import Inquiry


class InquiryListCreateView(generics.ListCreateAPIView):
    queryset = Inquiry.objects.select_related("user")
    serializer_class = InquiryListCreateSerializer
    permission_classes = [InquiryPermission]
    filterset_class = InquiryFilter

    def perform_create(self, serializer):
        me = self.request.user
        inquiry = serializer.save(user=me)
        send_mail(
            "support@wecoop.link",
            "서비스 관련 문의",
            f"{me.nickname}({me.email})님이 문의를 신청하였습니다.\n\n{inquiry.title} - {inquiry.type}\n\n{inquiry.content}",
        )
