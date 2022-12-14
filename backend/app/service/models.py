import random

from app.common.models import BaseModel
from django.db import models


class ServiceMenuChoices(models.TextChoices):
    DESIGN = "design", "디자인 & 그래픽"
    VIDEO = "video", "영상 & 사진"
    SOUND = "sound", "음향"
    DOCUMENT = "document", "문서 & 글작업"
    MARKETING = "marketing", "디지털 마케팅"


class WeekendChoices(models.TextChoices):
    ALL = "작업 가능", "작업 가능"
    ONLY_CONSULTING = "상담만 가능", "상담만 가능"
    IMPOSSIBLE = "작업 불가능", "작업 불가능"


class CheckChoices(models.TextChoices):
    WAIT = "미확인", "미확인"
    APPROVE = "미승인", "미승인"
    REJECT = "승인", "승인"


class Service(BaseModel):
    code = models.CharField(verbose_name="서비스 코드", null=True, blank=True, max_length=16)
    user = models.ForeignKey(
        "user.User", related_name="service_users", verbose_name="서비스 등록한 프리랜서", on_delete=models.CASCADE, null=True
    )
    title = models.CharField(verbose_name="서비스 명", max_length=64)
    description = models.TextField(verbose_name="설명")
    menu = models.CharField(
        verbose_name="메인 카테고리",
        max_length=24,
        choices=ServiceMenuChoices.choices,
        null=True,
    )
    category = models.CharField(verbose_name="하위 카테고리", max_length=24, help_text="ex) 브랜드 아이덴티티")
    sub_category = models.CharField(verbose_name="최하위 카테고리", max_length=24, help_text="ex) 로고 디자인", null=True)
    thumbnail = models.FileField(verbose_name="썸네일", upload_to="service_thumbnails")
    score = models.FloatField(verbose_name="서비스 평점", default=0, blank=True)
    weekend_work_type = models.CharField(
        verbose_name="주말작업 상태", max_length=24, null=True, choices=WeekendChoices.choices
    )
    has_tax_bill = models.BooleanField(verbose_name="세금계산서 발행 가능", null=True, default=False)
    is_visible = models.BooleanField(verbose_name="활성화 유무", default=True)
    approve_status = models.CharField(verbose_name="승인 상태", default="승인", max_length=16, choices=CheckChoices.choices)
    approve_date = models.DateField(verbose_name="승인 날짜", null=True, blank=True)

    @classmethod
    def generate_code(cls):
        return "".join([random.choice("0123456789") for _ in range(7)])

    def __str__(self):
        return f"{self.title}"

    class Meta:
        verbose_name = "서비스"
        verbose_name_plural = verbose_name


class ServiceInfoTypeChoices(models.TextChoices):
    BASIC = "basic", "Basic"
    PREMIUM = "premium", "Premium"
    DELUXE = "deluxe", "Deluxe"


class ServiceInfo(models.Model):
    service = models.ForeignKey(
        "service.Service",
        related_name="infos",
        verbose_name="서비스",
        on_delete=models.CASCADE,
    )
    type = models.CharField(verbose_name="유형", max_length=16, choices=ServiceInfoTypeChoices.choices)
    title = models.CharField(verbose_name="패키지 제목", max_length=64)
    description = models.TextField(verbose_name="패키지 설명")
    work_date = models.CharField(verbose_name="작업일", max_length=64)
    possible_update_count = models.CharField(verbose_name="수정 횟수", max_length=64)

    # 디자인&그래픽
    design_sample_count = models.PositiveIntegerField(verbose_name="시안 개수", null=True, blank=True)

    # 디자인&그래픽 or 영상&사진
    is_provide_origin_file = models.BooleanField(verbose_name="원본파일 제공", null=True, blank=True)

    # 디자인&그래픽 or 음향
    is_possible_commercial_use = models.BooleanField(verbose_name="상업적 이용 가능", null=True, blank=True)

    # 공통
    price = models.PositiveIntegerField(verbose_name="금액")

    # 영상&사진
    possible_region = models.CharField(verbose_name="(영상) 서비스 가능 지역", max_length=80, null=True, blank=True)

    # 영상&사진 or 음향
    running_time = models.CharField(verbose_name="러닝타임(초) or 장 수(글자크기: 12P)", null=True, blank=True, max_length=64)

    # 음향
    is_copyright_transfer = models.BooleanField(verbose_name="저작권 양도 가능", null=True, blank=True)

    def __str__(self):
        return f"{self.title}({self.type}, {self.id})"

    class Meta:
        verbose_name = "서비스 정보"
        verbose_name_plural = verbose_name


class ServiceImage(models.Model):
    service = models.ForeignKey(
        "service.Service",
        related_name="images",
        verbose_name="서비스",
        on_delete=models.CASCADE,
    )
    image = models.FileField(verbose_name="서비스 이미지", upload_to="service_images", null=True, blank=True)
    video_url = models.URLField(verbose_name="동영상 url", null=True, blank=True)

    class Meta:
        verbose_name = "서비스 설명 파일"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.id}(service: {self.service}"
