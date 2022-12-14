from app.alert.models import Alert
from app.chat.models import Chat
from app.user.models import User

from django.db.models import Q
from django.db import transaction
from rest_framework import status, response
from rest_framework.generics import ListCreateAPIView, UpdateAPIView, DestroyAPIView

from .permissions import ChatPermission
from .serializers import ChatListCreateSerializer, ChatUpdateSerializer

from config.mail_send import send_mail, send_sms


class ChatListCreateView(ListCreateAPIView):
    queryset = Chat.objects.select_related("client", "freelancer", "service")
    serializer_class = ChatListCreateSerializer
    permission_classes = [ChatPermission]
    pagination_class = None
    return_status = status.HTTP_201_CREATED
    response_data = {}

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        if self.return_status == status.HTTP_201_CREATED:
            self.response_data = serializer.data
        return response.Response(self.response_data, status=self.return_status, headers=headers)

    def get_queryset(self):
        me = self.request.user
        # return super().get_queryset().filter(Q(client=me) | Q(freelancer=me))
        # if me.type == "client":
        return (
            super()
            .get_queryset()
            .filter(Q(client=me, client_is_visible=True) | Q(freelancer=me, freelancer_is_visible=True))
        )
        # elif me.type == "freelancer":
        #     return super().get_queryset().filter(Q(freelancer=me) & Q(freelancer_is_visible=True))
        # else:
        #     return super().get_queryset()

    @transaction.atomic()
    def perform_create(self, serializer):
        me = self.request.user
        data = self.request.data
        freelancer_id = data["freelancer"]

        try:
            chat_room = Chat.objects.get(
                Q(client=me)
                & Q(freelancer_id=freelancer_id)
                & Q(service_id=data["service"])
                & Q(service_request__isnull=True)
                & Q(client_is_visible=True)
            )
            serializer = ChatListCreateSerializer(instance=chat_room, context={"request": self.request})
            self.response_data = serializer.data
            self.return_status = status.HTTP_409_CONFLICT
        except Chat.DoesNotExist:
            chat_room = serializer.save(
                client=me,
                freelancer_id=freelancer_id,
                service_id=data["service"],
            )

            alert_content = f"({chat_room.service.title}) 새로운 서비스 문의가 있어요."
            freelancer = User.objects.get(id=freelancer_id)
            Alert.objects.create(user_id=freelancer_id, type="서비스 문의", content=alert_content)
            if freelancer.is_sms_receive and freelancer.phone:
                send_sms(freelancer.phone, f"서비스 문의 - {alert_content}")


class ChatUpdateView(UpdateAPIView, DestroyAPIView):
    queryset = Chat.objects.select_related("client", "freelancer", "service")
    serializer_class = ChatUpdateSerializer
    permission_classes = [ChatPermission]

    @transaction.atomic()
    def perform_destroy(self, instance):
        me = self.request.user

        # if not instance.service_request:
        #     instance.delete()
        # else:
        is_client = me == instance.client
        if is_client:
            instance.client_is_visible = False
        else:
            instance.freelancer_is_visible = False
        instance.save()
