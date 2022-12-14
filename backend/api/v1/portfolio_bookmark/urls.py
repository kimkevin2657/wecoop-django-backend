from django.urls import path

from .views import (
    PortfolioBookmarkListCreateView,
)

urlpatterns = [
    path("", PortfolioBookmarkListCreateView.as_view()),
    # add etc action view
]
