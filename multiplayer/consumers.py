from channels.generic.websocket import JsonWebsocketConsumer
from .models import Presence, Challenge
from asgiref.sync import async_to_sync

class MultiplayerConsumer(JsonWebsocketConsumer):
     def connect(self):
        self.user = self.scope['user']
        if self.user.is_anonymous:
             self.close(3000, "Invalid token")
        
        self.accept()
    
        async_to_sync(self.channel_layer.group_add)("lobby", self.channel_name)
        self.add_presence(self.user, self.channel_name)

     def disconnect(self, close_code):
        if not self.user.is_anonymous:
            self.remove_presence(self.user)
        
     def remove_presence(self, user):
        Presence.objects.filter(user=user).delete()

     def add_presence(self, user, channel_name):
        if user.is_anonymous:
            return

        p, _ = Presence.objects.get_or_create(user=user)
        p.channel_name = channel_name
        p.save()

        self.presence = p

     def lobby_update(self, event):
        self.send_json({
            "members": event.get("members")
        })

     def challenge_request(self, event):
        """Receive challenge from other users on Channel"""
        challenge_id = event.get("challenge").get("id")
        c =  Challenge.objects.filter(id=challenge_id).get()

        # Update client
        self.send_json({
            "challenge": {
                "from": c.starter.id,
                "id": c.id
            }
        })

     def challenge_accept(self, event):
        """The opponent has accepted the challenge, send response"""

        print(f"Opponent accepted challenge {event}")

        self.send_json({
            "accept": {
                "challenge": {
                    "id": event.get("id")
                }
            }
        })

     def challenge_decline(self, event):
        self.send_json({
            "decline": {
                "challenge": {
                    "id": event.get("id")
                }
            }
        })

     def receive_json(self, content):
        """Process actions from the connected client"""

        if "challenge" in content:

            # route challenge to appropriate recipient
            rival_id = content.get("challenge").get("to")
            rival =  Presence.objects.filter(user_id=rival_id).get()

            if  Challenge.objects.filter(starter=self.presence, receiver=rival).exists():
                self.send_json({
                    "error": "A challenge for this user is already created."
                })
                return

            challenge =  Challenge.objects.create(starter=self.presence, receiver=rival)

            async_to_sync(self.channel_layer.send)(rival.channel_name, {
                "type": "challenge.request",
                "challenge": {
                    "id": challenge.id
                }
            })

        print(content)

        if "accept" in content:

            challenge_id = content.get("accept").get("challenge").get("id")
            challenge = Challenge.objects.filter(id=challenge_id, receiver_id=self.presence.id)
            
            if not challenge.exists():
                print("challenge does not exists")
                return
            
            challenge = challenge.get()

            challenge.state = challenge.State.ACCEPTED
            challenge.save()

            async_to_sync(self.channel_layer.send)(challenge.starter.channel_name, {
                "type": "challenge.accept",
                "id": challenge.id
            })

        if "decline" in content:

            challenge_id = content.get("decline").get("challenge").get("id")
            challenge = Challenge.objects.filter(id=challenge_id, receiver_id=self.presence.id)
            
            if not challenge.exists():
                print("challenge does not exists")
                return
            
            challenge = challenge.get()

            challenge.state = challenge.State.REJECTED
            challenge.save()

            print(f"sending to {challenge.starter.channel_name}")

            async_to_sync(self.channel_layer.send)(challenge.starter.channel_name, {
                "type": "challenge.decline",
                "id": challenge.id
            })