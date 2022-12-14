from django.urls import path

from api.v1.inquiry.views import (
    InquiryListCreateView,
)

urlpatterns = [
    path("", InquiryListCreateView.as_view()),
    # add etc action view
]
