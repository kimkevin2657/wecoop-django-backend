from django.urls import path, include
from rest_framework import routers

from .views import (
    PortfolioViewSet,
)

router = routers.DefaultRouter()
router.register("", PortfolioViewSet)

urlpatterns = [
    path("/", include(router.urls))
    # path('/', PortfolioListCreateView.as_view()),
    # path('/<int:pk>', PortfolioDetailView.as_view()),
    # add etc action view
]
