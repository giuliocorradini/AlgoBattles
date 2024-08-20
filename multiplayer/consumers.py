import json
from channels.generic.websocket import JsonWebsocketConsumer


class MultiplayerConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive_json(self, content):

        self.send_json({
            "message": content.get("message")
        })