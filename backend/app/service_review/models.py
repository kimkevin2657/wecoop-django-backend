from django.db import models

from app.common.models import BaseModel


class ServiceReview(BaseModel):
    user = models.ForeignKey("user.User", related_name="users", verbose_name="서비스 이용한 의뢰인", on_delete=models.CASCADE)
    service = models.ForeignKey(
        "service.Service", related_name="reviews", verbose_name="이용한 서비스", on_delete=models.CASCADE
    )
    service_request = models.ForeignKey(
        "service_request.ServiceRequest",
        related_name="reviews",
        verbose_name="서비스 요청",
        on_delete=models.CASCADE,
        null=True,
    )
    service_info = models.ForeignKey(
        "service.ServiceInfo",
        related_name="review_service_info",
        verbose_name="이용한 서비스 정보",
        on_delete=models.CASCADE,
        null=True,
    )
    content = models.TextField(verbose_name="한줄리뷰")
    score = models.PositiveIntegerField(verbose_name="별점")
    # image = models.ImageField(verbose_name='이미지', upload_to='review_images')

    class Meta:
        verbose_name = "서비스 리뷰"
        verbose_name_plural = verbose_name
        ordering = ["-created"]

    def __str__(self):
        return f"{self.user}/{self.service}"
