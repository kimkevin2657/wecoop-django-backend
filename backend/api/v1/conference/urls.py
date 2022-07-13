from django.urls import path

from api.v1.conference.views import ConferenceCreateView

urlpatterns = [
    path('', ConferenceCreateView.as_view()),
]
