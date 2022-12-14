from app.common.models import BaseModel
from django.db import models


class ServiceBookmark(BaseModel):
    user = models.ForeignKey(
        "user.User", related_name="bookmark_users", verbose_name="서비스 찜한 유저", on_delete=models.CASCADE
    )
    service = models.ForeignKey(
        "service.Service", related_name="bookmark_services", verbose_name="찜한 서비스", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "서비스 찜"
        verbose_name_plural = verbose_name
        ordering = ["-created"]

    def __str__(self):
        return f"{self.service}"
