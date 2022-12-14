from django.db import models
from django.contrib.postgres.fields import ArrayField

from app.common.models import BaseModel


class Portfolio(BaseModel):
    user = models.ForeignKey(
        "user.User", related_name="portfolio_users", verbose_name="포트폴리오 등록한 프리랜서", on_delete=models.CASCADE
    )
    title = models.CharField(verbose_name="제목", max_length=64)
    price = models.PositiveIntegerField(verbose_name="금액", null=True, blank=True)
    category = models.CharField(verbose_name="카테고리", max_length=24, help_text="ex) 디자인 & 그래픽")
    video_url = models.TextField(verbose_name="영상 포트폴리오 URL", null=True, blank=True)
    work_start_year = models.IntegerField(verbose_name="작업 시작 년도", null=True)
    work_start_month = models.IntegerField(verbose_name="작업 시작 월", null=True)
    work_end_year = models.IntegerField(verbose_name="작업 종료 년도", null=True)
    work_end_month = models.IntegerField(verbose_name="작업 종료 월", null=True)
    main_image = models.TextField(verbose_name="메인 이미지", null=True)
    is_visible = models.BooleanField(verbose_name="활성화 유무", default=True)
    images = ArrayField(
        models.TextField(),
        verbose_name="이미지 목록",
        help_text="https://www.naver.com,https://www.kakaocorp.com",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "포트폴리오"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class PortfolioImage(BaseModel):
    portfolio = models.ForeignKey(
        "portfolio.Portfolio",
        related_name="portfolio_images",
        verbose_name="포트폴리오",
        on_delete=models.CASCADE,
        null=True,
    )
    image = models.ImageField(verbose_name="포트폴리오 이미지", upload_to="portfolio_images")

    class Meta:
        verbose_name = "포트폴리오 이미지"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.portfolio}(id: {self.id})"
