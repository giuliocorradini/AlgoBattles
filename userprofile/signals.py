"""
userprofile.signals

This module provides a callback for post_save signals, to automatically create Profile objects
when a new User is created.

https://docs.djangoproject.com/en/5.0/topics/auth/customizing/#extending-the-existing-user-model
https://docs.djangoproject.com/en/5.0/ref/signals/#post-save
https://docs.djangoproject.com/en/5.0/topics/signals/
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

@receiver(post_save)
def create_profile_on_user(sender, instance, created, raw, using, update_fields, **kwargs):
    if sender is User and created:
        Profile.objects.create(user=instance)
