from rest_framework import generics, viewsets
from rest_framework.decorators import action
from rest_framework.status import HTTP_201_CREATED, HTTP_403_FORBIDDEN
from rest_framework.response import Response
from django.db import transaction

from .filters import PortfolioFilter
from .permissions import PortfolioPermission
from .serializers import (
    PortfolioListCreateSerializer,
    PortfolioDetailSerializer,
)
from app.portfolio.models import Portfolio, PortfolioImage


class PortfolioViewSet(viewsets.ModelViewSet):
    queryset = Portfolio.objects.select_related("user")
    serializer_action_classes = {
        "list": PortfolioListCreateSerializer,
    }
    serializer_class = PortfolioDetailSerializer
    permission_classes = [PortfolioPermission]
    filterset_class = PortfolioFilter

    @action(methods=["post"], detail=False)
    def generate_images(self, request, pk=None):
        images = request.FILES.getlist("images")
        image_urls = []

        for image in images:
            pg_image = PortfolioImage.objects.create(image=image)
            image_urls.append(pg_image.image.url)
        return Response(image_urls)

    @transaction.atomic()
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @transaction.atomic()
    def perform_update(self, serializer):
        serializer.save()


class PortfolioDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Portfolio.objects.select_related("user")
    serializer_class = PortfolioDetailSerializer
    permission_classes = [PortfolioPermission]
