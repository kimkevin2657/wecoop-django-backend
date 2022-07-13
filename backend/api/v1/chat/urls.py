from django.urls import path

from api.v1.chat.views import ChatListView, MessageListView

urlpatterns = [
    path('', ChatListView.as_view()),
    path('/<int:pk>/message', MessageListView.as_view()),
]
