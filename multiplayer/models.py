from django.db import models
from django.contrib.auth.models import User

class Presence(models.Model):
    """
    Presence of a user in the multiplayer lobby
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    channel_name = models.CharField(max_length=255)
