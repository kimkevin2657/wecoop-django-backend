from api.v1.user.serializers import ServiceUserSerializer
from app.portfolio.models import Portfolio
from app.portfolio_bookmark.models import PortfolioBookmark
from app.service.models import Service, ServiceImage, ServiceInfo
from app.service_bookmark.models import ServiceBookmark
from app.service_review.models import ServiceReview
from app.user.models import User
from django.db.models import Q, Sum
from rest_framework import serializers


class ServiceImageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceImage
        fields = "__all__"


class ServiceInfoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceInfo
        fields = "__all__"


class ServiceReviewListSerializer(serializers.ModelSerializer):
    user_nickname = serializers.CharField(read_only=True, source="user.nickname")

    class Meta:
        model = ServiceReview
        fields = [
            "id",
            "user_nickname",
            "content",
            "score",
            "service",
            "service_info",
            "service_request",
            "created",
            "updated",
        ]


class ServiceListSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField(read_only=True)
    review_count = serializers.SerializerMethodField(read_only=True)
    freelancer_id = serializers.CharField(source="user.id", read_only=True)
    has_career_mark = serializers.BooleanField(source="user.has_career_mark", read_only=True)
    has_bookmark = serializers.SerializerMethodField(read_only=True)
    is_mine = serializers.SerializerMethodField(read_only=True)
    has_video_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Service
        fields = [
            "id",
            "freelancer_id",
            "has_tax_bill",
            "has_career_mark",
            "title",
            "description",
            "category",
            "sub_category",
            "thumbnail",
            "score",
            "created",
            "price",
            "review_count",
            "has_bookmark",
            "is_mine",
            "is_visible",
            "has_video_url",
            "weekend_work_type",
        ]

    def get_has_video_url(self, obj):
        res = (
            ServiceImage.objects.select_related("service")
            .exclude(video_url="")
            .filter(Q(service=obj) & Q(video_url__isnull=False))
            .exists()
        )
        return res

    def get_is_mine(self, obj):
        return self.context["request"].user == obj.user

    def get_has_bookmark(self, obj):
        me = self.context["request"].user
        if not me.is_authenticated:
            return False
        return ServiceBookmark.objects.select_related("user", "service").filter(user=me, service=obj).exists()

    def get_price(self, obj):
        infos = ServiceInfo.objects.select_related("service").filter(Q(service=obj) & Q(type="basic"))
        if not infos:
            return 0
        info = infos.first()
        return info.price

    def get_review_count(self, obj):
        return obj.reviews.count()


class PortfolioListSerializer(serializers.ModelSerializer):
    has_bookmark = serializers.SerializerMethodField(read_only=True)
    is_mine = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Portfolio
        fields = [
            "id",
            "title",
            "category",
            "main_image",
            "has_bookmark",
            "is_mine",
            "is_visible",
            "video_url",
            "price",
            "work_start_year",
            "work_start_month",
            "work_end_year",
            "work_end_month",
            "images",
        ]

    def get_is_mine(self, obj):
        return self.context["request"].user == obj.user

    def get_has_bookmark(self, obj):
        me = self.context["request"].user
        if not me.is_authenticated:
            return False
        return PortfolioBookmark.objects.select_related("user", "portfolio").filter(user=me, portfolio=obj).exists()


class ServiceDetailSerializer(serializers.ModelSerializer):
    images = ServiceImageListSerializer(read_only=True, many=True)
    infos = ServiceInfoListSerializer(read_only=True, many=True)
    reviews = ServiceReviewListSerializer(read_only=True, many=True)
    portfolios = serializers.SerializerMethodField(read_only=True)
    review_count = serializers.SerializerMethodField(read_only=True)
    freelancer = serializers.SerializerMethodField(read_only=True)
    has_bookmark = serializers.SerializerMethodField(read_only=True)
    is_mine = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Service
        fields = [
            "id",
            "is_mine",
            "is_visible",
            "freelancer",
            "title",
            "description",
            "menu",
            "category",
            "sub_category",
            "thumbnail",
            "score",
            "weekend_work_type",
            "has_tax_bill",
            "images",
            "infos",
            "reviews",
            "portfolios",
            "review_count",
            "has_bookmark",
        ]

    def get_is_mine(self, obj):
        return self.context["request"].user == obj.user

    def get_freelancer(self, obj):
        user = User.objects.get(id=obj.user_id)
        serializer = ServiceUserSerializer(instance=user, read_only=True, context={"request": self.context["request"]})
        user_services = Service.objects.select_related("user").exclude(is_deleted=True).filter(user=user)
        avg_score = 0
        if user_services:
            avg_score = user_services.aggregate(Sum("score"))["score__sum"] / user_services.count()
        score_count = ServiceReview.objects.select_related("user").filter(service__user=user).count()

        return {
            "id": user.id,
            "type": user.type,
            "safe_phone": user.safe_phone,
            "is_safe_phone_open": user.is_safe_phone_open,
            "nickname": user.nickname,
            "profile_image": user.profile_image,
            "score": avg_score,
            "score_count": score_count,
            "has_career_mark": user.has_career_mark,
            "contactable_start_time": user.contactable_start_time,
            "contactable_end_time": user.contactable_end_time,
            "description": user.description,
            "careers": serializer.data["careers"],
        }

    def get_has_bookmark(self, obj):
        me = self.context["request"].user
        if not me.is_authenticated:
            return False
        return ServiceBookmark.objects.select_related("user", "service").filter(user=me, service=obj).exists()

    def get_review_count(self, obj):
        return obj.reviews.count()

    def get_portfolios(self, obj):
        portfolios = Portfolio.objects.select_related("user").filter(
            Q(user=obj.user) & Q(category=obj.get_menu_display()) & Q(is_visible=True)
        )
        serializer = PortfolioListSerializer(portfolios, many=True, context={"request": self.context["request"]})
        return serializer.data
