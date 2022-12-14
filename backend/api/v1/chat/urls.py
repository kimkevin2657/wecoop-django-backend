from django.urls import path

from .views import ChatListCreateView, ChatUpdateView

urlpatterns = [
    path("", ChatListCreateView.as_view()),
    path("/<int:pk>/", ChatUpdateView.as_view()),
]
