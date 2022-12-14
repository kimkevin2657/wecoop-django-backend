import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from app.conference.models import Conference


class EventTypeMixin:
    async def send(self, *args, **kwargs):
        raise NotImplementedError()

    async def chat(self, event):
        await self.send(text_data=json.dumps(event))

    async def join(self, event):
        # get peers from db
        await self.send(
            text_data=json.dumps(
                {
                    "type": event["type"],
                    "peers": [],  # send peers
                }
            )
        )


class ConferenceConsumer(AsyncWebsocketConsumer, EventTypeMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def connect(self):
        if await self.get_conference():
            await self.channel_layer.group_add(
                self.scope["url_route"]["kwargs"]["room"],
                self.channel_name,
            )
            await self.accept()
            # add peer from scope
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.scope["url_route"]["kwargs"]["room"],
            self.channel_name,
        )
        # remove peer

    async def receive(self, text_data=None, bytes_data=None):
        await self.channel_layer.group_send(
            self.scope["url_route"]["kwargs"]["room"],
            json.loads(text_data),
        )

    @database_sync_to_async
    def get_conference(self):
        try:
            conference = Conference.objects.get(room=self.scope["url_route"]["kwargs"]["room"])
        except Conference.DoesNotExist:
            conference = None
        return conference
