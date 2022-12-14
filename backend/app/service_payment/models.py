import random

from app.common.models import BaseModel
from django.db import models


class PaymentStatus(models.TextChoices):
    PAYMENT_COMPLETE = "구매확정", "구매확정"
    PAYMENT_CANCEL = "구매취소", "구매취소"
    PAYMENT_REFUND = "환불", "환불"


class ServicePayment(BaseModel):
    user = models.ForeignKey("user.User", related_name="payment_users", verbose_name="유저", on_delete=models.CASCADE)
    service = models.ForeignKey(
        "service.Service", related_name="payment_services", verbose_name="구매한 서비스", on_delete=models.CASCADE
    )
    service_info = models.ForeignKey(
        "service.ServiceInfo", related_name="payment_service_infos", verbose_name="서비스 유형", on_delete=models.CASCADE
    )
    service_request = models.ForeignKey(
        "service_request.ServiceRequest",
        related_name="payment_service_request",
        verbose_name="서비스 요청",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    service_info_count = models.PositiveIntegerField(verbose_name="서비스유형 선택한 수량", default=1)
    payment_number = models.CharField(verbose_name="결제번호", max_length=12, null=True)
    price = models.PositiveIntegerField(verbose_name="결제금액")
    type = models.CharField(verbose_name="결제방법", max_length=16, null=True, default="토스")
    status = models.CharField(verbose_name="상태", default="구매확정", choices=PaymentStatus.choices, max_length=12)

    has_tax_bill = models.BooleanField(verbose_name="세금계산서 발행신청", null=True, default=False)
    # 세금계산서 발행신청인 경우
    ceo_number = models.CharField(verbose_name="사업자등록번호", max_length=36, null=True, blank=True)
    company_name = models.CharField(verbose_name="회사(법인)명", max_length=24, null=True, blank=True)
    ceo_name = models.CharField(verbose_name="대표자명", max_length=24, null=True, blank=True)
    manager_name = models.CharField(verbose_name="담당자명", max_length=16, null=True, blank=True)
    manager_phone = models.CharField(verbose_name="담당자 연락처", max_length=16, null=True, blank=True)
    main_category = models.CharField(verbose_name="업태", max_length=24, null=True, blank=True)
    sub_category = models.CharField(verbose_name="종목", max_length=24, null=True, blank=True)
    address = models.TextField(verbose_name="사업장 주소지", null=True, blank=True)
    tax_email = models.EmailField(verbose_name="세금계산서 이메일", null=True, blank=True)

    def __str__(self):
        return f"{self.payment_number} ({self.service})"

    class Meta:
        verbose_name = "서비스 구매(결제)"
        verbose_name_plural = verbose_name
        ordering = ["-created"]
