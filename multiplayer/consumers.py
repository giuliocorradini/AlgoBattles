from channels.generic.websocket import JsonWebsocketConsumer
from .models import Presence, Challenge
from puzzle.models import Puzzle
from asgiref.sync import async_to_sync
from .auth import get_user
from .serializers import ChallengeSerializer
from django.db.models import Q

class MultiplayerConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.user = None
        self.challenge = None
        self.accept()

    def authenticate(self, token):
        self.user = get_user(token)
        
        if self.user.is_anonymous:
            self.close(3000, "Invalid token")
        
        self.auth = True

    def disconnect(self, close_code):
        if self.user and not self.user.is_anonymous:
            self.remove_presence(self.user)
        
    def enter_lobby(self):
        async_to_sync(self.channel_layer.group_add)("lobby", self.channel_name)
        self.add_presence(self.user, self.channel_name)

        p = Challenge.objects.filter(Q(starter=self.presence) | Q(receiver=self.presence), state=Challenge.State.ONGOING)

        if p.exists():
            chal = p.get()
            opponent = chal.starter if chal.receiver == self.presence else chal.receiver
            self.send_json({
                "restore": {
                    "challenge": {
                        "id": chal.id
                    },
                    "puzzle": {
                        "id": chal.puzzle.id
                    },
                    "opponent": {
                        "id": opponent.user.id,
                        "username": opponent.user.username,
                    }
                }
            })

        else:
            self.challenge_update()

    def remove_presence(self, user):
        # Fold open challenge before exiting
        if self.challenge:
            opponent = self.challenge.starter if self.challenge.receiver == self.presence else self.challenge.receiver

            async_to_sync(self.channel_layer.send)(opponent.channel_name, {
                "type": "declare.winner",
                "winner": opponent.user.id
            })
            
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

    def challenge_update(self, event=None):
        my_open_challenges = Challenge.objects.filter(receiver=self.presence, state=Challenge.State.WAITING)

        self.send_json({
            "challenge": {
                "all": ChallengeSerializer(my_open_challenges, many=True).data
            }
        })


    def challenge_request(self, event):
        """Handle a new challenge from other users on Channel.
        Sends all challenges in WAITING state
        """
        challenge_id = event.get("challenge").get("id")
        c =  Challenge.objects.filter(id=challenge_id).get()

        my_open_challenges = Challenge.objects.filter(receiver=self.presence, state=Challenge.State.WAITING)

        # Update client
        self.send_json({
            "challenge": {
                "last": {
                    "id": c.id,
                    "from": {
                        "id": c.starter.user.id,
                        "username": c.starter.user.username
                    }
                },
                "all": ChallengeSerializer(my_open_challenges, many=True).data
            }
        })

    def challenge_accept(self, event):
        """The opponent has accepted the challenge, send response"""

        print(f"Opponent accepted challenge {event}")

        self.challenge = Challenge.objects.get(id=event.get("id"))

        self.send_json({
            "accept": {
                "challenge": {
                    "id": event.get("id")
                },
                "opponent": {
                    "id": self.challenge.receiver.user.id,
                    "username": self.challenge.receiver.user.username,
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

    def challenge_setpuzzle(self, event):
        self.send_json(event.get("message"))

    def declare_winner(self, event):
        """Receive channel message from database hook signal (check_passed_attempt_for_challenge)
        And terminate the challenge telling participants who wins.
        """

        self.send_json({
            "stop": {
                "result": ("winner" if event.get("winner") == self.user.id else "loser")
            }
        })

        self.challenge = None

    def receive_json(self, content):
        """Process actions from the connected client"""

        print(content)

        if "authenticate" in content:
            token = content.get("authenticate").get("token")
            self.authenticate(token)

        if not self.auth:
            self.close()
            return

        if "enter" in content:
            self.enter_lobby()

        elif "challenge" in content:

            if Challenge.objects.filter((Q(state=Challenge.State.ACCEPTED) | Q(state=Challenge.State.ONGOING)) & (Q(starter_id=self.presence.id) | Q(receiver_id=self.presence.id))).exists():
                self.send_json({
                    "error": "Your already started a challenge."
                })

            # route challenge to appropriate recipient
            try:
                rival_id = int(content.get("challenge").get("to"))
            except ValueError:
                self.close(1002, "Invalid rival ID")

            if rival_id == self.user.id:
                self.send_json({
                    "error": "You can't challenge yourself"
                })
                return

            rival = Presence.objects.filter(user_id=rival_id).get()

            if not rival:
                self.send_json({
                    "error": "Invalid rival ID"
                })
                return

            if  Challenge.objects.filter(starter=self.presence, receiver=rival, state=Challenge.State.WAITING).exists():
                self.send_json({
                    "error": "A challenge for this user was already sent."
                })
                return

            challenge, created = Challenge.objects.get_or_create(starter=self.presence, receiver=rival)
            if not created:
                challenge.delete()
                challenge = Challenge.objects.create(starter=self.presence, receiver=rival)

            async_to_sync(self.channel_layer.send)(rival.channel_name, {
                "type": "challenge.request",
                "challenge": {
                    "id": challenge.id
                }
            })

        elif "accept" in content:

            challenge_id = content.get("accept").get("challenge").get("id")
            challenge = Challenge.objects.filter(id=challenge_id, receiver_id=self.presence.id)
            
            if not challenge.exists():
                print("challenge does not exists")
                return
            
            challenge = challenge.get()

            challenge.state = challenge.State.ACCEPTED
            challenge.save(update_fields=["state"])

            self.challenge = challenge

            async_to_sync(self.channel_layer.send)(challenge.starter.channel_name, {
                "type": "challenge.accept",
                "id": challenge.id
            })

        elif "decline" in content:

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

        elif "puzzle" in content:
            puzzle_id = content.get("puzzle").get("set").get("id")

            if self.challenge.starter == self.presence:
                self.challenge.puzzle = Puzzle.objects.get(id=puzzle_id)
                self.challenge.state = Challenge.State.ONGOING
                self.challenge.save()

                async_to_sync(self.channel_layer.send)(self.challenge.receiver.channel_name, {
                    "type": "challenge.setpuzzle",
                    "message": {
                        "puzzle": {
                            "id": puzzle_id
                        }
                    }
                })
