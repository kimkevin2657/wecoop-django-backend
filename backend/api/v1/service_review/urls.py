from django.urls import path

from .views import (
    ServiceReviewListCreateView,
    ServiceReviewDetailUpdateView,
)

urlpatterns = [
    path("", ServiceReviewListCreateView.as_view()),
    path("<int:pk>/", ServiceReviewDetailUpdateView.as_view()),
    # add etc action view
]
