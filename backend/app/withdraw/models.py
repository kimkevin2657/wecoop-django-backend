import random

from app.common.models import BaseModel

from django.db import models


class StatusChoices(models.TextChoices):
    WAIT = "정산 대기", "정산 대기"
    COMPLETE = "정산 완료", "정산 완료"
    CANCEL = "정산 미승인", "정산 미승인"


class Withdraw(BaseModel):
    user = models.ForeignKey("user.User", related_name="withdraw_users", verbose_name="유저", on_delete=models.CASCADE)
    status = models.CharField(verbose_name="상태", default="정산 대기", max_length=16, choices=StatusChoices.choices)
    apply_price = models.PositiveIntegerField(verbose_name="인출 신청 금액", null=True)
    payment_fee = models.PositiveIntegerField(verbose_name="결제 수수료 및 결제망 이용료", null=True)
    vat = models.PositiveIntegerField(verbose_name="부가세", null=True)
    final_price = models.PositiveIntegerField(verbose_name="인출신청 금액(수수료 제외 최종 수익금)", null=True)

    bank_name = models.CharField(verbose_name="은행명", max_length=12, null=True)
    account_number = models.CharField(verbose_name="계좌번호", max_length=24, null=True)
    withdraw_number = models.CharField(verbose_name="수익금인출 번호", max_length=12, null=True)

    class Meta:
        verbose_name = "수익금 인출"
        verbose_name_plural = verbose_name
        ordering = ["-created"]

    @classmethod
    def generate_withdraw_number(cls):
        return "".join([random.choice("123456789") for _ in range(10)])

    def __str__(self):
        return f"{self.user}"
