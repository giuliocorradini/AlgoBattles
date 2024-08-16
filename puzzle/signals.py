"""
puzzle.signals

This module provides callbacks for post_save signals to optimize the computation of completed developments for
a given puzzle and a given user.

https://docs.djangoproject.com/en/5.0/ref/signals/#post-save
https://docs.djangoproject.com/en/5.0/topics/signals/
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Development, Attempt

@receiver(post_save)
def update_completed_dev_on_attempt(sender, instance, created, raw, using, update_fields, **kwargs):
    """Run when any attempt is marked as passed"""
    if sender is Attempt and instance.passed:
        instance.development.completed = True
        instance.save()

