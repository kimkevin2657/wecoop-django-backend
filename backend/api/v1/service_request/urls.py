from django.urls import path

from .views import (
    ServiceRequestListCreateView,
    ServiceRequestDetailUpdateView,
)

urlpatterns = [
    path("", ServiceRequestListCreateView.as_view()),
    path("/<int:pk>/", ServiceRequestDetailUpdateView.as_view()),
    # add etc action view
]
