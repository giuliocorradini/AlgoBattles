from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.db.models import Exists, OuterRef
from django.db.transaction import atomic
from django.db.models import Q
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Presence, Challenge, User
from userprofile.serializers import UserPublicInformationSerializer
from puzzle.models import Attempt

channel_layer = get_channel_layer()
serializer = UserPublicInformationSerializer

@receiver(post_save, sender=Presence)
@receiver(post_delete, sender=Presence)
def broadcast_presence(sender, instance, **kwargs):
    print(f"Updated {instance}")
    """
    Broadcast the new list of present users to the room.
    """

    users = User.objects.filter(
        Exists(
            Presence.objects.filter(user=OuterRef('pk'))
        )
    )
    
    users_data = serializer(users, many=True).data


    channel_layer_message = {
        "type": "lobby.update",
        "members": users_data
    }

    async_to_sync(channel_layer.group_send)("lobby", channel_layer_message)

def reject_c(c):
    if c.state != Challenge.State.WAITING:
        return
    
    c.state = Challenge.State.REJECTED
    c.save()
    async_to_sync(channel_layer.send)(c.starter.channel_name, {
        "type": "challenge.decline",
        "id": c.id
    })

@receiver(post_save, sender=Challenge)
def reject_others(sender, instance, **kwargs):
    update_fields = kwargs.get("update_fields")
    if not update_fields:
        update_fields = []
        
    if "state" in update_fields and instance.state == Challenge.State.ACCEPTED:
        with atomic():
            starter_challenges = Challenge.objects.filter(~Q(id=instance.id) & (Q(starter_id=instance.starter_id) | Q(receiver_id=instance.starter_id)))
            receiver_challenges = Challenge.objects.filter(~Q(id=instance.id) & (Q(starter_id=instance.receiver_id) | Q(receiver_id=instance.receiver_id)))

            for c in starter_challenges:
                reject_c(c)

            for c in receiver_challenges:
                reject_c(c)

@receiver(post_save, sender=Attempt)
def check_passed_attempt_for_challenge(sender, instance: Attempt, **kwargs):
    print("responding to attempt post save")
    if not instance.passed:
        return
    
    print(instance)
    
    challenge = instance.development.challenge

    if challenge and challenge.state == Challenge.State.ONGOING:
        challenge.state = Challenge.State.COMPLETED
        challenge.winner = instance.development.user
        challenge.save()

        async_to_sync(channel_layer.send)(challenge.sender.channel_name, {
            "type": "declare.winner",
            "winner": instance.development.user.id
        })

        async_to_sync(channel_layer.send)(challenge.receiver.channel_name, {
            "type": "declare.winner",
            "winner": instance.development.user.id
        })
