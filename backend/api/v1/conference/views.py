from rest_framework.generics import CreateAPIView

from api.v1.conference.serializers import ConferenceCreateSerializer


class ConferenceCreateView(CreateAPIView):
    serializer_class = ConferenceCreateSerializer