from django.db import transaction

from rest_framework import generics, status
from rest_framework.response import Response

from .filters import ServiceBookmarkFilter
from .permissions import ServiceBookmarkPermission
from .serializers import (
    ServiceBookmarkListCreateSerializer,
)
from app.service_bookmark.models import ServiceBookmark


class ServiceBookmarkListCreateView(generics.ListCreateAPIView):
    queryset = ServiceBookmark.objects.select_related("user", "service")
    serializer_class = ServiceBookmarkListCreateSerializer
    permission_classes = [ServiceBookmarkPermission]
    filterset_class = ServiceBookmarkFilter
    return_status = status.HTTP_201_CREATED
    response_data = {}

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        # if self.return_status == status.HTTP_201_CREATED:
        #     self.response_data = serializer.data
        return Response(self.response_data, status=self.return_status, headers=headers)

    @transaction.atomic()
    def perform_create(self, serializer):
        request = self.request

        try:
            service_bookmark = ServiceBookmark.objects.get(service_id=request.data["service"], user=request.user)
            service_bookmark.delete()
            self.response_data = {"data": None, "message": "서비스 찜이 취소되었습니다."}
        except ServiceBookmark.DoesNotExist:
            serializer.save(user=request.user)
            self.response_data = {"data": serializer.data, "message": "서비스가 찜목록에 추가되었습니다."}
