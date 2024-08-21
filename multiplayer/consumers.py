import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer


class MultiplayerConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        if self.scope['user'].is_anonymous:
            await self.close(3000, "Invalid token")
        
        await self.accept()
        self.user = self.scope['user']
        self.lobby = set()
        
        await self.channel_layer.group_add("lobby", self.channel_name)

        await self.channel_layer.group_send("lobby", {
            "type": "user.entering",
            "id": self.user.id
        })

    async def disconnect(self, close_code):
        await self.channel_layer.group_send("lobby", {
            "type": "user.leaving",
            "id": self.user.id
        })

    async def receive_json(self, content):
        await self.send_json({
            "message": content.get("message")
        })

    async def user_entering(self, event):
        user_id = event.get("id")
        self.lobby.add(user_id)

        await self.send_json({
            "lobby": list(self.lobby)
        })
    
    async def user_leaving(self, event):
        user_id = event.get("id")
        self.lobby.remove(user_id)
