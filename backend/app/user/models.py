import random

from app.common.models import BaseManagerMixin, BaseModel, BaseModelMixin
from app.device.models import Device
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.db import models


class UserManager(DjangoUserManager, BaseManagerMixin):
    def _create_user(self, email, password, **extra_fields):
        email = self.model.normalize_username(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class UserTypeChoices(models.TextChoices):
    CLIENT = "client", "의뢰인"
    FREELANCER = "freelancer", "프리랜서"
    ADMIN = "admin", "관리자"


class User(AbstractUser, BaseModelMixin):
    first_name = None
    last_name = None
    username = None

    name = models.CharField(verbose_name="실명", max_length=16, null=True, blank=True)
    nickname = models.CharField(verbose_name="닉네임", max_length=16, null=True)
    email = models.EmailField(verbose_name="이메일", unique=True, max_length=64)
    phone = models.CharField(verbose_name="휴대폰", max_length=11, null=True, blank=True)
    contactable_phone = models.CharField(verbose_name="연락 가능한 번호", max_length=11, null=True, blank=True)
    contactable_start_time = models.CharField(verbose_name="연락 가능한 시작시간", max_length=12, null=True, blank=True)
    contactable_end_time = models.CharField(verbose_name="연락 가능한 종료시간", max_length=12, null=True, blank=True)
    safe_phone = models.CharField(verbose_name="안심번호", max_length=32, null=True, blank=True)
    is_safe_phone_open = models.BooleanField(verbose_name="안심번호 공개 여부", default=False)
    possible_withdraw_price = models.PositiveIntegerField(verbose_name="출금 가능 수익금", default=0, blank=True)

    type = models.CharField(verbose_name="유형", max_length=16, choices=UserTypeChoices.choices, null=True)
    profile_image = models.TextField(verbose_name="프로필 이미지", null=True, blank=True)
    resident_number = models.CharField(verbose_name="주민등록번호", max_length=13, null=True, blank=True)
    account_number = models.CharField(verbose_name="수익금 출금 계좌", max_length=24, null=True, blank=True)
    bank_name = models.CharField(verbose_name="은행명", max_length=12, null=True, blank=True)

    is_email_receive = models.BooleanField(verbose_name="이메일 수신", default=True)
    is_sms_receive = models.BooleanField(verbose_name="SMS 수신", default=True)
    has_career_mark = models.BooleanField(verbose_name="경력인증 유무", default=False)
    description = models.TextField(verbose_name="자기소개", null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # 빈값 유지
    VERIFY_FIELDS = ["email", "type"]  # 회원가입 시 검증 받을 필드 (email, phone)
    REGISTER_FIELDS = ["email", "type"]  # 회원가입 시 입력 받을 필드 (email, phone, password)

    objects = UserManager()

    class Meta:
        verbose_name = "유저"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.nickname

    def connect_device(self, uid, token):
        Device.objects.update_or_create(uid=uid, defaults={"user": self, "token": token})

    def disconnect_device(self, uid):
        self.device_set.filter(uid=uid).delete()

    @classmethod
    def generate_email(cls):
        return "".join(
            [random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") for _ in range(20)]
        )


class EducationStatusChoices(models.TextChoices):
    Attending = "attending", "재학"
    PAUSE = "pause", "휴학"
    COMPLETE = "complete", "이수"
    GRADUATE = "graduate", "졸업"


class CheckChoices(models.TextChoices):
    WAIT = "미확인", "미확인"
    APPROVE = "미승인", "미승인"
    REJECT = "승인", "승인"


class UserEducation(BaseModel):
    user = models.OneToOneField("user.User", on_delete=models.CASCADE, related_name="education")
    university_name = models.CharField(verbose_name="학교명", max_length=24, null=True)
    major_name = models.CharField(verbose_name="전공", max_length=24, null=True)
    status = models.CharField(
        verbose_name="상태",
        choices=EducationStatusChoices.choices,
        max_length=12,
        null=True,
    )
    image = models.TextField(verbose_name="이미지", null=True, blank=True)
    certificate_status = models.CharField(
        verbose_name="승인 상태", default="미확인", max_length=16, choices=CheckChoices.choices
    )

    class Meta:
        verbose_name = "학력/전공(선택)"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.university_name}/{self.user}"


class UserCareer(BaseModel):
    user = models.ForeignKey("user.User", on_delete=models.CASCADE, related_name="careers")
    company_name = models.CharField(verbose_name="회사명", max_length=24, null=True, blank=True)
    is_company_open = models.BooleanField(verbose_name="회사명 표시", null=True)
    department = models.CharField(verbose_name="근무부서", max_length=24, null=True, blank=True)
    rank = models.CharField(verbose_name="직위", max_length=16, null=True, blank=True)
    year = models.PositiveIntegerField(verbose_name="년", null=True)
    month = models.PositiveIntegerField(verbose_name="개월", null=True)
    is_freelancer = models.BooleanField(verbose_name="프리랜서 경력 유무", null=True)
    image = models.TextField(verbose_name="이미지", null=True, blank=True)
    certificate_status = models.CharField(
        verbose_name="승인 상태", default="미확인", max_length=16, choices=CheckChoices.choices
    )

    class Meta:
        verbose_name = "경력사항(선택)"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.company_name}/{self.user}"


class UserCertificate(BaseModel):
    user = models.ForeignKey("user.User", on_delete=models.CASCADE, related_name="certificates")
    certificate_name = models.CharField(verbose_name="자격증명", max_length=24, null=True)
    obtain_date = models.DateField(verbose_name="자격 취득일", null=True)
    agency = models.CharField(verbose_name="발급기관", max_length=16, null=True)
    image = models.TextField(verbose_name="이미지", null=True, blank=True)
    certificate_status = models.CharField(
        verbose_name="승인 상태", default="미확인", max_length=16, choices=CheckChoices.choices
    )

    class Meta:
        verbose_name = "자격증(선택)"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.certificate_name}/{self.user}"


class CeoInfo(BaseModel):
    user = models.OneToOneField("user.User", on_delete=models.CASCADE, related_name="ceo_info")
    company_name = models.CharField(verbose_name="기업명", max_length=24)
    ceo_number = models.CharField(verbose_name="사업자등록번호", max_length=36, null=True)
    business_type = models.CharField(verbose_name="사업자 유형", max_length=24)
    ceo_name = models.CharField(verbose_name="대표자명", max_length=24)
    main_category = models.CharField(verbose_name="업태", max_length=24)
    sub_category = models.CharField(verbose_name="업종", max_length=24)
    address = models.TextField(verbose_name="사업장 주소지")
    business_registration = models.TextField(verbose_name="사업자등록증", null=True)
    bank_book = models.TextField(verbose_name="사업자/대표자명 통장사본", null=True)

    tax_email = models.EmailField(verbose_name="세금계산서 수취 이메일", null=True)
    manager_name = models.CharField(verbose_name="담당자명", max_length=16)
    manager_phone = models.CharField(verbose_name="담당자 연락처", max_length=16)
    bank_name = models.CharField(verbose_name="수익금 출근 은행명", max_length=12)
    account_number = models.CharField(verbose_name="수익금 출금 계좌", max_length=24)
    bank_owner_name = models.CharField(verbose_name="예금주명 (기업 정보와 일치)", max_length=16)
    certificate_status = models.CharField(
        verbose_name="인증 승인 상태", default="미확인", max_length=16, choices=CheckChoices.choices
    )

    class Meta:
        verbose_name = "사업자정보(프리랜서, 선택)"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.company_name}/{self.user}"


class SocialKindChoices(models.TextChoices):
    KAKAO = "kakao", "카카오"
    NAVER = "naver", "네이버"
    FACEBOOK = "facebook", "페이스북"
    GOOGLE = "google", "구글"
    APPLE = "apple", "애플"


class Social(BaseModel):
    user = models.OneToOneField("user.User", on_delete=models.CASCADE)
    kind = models.CharField(verbose_name="타입", max_length=16, choices=SocialKindChoices.choices)

    class Meta:
        verbose_name = "소셜"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.user}/{self.kind}"


class TotalFile(BaseModel):
    file = models.FileField(verbose_name="파일", upload_to="files")

    class Meta:
        verbose_name = "이미지 or 영상"
        verbose_name_plural = verbose_name


class UserDeleteReason(BaseModel):
    user_email = models.EmailField(verbose_name="유저 이메일", null=True)
    user_nickname = models.CharField(verbose_name="유저 닉네임", null=True, max_length=32)
    reason = models.TextField(verbose_name="회원탈퇴 이유")

    class Meta:
        verbose_name = "회원탈퇴"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.user_nickname}"
