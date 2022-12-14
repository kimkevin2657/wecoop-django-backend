from api.v1.service_review.serializers import ServiceReviewListCreateSerializer
from app.portfolio.models import Portfolio
from app.user.models import User
from app.portfolio_bookmark.models import PortfolioBookmark
from app.service.models import Service, ServiceImage, ServiceInfo
from app.service_bookmark.models import ServiceBookmark
from app.service_review.models import ServiceReview
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets, status
from rest_framework.response import Response

from .pagination import ServicePagination
from .filters import ServiceFilter
from .permissions import ServicePermission
from .serializers import (
    PortfolioListSerializer,
    ServiceDetailSerializer,
    ServiceImageListSerializer,
    ServiceInfoListSerializer,
    ServiceListSerializer,
)


class ServiceListView(generics.ListAPIView):
    queryset = Service.objects.select_related("user").exclude(Q(is_visible=False) | Q(is_deleted=True))
    serializer_class = ServiceListSerializer
    permission_classes = [ServicePermission]
    filter_backends = [DjangoFilterBackend]
    filter_class = ServiceFilter
    pagination_class = ServicePagination

    def get_queryset(self):
        return super().get_queryset().filter(approve_status="승인").order_by("created").distinct()


class ServiceDetailView(generics.RetrieveDestroyAPIView, generics.UpdateAPIView):
    queryset = Service.objects.select_related("user").exclude(Q(is_deleted=True))
    serializer_class = ServiceDetailSerializer
    permission_classes = [ServicePermission]

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()


class ServiceImageDetailView(generics.UpdateAPIView):
    queryset = ServiceImage.objects.select_related("service")
    serializer_class = ServiceImageListSerializer


class ServiceInfoDetailView(generics.UpdateAPIView):
    queryset = ServiceInfo.objects.select_related("service")
    serializer_class = ServiceInfoListSerializer


class UserProductListView(viewsets.ViewSet):
    def list(self, request):
        data = request.query_params
        user_id = data.get("userId")
        service_queryset = Service.objects.select_related("user").filter(Q(user_id=user_id) & Q(is_deleted=False))
        services = ServiceListSerializer(service_queryset, context={"request": request}, many=True)

        portfolio_queryset = Portfolio.objects.filter(user_id=user_id)
        portfolios = PortfolioListSerializer(portfolio_queryset, many=True, context={"request": request})

        service_review_filter = Q(user_id=user_id)
        users = User.objects.filter(id=user_id)
        if not users:
            return Response({"msg": f"id:{user_id}의 유저가 존재하지 않습니다."}, status=status.HTTP_401_UNAUTHORIZED)
        user = users.first()
        if user.type == "freelancer":
            service_review_filter = Q(service__user=user)

        service_review_queryset = ServiceReview.objects.filter(service_review_filter)
        reviews = ServiceReviewListCreateSerializer(service_review_queryset, many=True, context={"request": request})

        return Response(
            {
                "is_mine": str(user_id) == str(request.user.id),
                "services": services.data,
                "portfolios": portfolios.data,
                "reviews": reviews.data,
            }
        )


class UserBookmarkListView(viewsets.ViewSet):
    def list(self, request):
        data = request.query_params
        user_id = data.get("userId")
        service_ids = ServiceBookmark.objects.filter(user_id=user_id).values_list("service", flat=True)
        service_queryset = Service.objects.exclude(is_deleted=True).filter(id__in=service_ids)
        services = ServiceListSerializer(service_queryset, context={"request": request}, many=True)

        portfolio_ids = PortfolioBookmark.objects.filter(user_id=user_id).values_list("portfolio", flat=True)
        portfolio_queryset = Portfolio.objects.filter(id__in=portfolio_ids)
        portfolios = PortfolioListSerializer(portfolio_queryset, many=True, context={"request": request})

        return Response(
            {
                "is_mine": str(user_id) == str(request.user.id),
                "services": services.data,
                "portfolios": portfolios.data,
            }
        )
