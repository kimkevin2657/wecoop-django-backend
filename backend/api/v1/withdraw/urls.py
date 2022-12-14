from django.urls import path

from .views import (
    WithdrawListCreateView,
)

urlpatterns = [
    path("", WithdrawListCreateView.as_view()),
    # add etc action view
]
