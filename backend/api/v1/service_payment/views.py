import requests

from django.conf import settings
from django.db import transaction
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.response import Response

from .filters import ServicePaymentFilter
from .permissions import ServicePaymentPermission
from .serializers import (
    ServicePaymentListCreateSerializer,
    ServicePaymentDetailUpdateSerializer,
)
from api.v1.service_request.serializers import ServicePlusOptionSerializer
from app.service_payment.models import ServicePayment
from app.service_request.models import ServiceRequest, ServicePlusOption
from app.chat.models import Chat
from app.alert.models import Alert

from config.mail_send import send_mail, send_sms


class ServicePaymentListCreateView(generics.ListAPIView):
    queryset = ServicePayment.objects.select_related("user", "service", "service_info", "service_request")
    serializer_class = ServicePaymentListCreateSerializer
    permission_classes = [ServicePaymentPermission]
    filterset_class = ServicePaymentFilter
    pagination_class = None

    def get_queryset(self):
        me = self.request.user
        queryset = super().get_queryset()
        query = self.request.query_params

        if query.get("start_date") and query.get("end_date"):
            filter_content = (
                Q(user=me) & Q(created__gte=query.get("start_date")) & Q(created__lte=query.get("end_date"))
            )
            if me.type == "freelancer":
                filter_content = (
                    Q(service__user=me)
                    & Q(created__gte=query.get("start_date"))
                    & Q(created__lte=query.get("end_date"))
                )
            if query.get("status"):
                if query.get("status") == "취소":
                    filter_content &= Q(status="환불") | Q(status="구매취소")
                else:
                    filter_content &= Q(status=query.get("status"))
            return queryset.filter(filter_content)
        else:
            return queryset.filter(user=me)


class ServicePaymentDetailUpdateView(generics.RetrieveUpdateAPIView):
    queryset = ServicePayment.objects.all()
    serializer_class = ServicePaymentDetailUpdateSerializer
    permission_classes = [ServicePaymentPermission]


class IamPortPaymentView(generics.CreateAPIView):
    @transaction.atomic()
    def post(self, request):
        data = request.data
        me = request.user
        imp_uid = data["imp_uid"]

        body = {"imp_key": settings.IAMPORT_API_KEY, "imp_secret": settings.IAMPORT_API_SECRET}
        result = requests.post("https://api.iamport.kr/users/getToken", body)
        res = result.json()
        # print(f'{res}\n\n')

        if res["code"] == 0:  # 제대로 호출되었을 때,
            access_token = res["response"]["access_token"]
            # print(access_token)
            headers = {"Authorization": access_token}
            payment_complete_result = requests.get(f"https://api.iamport.kr/payments/{imp_uid}/", headers=headers)
            payment_complete_res = payment_complete_result.json()
            # print(payment_complete_res)
            if payment_complete_res["code"] == 0:
                serializer = ServicePaymentListCreateSerializer(data=data)
                serializer.is_valid(raise_exception=True)
                service_payment = serializer.save(user=me)

                # 서비스요청 -> 재결제
                if "service_request" in data and data["service_request"] is not None:
                    service_payment.service_request_id = data["service_request"]
                    service_payment.service_info_count = 1
                    service_payment.save()

                    chat = Chat.objects.get(id=data["chat_id"])
                    chat.service_request_id = data["service_request"]
                    chat.save()
                    service_request = chat.service_request
                    service_request.service_info_id = data["service_info"]
                    service_request.freelancer_status = "working"
                    service_request.client_status = "working"
                    service_request.save()

                    alert_content = f"({chat.service.title}) 새로운 견적이 도착했어요."
                    exist_payments = ServicePayment.objects.filter(service_request_id=data["service_request"])
                    exist_payment = exist_payments.first()
                    send_mail(
                        "admin@wecoop.link",
                        "재결제 요청",
                        f"{alert_content} 의뢰인 이메일: {chat.client.email}, 결제금액: {exist_payment.price}, 결제번호: {exist_payment.payment_number}",
                    )

                    if "plus_options" in data:
                        ServicePlusOption.objects.filter(service_request_id=data["service_request"]).delete()
                        serializer = ServicePlusOptionSerializer(data=data["plus_options"], many=True)
                        serializer.is_valid(raise_exception=True)
                        serializer.save(service_request_id=data["service_request"])
                    Alert.objects.create(user=chat.freelancer, type="재결제 요청", content=alert_content)
                    if chat.freelancer.is_email_receive:
                        send_mail(chat.freelancer.email, "재결제 요청", alert_content)
                    if chat.freelancer.is_sms_receive and chat.freelancer.phone:
                        send_sms(chat.freelancer.phone, f"재결제 요청 - {alert_content}")

                else:  # 상세 -> 결제 or 서비스문의 -> 결제
                    service = service_payment.service
                    service_request = ServiceRequest.objects.create(
                        client=me,
                        freelancer=service.user,
                        service=service,
                        service_info=service_payment.service_info,
                        client_status="wait",
                        freelancer_status="wait",
                    )

                    service_payment.service_request = service_request
                    service_payment.save()
                    data["service_request"] = service_request.id

                    if "plus_options" in data:
                        ServicePlusOption.objects.filter(service_request=service_request).delete()
                        serializer = ServicePlusOptionSerializer(data=data["plus_options"], many=True)
                        serializer.is_valid(raise_exception=True)
                        serializer.save(service_request=service_request)

                    if "chat_id" in data:
                        chat = Chat.objects.get(id=data["chat_id"])
                        chat.service_request = service_request
                        chat.save()
                    else:
                        chat_room = Chat.objects.create(
                            client=me, freelancer=service.user, service=service, service_request=service_request
                        )
                        headers = {"api-key": settings.TALKPLUS_API_KEY, "app-id": settings.TALKPLUS_APP_ID}
                        body = {
                            "ownerId": str(me.id),
                            "type": "public",
                            "channelId": str(chat_room.id),
                            "members": [str(service.user.id)],
                        }
                        requests.post(
                            "https://api.talkplus.io/v1.4/api/channels/create",
                            data=body,
                            headers=headers,
                        )

                return Response(
                    {
                        "msg": "결제가 완료되었습니다.",
                        "data": {
                            "price": payment_complete_res["response"]["amount"],
                            "payment_date": service_payment.created,
                            "payment_number": service_payment.payment_number,
                            "service_request_id": data["service_request"],
                        },
                        "iamport_code": res["code"],
                        "ok": True,
                    }
                )
            else:
                return Response(
                    {"msg": payment_complete_res["message"], "iamport_code": payment_complete_res["code"], "ok": False},
                    status=status.HTTP_403_FORBIDDEN,
                )
        else:
            return Response(
                {"msg": res["message"], "iamport_code": res["code"], "ok": False}, status=status.HTTP_403_FORBIDDEN
            )
