from django.apps import AppConfig


class MultiplayerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'multiplayer'

    def ready(self):
        from . import signals
