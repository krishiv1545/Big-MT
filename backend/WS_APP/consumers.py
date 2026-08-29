import json

from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ChatRoom


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        user = self.scope["user"]

        if not user.is_authenticated:
            await self.close(code=4001)
            return

        self.room_uuid = self.scope["url_route"]["kwargs"]["room_uuid"]

        try:
            room = await ChatRoom.objects.aget(uuid=self.room_uuid)
        except ChatRoom.DoesNotExist:
            await self.close(code=4004)
            return

        authorized_rooms = self.scope["session"].get(
            "authorized_rooms",
            []
        )

        if str(room.id) not in authorized_rooms:
            await self.close(code=4003)
            return

        self.room_group_name = f"chat_room_{self.room_uuid}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )

        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name,
            )

    async def receive(self, text_data):
        data = json.loads(text_data)

        message = data.get("message", "").strip()

        if not message:
            return

        username = self.scope["user"].username

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "username": username,
                "message": message,
            },
        )

    async def chat_message(self, event):
        await self.send(
            text_data=json.dumps({
                "type": "chat_message",
                "username": event["username"],
                "message": event["message"],
            })
        )