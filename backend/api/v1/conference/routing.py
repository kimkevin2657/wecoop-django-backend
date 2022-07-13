from django.urls import path
from api.v1.conference.consumers import ConferenceConsumer

websocket_urlpatterns = [
    path('ws/conference/<str:room>', ConferenceConsumer.as_asgi()),
]
