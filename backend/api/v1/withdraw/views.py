from app.withdraw.models import Withdraw
from config.mail_send import send_mail

from django.db import transaction
from django.db.models import Q
from rest_framework import generics

from .filters import WithdrawFilter
from .permissions import WithdrawPermission
from .serializers import WithdrawListCreateSerializer


class WithdrawListCreateView(generics.ListCreateAPIView):
    queryset = Withdraw.objects.select_related("user")
    serializer_class = WithdrawListCreateSerializer
    permission_classes = [WithdrawPermission]
    filterset_class = WithdrawFilter
    pagination_class = None

    @transaction.atomic()
    def perform_create(self, serializer):
        user = self.request.user
        withdraw = serializer.save(user=self.request.user, withdraw_number=Withdraw.generate_withdraw_number())
        alert_content = f"{user.nickname}님이 {withdraw.final_price}원 수익금 인출을 요청하였습니다. 인출번호: {withdraw.withdraw_number}"
        send_mail("admin@wecoop.link", "수익금 인출 요청", alert_content)
        user.possible_withdraw_price -= withdraw.apply_price
        user.save()

    def get_queryset(self):
        query = self.request.query_params
        filter_content = (
            Q(user=self.request.user)
            & Q(created__gte=query.get("start_date"))
            & Q(created__lte=query.get("end_date"))
            & Q(status="정산 완료")
        )

        return super().get_queryset().filter(filter_content)
