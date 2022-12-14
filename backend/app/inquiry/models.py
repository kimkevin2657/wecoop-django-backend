from app.common.models import BaseModel
from django.db import models


class TypeChoices(models.TextChoices):
    WAIT = "답변 대기", "답변 대기"
    COMPLETE = "답변 완료", "답변 완료"


class Inquiry(BaseModel):
    user = models.ForeignKey(
        "user.User",
        related_name="inquiry_users",
        verbose_name="문의 등록한 유저",
        on_delete=models.CASCADE,
    )
    type = models.CharField(verbose_name="유형", max_length=24)
    status = models.CharField(
        verbose_name="답변 상태",
        max_length=24,
        default="답변 대기",
        choices=TypeChoices.choices,
    )
    title = models.CharField(verbose_name="제목", max_length=64, null=True)
    content = models.TextField(verbose_name="문의내용")
    file = models.FileField(verbose_name="첨부파일", null=True, blank=True)

    class Meta:
        verbose_name = "문의"
        verbose_name_plural = verbose_name
        ordering = ["-created"]

    def __str__(self):
        return f"{self.user}{self.title}"
