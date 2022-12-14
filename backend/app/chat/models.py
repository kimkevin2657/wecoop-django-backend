from django.db import models

from app.common.models import BaseModel


class Chat(BaseModel):
    client = models.ForeignKey(
        "user.User",
        verbose_name="의뢰인(채팅방 생성하는 유저)",
        related_name="chat_clients",
        null=True,
        on_delete=models.SET_NULL,
        blank=True,
    )
    freelancer = models.ForeignKey(
        "user.User",
        verbose_name="프리랜서",
        related_name="chat_freelancers",
        null=True,
        on_delete=models.SET_NULL,
        blank=True,
    )
    service = models.ForeignKey(
        "service.Service", verbose_name="서비스", related_name="chat_services", null=True, on_delete=models.CASCADE
    )
    service_request = models.OneToOneField(
        "service_request.ServiceRequest",
        verbose_name="서비스요청",
        related_name="requests",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    last_message = models.TextField(verbose_name="최근(마지막) 메세지", null=True, blank=True)
    service_option_id = models.PositiveIntegerField(verbose_name="문의 시에 선택한 옵션 id", null=True, blank=True)
    client_is_visible = models.BooleanField(verbose_name="클라이언트 활성화 유무", default=True)
    freelancer_is_visible = models.BooleanField(verbose_name="프리랜서 활성화 유무", default=True)

    class Meta:
        verbose_name = "채팅방(서비스 문의)"
        verbose_name_plural = verbose_name
        ordering = ["-updated", "-created"]

    def __str__(self):
        return f"{self.client}/{self.freelancer}/{self.service} / {self.id}"


class Message(BaseModel):
    chat = models.ForeignKey("chat.Chat", verbose_name="채팅방", on_delete=models.CASCADE)
    user = models.ForeignKey("user.User", verbose_name="메세지 작성자", on_delete=models.CASCADE)
    text = models.TextField(verbose_name="메세지 내용", null=True, blank=True)
    file = models.URLField(verbose_name="파일", null=True, blank=True)

    class Meta:
        verbose_name = "메세지"
        verbose_name_plural = verbose_name
        ordering = ["-created"]

    def __str__(self):
        return f"{self.text}/{self.chat}"
