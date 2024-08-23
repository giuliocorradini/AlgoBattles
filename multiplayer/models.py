from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class Presence(models.Model):
    """
    Presence of a user in the multiplayer lobby. Associates a user with its channel_name
    when online.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    channel_name = models.CharField(max_length=255)


class Challenge(models.Model):
    starter = models.ForeignKey(Presence, on_delete=models.CASCADE)
    receiver = models.ForeignKey(Presence, on_delete=models.CASCADE, related_name="rival")
    
    class State(models.IntegerChoices):
        WAITING = 1, _("Waiting")
        REJECTED = 2, _("Rejected")
        ACCEPTED = 3, _("Accepted")
        ONGOING = 4, _("Ongoing")
        COMPLETED = 5, _("Completed")
        TIMES_UP = 6, _("Time's up")

    state = models.IntegerField(
        choices=State.choices,
        default=State.WAITING
    )

    puzzle = models.OneToOneField('puzzle.Puzzle', on_delete=models.SET_NULL, null=True)

    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, default=None)

    class Meta:
        unique_together = ('starter', 'receiver')
