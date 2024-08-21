from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from .models import Presence

class MultiplayerConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_anonymous:
            await self.close(3000, "Invalid token")
        
        await self.accept()
        
        await self.channel_layer.group_add("lobby", self.channel_name)
        await self.add_presence(self.user, self.channel_name)

    async def disconnect(self, close_code):
        if not self.user.is_anonymous:
            await self.remove_presence(self.user)
        
    async def remove_presence(self, user):
        await Presence.objects.filter(user=user).adelete()

    async def add_presence(self, user, channel_name):
        if user.is_anonymous:
            print("sure?")
            return

        p = Presence.objects.filter(user=user)
        if await p.aexists():
            p = await p.aget()
            p.channel_name = channel_name
            await sync_to_async(p.save)()
        else:
            await Presence.objects.acreate(user=user, channel_name=channel_name)

    async def lobby_update(self, event):
        await self.send_json({
            "members": event.get("members")
        })

    async def challenge_request(self, event):
        """Receive challenge from other users on Channel"""

        await self.send_json(event)

    async def receive_json(self, content):
        if "challenge" in content:
            # route challenge to appropriate recipient
            rival_id = content.get("challenge").get("to")
            rival = await Presence.objects.filter(user_id=rival_id).aget()

            await self.channel_layer.send(rival.channel_name, {
                "type": "challenge.request",
                "challenge": {
                    "from": self.user.id
                }
            })
        