from app.common.models import BaseModel
from django.db import models


class Alert(BaseModel):
    user = models.ForeignKey("user.User", related_name="alert_users", verbose_name="유저", on_delete=models.CASCADE)
    type = models.CharField(verbose_name="유형", max_length=24)
    content = models.TextField(verbose_name="내용")
    is_read = models.BooleanField(verbose_name="읽음", default=False)

    class Meta:
        verbose_name = "알림"
        verbose_name_plural = verbose_name
        ordering = ["-created"]

    def __str__(self):
        return f"{self.user}/{self.type}"
