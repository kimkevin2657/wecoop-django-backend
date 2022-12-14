from app.common.models import BaseModel
from django.db import models


class ClientRequestStatus(models.TextChoices):
    WAIT = "wait", "서비스 요청"
    WORKING = "working", "업무 진행중"
    COMPLETE = "complete", "업무완료"
    CANCEL = "cancel", "요청 취소"
    REFUND_WAIT = "refund_wait", "환불 처리중"
    REFUND = "refund", "환불"


class FreelancerRequestStatus(models.TextChoices):
    WAIT = "wait", "서비스 요청"
    WORKING = "working", "업무 진행중"  # 주문완료
    COMPLETE = "complete", "업무완료"  # 주문완료
    CANCEL = "cancel", "요청 취소"  # 주문취소
    REFUND = "refund", "환불"  # 주문취소, 프리랜서일 때 가능


class CancelUserType(models.TextChoices):
    FREELANCER = "freelancer", "프리랜서"
    CLIENT = "client", "클라이언트"


class ServiceRequest(BaseModel):
    client = models.ForeignKey(
        "user.User", verbose_name="의뢰인", related_name="request_clients", on_delete=models.CASCADE
    )
    freelancer = models.ForeignKey(
        "user.User", verbose_name="프리랜서", related_name="request_freelancers", on_delete=models.CASCADE
    )
    service = models.ForeignKey(
        "service.Service", verbose_name="서비스", related_name="request_services", on_delete=models.CASCADE
    )
    service_info = models.ForeignKey(
        "service.ServiceInfo", verbose_name="서비스 정보", related_name="request_service_info", on_delete=models.CASCADE
    )

    client_status = models.CharField(
        verbose_name="의뢰인의 요청 상태", default="wait", choices=ClientRequestStatus.choices, max_length=12
    )
    freelancer_status = models.CharField(
        verbose_name="프리랜서의 요청 상태", default="wait", choices=FreelancerRequestStatus.choices, max_length=12
    )

    has_review_write = models.BooleanField(verbose_name="리뷰 작성", default=False)

    refund_type = models.CharField(verbose_name="취소/환불 유형", max_length=24, null=True, blank=True)
    refund_content = models.TextField(verbose_name="취소/환불 사유", null=True, blank=True)
    cancel_user_type = models.CharField(
        verbose_name="취소(환불)한 유저 유형", choices=CancelUserType.choices, max_length=16, null=True, blank=True
    )

    class Meta:
        verbose_name = "서비스 요청"
        verbose_name_plural = verbose_name
        ordering = ["-created"]

    def __str__(self):
        return f"{self.client}/{self.freelancer}/{self.service}"


class ServicePlusOption(models.Model):
    service_request = models.ForeignKey(
        "service_request.ServiceRequest", verbose_name="서비스 요청", related_name="plus_options", on_delete=models.CASCADE
    )
    name = models.CharField(verbose_name="옵션명", max_length=64)
    quantity = models.PositiveIntegerField(verbose_name="수량")
    price = models.PositiveIntegerField(verbose_name="가격")

    class Meta:
        verbose_name = "서비스 추가옵션"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.name}/{self.id}"
