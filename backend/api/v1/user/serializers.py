import calendar
from datetime import datetime

from django.contrib.auth import authenticate
from django.db.models import Sum, Q
from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers, status, response
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from .examples import login_examples
from app.user.models import User, Social, SocialKindChoices, Device
from app.withdraw.models import Withdraw
from app.service_payment.models import ServicePayment
from app.service.models import Service
from app.service_review.models import ServiceReview
from .info_serializers import *


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ["uid", "token"]


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True)
    score = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "name",
            "nickname",
            "phone",
            "safe_phone",
            "is_safe_phone_open",
            "profile_image",
            "type",
            "score",
            "resident_number",
            "account_number",
            "bank_name",
            "contactable_phone",
            "contactable_start_time",
            "contactable_end_time",
            "description",
            "is_email_receive",
            "is_sms_receive",
            "last_login",
            "possible_withdraw_price",
        ]

    def get_score(self, obj):
        user_services = Service.objects.select_related("user").exclude(is_deleted=True).filter(user=obj)
        if not user_services:
            return 0
        avg_score = user_services.aggregate(Sum("score"))["score__sum"] / user_services.count()
        return avg_score


class UserSocialLoginSerializer(serializers.Serializer):
    code = serializers.CharField(write_only=True)
    state = serializers.CharField(write_only=True)
    redirect_uri = serializers.URLField(write_only=True)
    user_type = serializers.CharField(write_only=True, allow_null=True)

    def validate(self, attrs):
        if attrs["state"] not in SocialKindChoices:
            raise ValidationError({"kind": "지원하지 않는 소셜 타입입니다."})

        return attrs


@extend_schema_serializer(examples=login_examples)
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)
    device = DeviceSerializer(required=False, write_only=True, allow_null=True, help_text="모바일앱에서만 사용합니다.")
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)

    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)

    def validate(self, attrs):
        self.user = authenticate(request=self.context["request"], email=attrs["email"], password=attrs["password"])
        if self.user:
            refresh = self.get_token(self.user)
        else:
            raise ValidationError(["인증정보가 일치하지 않습니다."])

        data = dict()
        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)
        if attrs.get("device"):
            self.user.connect_device(**attrs["device"])

        return data

    def create(self, validated_data):
        return validated_data


class UserLogoutSerializer(serializers.Serializer):
    uid = serializers.CharField(required=False, help_text="기기의 고유id")

    def create(self, validated_data):
        user = self.context["request"].user
        if validated_data.get("uid"):
            user.disconnect_device(validated_data["uid"])

        return {}


def get_month_range():
    today = datetime.today().date()
    year = today.year
    month = today.month
    date = datetime(year=year, month=month, day=1).date()
    month_range = calendar.monthrange(date.year, date.month)
    last_day = today.replace(day=month_range[1])
    return [date, last_day]


class UserProfileSerializer(serializers.ModelSerializer):
    education = UserEducationSerializer(read_only=True)
    careers = UserCareerSerializer(read_only=True, many=True)
    certificates = UserCertificateSerializer(read_only=True, many=True)
    ceo_info = CeoInfoSerializer(read_only=True)
    is_mine = serializers.SerializerMethodField(read_only=True)
    email = serializers.EmailField(read_only=True)
    score = serializers.SerializerMethodField(read_only=True)
    score_count = serializers.SerializerMethodField(read_only=True)
    total_estimated_price = serializers.SerializerMethodField(read_only=True)
    withdraw_complete_price = serializers.SerializerMethodField(read_only=True)
    payment_info = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "is_mine",
            "has_career_mark",
            "possible_withdraw_price",
            "total_estimated_price",
            "withdraw_complete_price",
            "email",
            "name",
            "nickname",
            "phone",
            "safe_phone",
            "is_safe_phone_open",
            "profile_image",
            "type",
            "score",
            "score_count",
            "resident_number",
            "account_number",
            "bank_name",
            "contactable_phone",
            "contactable_start_time",
            "contactable_end_time",
            "description",
            "is_email_receive",
            "is_sms_receive",
            "education",
            "careers",
            "certificates",
            "ceo_info",
            "payment_info",
        )

    def get_payment_info(self, obj):
        me = self.context["request"].user
        if not me.is_authenticated:
            return None
        if me.type != "client":
            return None
        total_payments = ServicePayment.objects.select_related(
            "user", "service", "service_info", "service_request"
        ).filter(Q(user=me) & Q(status="구매확정"))

        [month_start_date, month_end_date] = get_month_range()

        month_filter = Q(user=me) & Q(created__gte=month_start_date) & Q(created__lte=month_end_date)
        month_payments = ServicePayment.objects.select_related(
            "user", "service", "service_info", "service_request"
        ).filter(month_filter)

        return {
            "month_payment_price": month_payments.aggregate(Sum("price"))["price__sum"] if month_payments else 0,
            "service_use_count": month_payments.count(),
            "total_payment_price": total_payments.aggregate(Sum("price"))["price__sum"] if total_payments else 0,
        }

    def get_total_estimated_price(self, obj):
        total_service_request = sum(
            ServicePayment.objects.select_related("user", "service", "service_info", "service_request")
            .filter(Q(service__user=obj) & Q(service_request__client_status="working"))
            .values_list("price", flat=True)
        )
        return total_service_request if total_service_request else 0

    def get_withdraw_complete_price(self, obj):
        total_withdraw = Withdraw.objects.select_related("user").filter(Q(user=obj) & Q(status="정산 완료"))
        return total_withdraw.aggregate(Sum("final_price"))["final_price__sum"] if total_withdraw else 0

    def get_score(self, obj):
        user_services = Service.objects.select_related("user").exclude(is_deleted=True).filter(user=obj)
        if not user_services:
            return 0
        avg_score = user_services.aggregate(Sum("score"))["score__sum"] / user_services.count()
        return avg_score

    def get_score_count(self, obj):
        return ServiceReview.objects.select_related("user").filter(service__user=obj).count()

    def get_is_mine(self, obj):
        me = self.context["request"].user
        if not me.is_authenticated:
            return False
        return me.id == obj.id


class ServiceUserSerializer(serializers.ModelSerializer):
    careers = UserCareerSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = ("careers",)
