from django.urls import path

from .views import (
    ServiceBookmarkListCreateView,
)

urlpatterns = [
    path("", ServiceBookmarkListCreateView.as_view()),
    # add etc action view
]
