import requests

from config.mail_send import send_mail, send_sms

from app.chat.models import Chat
from app.service_payment.models import ServicePayment
from app.service_request.models import ServiceRequest
from app.alert.models import Alert
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from rest_framework import generics

from .filters import ServiceRequestFilter
from .permissions import ServiceRequestPermission
from .serializers import (
    ServiceRequestDetailUpdateSerializer,
    ServiceRequestListCreateSerializer,
)


class ServiceRequestListCreateView(generics.ListCreateAPIView):
    queryset = ServiceRequest.objects.select_related("client", "freelancer", "service", "service_info")
    serializer_class = ServiceRequestListCreateSerializer
    permission_classes = [ServiceRequestPermission]
    filterset_class = ServiceRequestFilter
    pagination_class = None

    def get_queryset(self):
        query = self.request.query_params
        if query.get("isMine"):
            filter_query = Q(freelancer=self.request.user)
            if query.get("start_date") and query.get("end_date"):
                filter_query &= Q(updated__gte=query.get("start_date")) & Q(updated__lte=query.get("end_date"))
            return super().get_queryset().exclude(freelancer_status="wait").filter(filter_query)
        return super().get_queryset()

    @transaction.atomic()
    def perform_create(self, serializer):
        data = self.request.data
        me = self.request.user

        service_request = serializer.save(client=me)

        if "chat_id" in data:
            chat = Chat.objects.get(id=data["chat_id"])
            chat.service_request = service_request
            chat.save()
        else:
            chat_room = Chat.objects.create(
                client=me,
                freelancer_id=data["freelancer"],
                service_id=data["service"],
                service_request=service_request,
            )

            headers = {
                "api-key": settings.TALKPLUS_API_KEY,
                "app-id": settings.TALKPLUS_APP_ID,
            }
            body = {
                "ownerId": str(me.id),
                "type": "public",
                "channelId": str(chat_room.id),
                "members": [str(data["freelancer"])],
            }
            requests.post(
                "https://api.talkplus.io/v1.4/api/channels/create",
                data=body,
                headers=headers,
            )


class ServiceRequestDetailUpdateView(generics.RetrieveUpdateAPIView):
    queryset = ServiceRequest.objects.select_related("client", "freelancer", "service", "service_info")
    serializer_class = ServiceRequestDetailUpdateSerializer
    permission_classes = [ServiceRequestPermission]

    @transaction.atomic()
    def perform_update(self, serializer):
        data = self.request.data

        service_request = serializer.save()
        client = service_request.client
        freelancer = service_request.freelancer

        service = service_request.service

        if "client_status" in data:
            client_status = data["client_status"]

            if client_status == "complete" and not service_request.has_review_write:
                service_payments = ServicePayment.objects.filter(Q(service_request=service_request) & Q(status="구매확정"))
                if service_payments.exists():
                    total_price = service_payments.last().price

                    freelancer.possible_withdraw_price += total_price
                    freelancer.save()
                alert_content = f"({service.title}) 의뢰인으로부터 서비스 최종 확인이 완료되었어요. 완료된 서비스는 업무관리-업무완료에서 확인하실 수 있어요."
                Alert.objects.create(user=freelancer, type="서비스 최종 확인", content=alert_content)
                if freelancer.is_email_receive:
                    send_mail(freelancer.email, "서비스 최종 확인", alert_content)
                if freelancer.is_sms_receive and freelancer.phone:
                    send_sms(freelancer.phone, f"서비스 최종 확인 - {alert_content}")

            elif (
                client_status == "refund_wait"
                and data["freelancer_status"] != "refund"
                and data.get("cancel_user_type") == "client"
            ):
                alert_content = f"({service.title}) 의뢰인이 구매를 취소했어요. 취소된 서비스는 업무관리-취소/환불에서 확인하실 수 있어요."
                Alert.objects.create(user=freelancer, type="서비스 취소", content=alert_content)
                if freelancer.is_email_receive:
                    send_mail(freelancer.email, "서비스 취소", alert_content)
                if freelancer.is_sms_receive and freelancer.phone:
                    send_sms(freelancer.phone, f"서비스 취소 - {alert_content}")
                payment = ServicePayment.objects.filter(service_request=service_request).last()
                send_mail(
                    "admin@wecoop.link",
                    "서비스 취소",
                    alert_content + f" 의뢰인 이메일: {client.email}, 결제금액: {payment.price}, 결제번호: {payment.payment_number}",
                )
        if "freelancer_status" in data:
            freelancer_status = data["freelancer_status"]

            if freelancer_status == "refund":  # 환불, 오로지 프리랜서만 환불요청 가능
                alert_content = f"({service.title}) 프리랜서로부터 서비스 환불이 완료되었어요. 결제 취소 처리 기간은 해당 카드사로 문의해 주세요."
                Alert.objects.create(user=client, type="서비스 환불", content=alert_content)
                payment = ServicePayment.objects.filter(service_request=service_request).last()
                if client.is_email_receive:
                    send_mail(client.email, "서비스 환불", alert_content)
                if client.is_sms_receive and client.phone:
                    send_sms(client.phone, f"서비스 환불 - {alert_content}")
                send_mail(
                    "admin@wecoop.link",
                    "서비스 환불",
                    alert_content + f" 의뢰인 이메일: {client.email}, 결제금액: {payment.price}, 결제번호: {payment.payment_number}",
                )
            elif freelancer_status == "complete":
                alert_content = f"({service.title}) 의뢰하신 서비스가 완료되었어요. 리뷰를 남겨주시면 프리랜서에게 큰 힘이 돼요."
                Alert.objects.create(user=client, type="서비스 완료", content=alert_content)
                if client.is_email_receive:
                    send_mail(client.email, "서비스 완료", alert_content)
                if client.is_sms_receive and client.phone:
                    send_sms(client.phone, f"서비스 완료 - {alert_content}")
            elif freelancer_status == "cancel" and data.get("cancel_user_type") == "freelancer":  # 취소, 프리랜서+의뢰인 다 가능
                alert_content = f"({service.title}) 프리랜서의 사정으로 인해 결제가 취소되었어요. 자세한 내용은 업무관리-취소/환불에서 확인해 주세요. 결제 취소 처리 기간은 해당 카드사로 문의해 주세요."
                Alert.objects.create(user=client, type="판매 취소", content=alert_content)
                if client.is_email_receive:
                    send_mail(client.email, "판매 취소", alert_content)
                if client.is_sms_receive and client.phone:
                    send_sms(client.phone, f"판매 취소 - {alert_content}")
                payment = ServicePayment.objects.filter(service_request=service_request).last()
                send_mail(
                    "admin@wecoop.link",
                    "판매 취소",
                    alert_content + f" 의뢰인 이메일: {client.email}, 결제금액: {payment.price}, 결제번호: {payment.payment_number}",
                )
            elif freelancer_status == "working":
                alert_content = f"({service_request.service.title}) 프리랜서가 요청을 수락하여 업무를 진행 중이에요."
                #     Alert.objects.create(user=client, type="서비스 요청 수락", content=alert_content)
                #     if client.is_email_receive:
                #         send_mail(client.email, "서비스 요청 수락", alert_content)
                if client.is_sms_receive and client.phone:
                    send_sms(client.phone, f"서비스 요청 수락 - {alert_content}")

        if "has_review_write" in data and data["has_review_write"]:
            alert_content = f"({service.title}) 새로운 리뷰가 등록됐어요."
            Alert.objects.create(user=freelancer, type="리뷰 작성 완료", content=alert_content)
            if freelancer.is_email_receive:
                send_mail(freelancer.email, "리뷰 작성 완료", alert_content)
            if freelancer.is_sms_receive and freelancer.phone:
                send_sms(freelancer.phone, f"리뷰 작성 완료 - {alert_content}")
