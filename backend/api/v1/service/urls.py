from django.urls import path
from .views import (
    ServiceListView,
    ServiceDetailView,
    UserBookmarkListView,
    UserProductListView,
    ServiceImageDetailView,
    ServiceInfoDetailView,
)


urlpatterns = [
    path("", ServiceListView.as_view()),
    path("/<int:pk>", ServiceDetailView.as_view()),
    path("/images/<int:pk>", ServiceImageDetailView.as_view()),
    path("/infos/<int:pk>", ServiceInfoDetailView.as_view()),
    path("/all_bookmark", UserBookmarkListView.as_view({"get": "list"})),
    path("/all_products", UserProductListView.as_view({"get": "list"})),
]
