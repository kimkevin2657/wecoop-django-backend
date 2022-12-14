from django.urls import path

from .views import ServicePaymentListCreateView, ServicePaymentDetailUpdateView, IamPortPaymentView

urlpatterns = [
    path("", ServicePaymentListCreateView.as_view()),
    path("/<int:pk>/", ServicePaymentDetailUpdateView.as_view()),
    path("/iamport", IamPortPaymentView.as_view()),
]
