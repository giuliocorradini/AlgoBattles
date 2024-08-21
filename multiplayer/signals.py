from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.db.models import Exists, OuterRef
from channels.layers import get_channel_layer
from .models import Presence, User
from userprofile.serializers import UserPublicInformationSerializer
from channels.db import database_sync_to_async

channel_layer = get_channel_layer()
serializer = UserPublicInformationSerializer

@receiver(post_save, sender=Presence)
@receiver(post_delete, sender=Presence)
async def broadcast_presence(sender, instance, **kwargs):
    """
    Broadcast the new list of present users to the room.
    """

    users = User.objects.filter(
        Exists(
            Presence.objects.filter(user=OuterRef('pk'))
        )
    )
    
    users_data = await database_sync_to_async(lambda: serializer(users, many=True).data)()


    channel_layer_message = {
        "type": "lobby.update",
        "members": users_data
    }

    await channel_layer.group_send("lobby", channel_layer_message)