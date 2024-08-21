import json
from channels.generic.websocket import JsonWebsocketConsumer


class MultiplayerConsumer(JsonWebsocketConsumer):
    def connect(self):
        if self.scope['user'].is_anonymous:
            self.close(3000, "Invalid token")
        
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive_json(self, content):

        self.send_json({
            "message": self.scope['user'].username
        })

        self.send_json({
            "message": content.get("message")
        })