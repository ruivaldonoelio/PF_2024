from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import sync_to_async
from .models import Mensagens, Forum
from django.contrib.auth import get_user_model

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.forum_id = self.scope['url_route']['kwargs']['forum_id']
        self.room_group_name = f'forum_{self.forum_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        user = self.scope['user']
        forum = await sync_to_async(Forum.objects.get)(id=self.forum_id)


        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'emissor': user.username
            }
        )

    async def chat_message(self, event):
        message = event['message']
        emissor = event['emissor']
        hora = datetime.today()
        hora_atual = hora.strftime('%B %d, %Y, %I:%M %p').replace("AM", "a.m.")

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'emissor': emissor,
            'hora': hora_atual,
        }))
