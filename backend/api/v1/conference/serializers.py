import uuid

from rest_framework import serializers

from app.conference.models import Conference


class ConferenceCreateSerializer(serializers.ModelSerializer):
    room = serializers.CharField(read_only=True)

    class Meta:
        model = Conference
        fields = ['room']

    def validate(self, attrs):
        attrs['room'] = self._get_random_room()
        return attrs

    def _get_random_room(self):
        room = uuid.uuid4().hex[:16]
        if Conference.objects.filter(room=room).exists():
            return self._get_random_room()
        return room
