from rest_framework import generics, status, response, viewsets

from django.db import transaction
from .filters import PortfolioBookmarkFilter
from .permissions import PortfolioBookmarkPermission
from .serializers import (
    PortfolioBookmarkListCreateSerializer,
    BookmarkedPortfolioSerializer,
)
from app.portfolio_bookmark.models import PortfolioBookmark


class PortfolioBookmarkListCreateView(generics.ListCreateAPIView):
    queryset = PortfolioBookmark.objects.select_related("user", "portfolio")
    serializer_class = PortfolioBookmarkListCreateSerializer
    permission_classes = [PortfolioBookmarkPermission]
    filterset_class = PortfolioBookmarkFilter
    return_status = status.HTTP_201_CREATED
    response_data = {}

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        # if self.return_status == status.HTTP_201_CREATED:
        #     self.response_data = serializer.data
        return response.Response(self.response_data, status=self.return_status, headers=headers)

    @transaction.atomic()
    def perform_create(self, serializer):
        request = self.request

        try:
            portfolio_bookmark = PortfolioBookmark.objects.get(
                portfolio_id=request.data["portfolio"], user=request.user
            )
            portfolio_bookmark.delete()
            self.response_data = {"data": None, "message": "포트폴리오 찜이 취소되었습니다."}
        except PortfolioBookmark.DoesNotExist:
            serializer.save(user=request.user)
            self.response_data = {"data": serializer.data, "message": "포트폴리오가 찜목록에 추가되었습니다."}
