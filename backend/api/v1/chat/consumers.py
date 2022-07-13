import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from app.chat.models import Message, Chat


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_dict = {}  # {1: chat object(1), 2: chat object(2), ...}
        self.user = self.scope['user']

        if self.user.is_authenticated:
            await self.channel_layer.group_add(
                str(self.user.pk),
                self.channel_name,
            )
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            str(self.user.pk),
            self.channel_name,
        )

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)

        if not self.chat_dict.get(data['chat_id']):
            self.chat_dict[data['chat_id']] = await self.get_chat(data['chat_id'])

        message = await self.create_message(data)

        for user in self.chat_dict[data['chat_id']]:
            await self.channel_layer.group_send(
                str(user.pk),
                {
                    'type': 'send_message',
                    'chat_id': data['chat_id'],
                    'user_id': message.user.pk,
                    'text': message.text,
                    'created': message.created.isoformat(),
                },
            )

    async def send_message(self, event):
        await self.send(text_data=json.dumps({
            'chat_id': event['chat_id'],
            'user_id': event['user_id'],
            'text': event['text'],
            'created': event['created'],
        }))

    @database_sync_to_async
    def get_chat(self, chat_id):
        try:
            chat = self.user.chat_set.prefetch_related('user_set').get(pk=chat_id)
        except Chat.DoesNotExist:
            chat = None
        return chat

    @database_sync_to_async
    def create_message(self, data):
        message = Message.objects.create(
            chat_id=data['chat_id'],
            user=self.user,
            text=data['text'],
        )
        # 상대에게 푸시알림 전송(by celery)
        return message

