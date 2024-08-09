from django.apps import AppConfig


class UserprofileConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'userprofile'

    def ready(self):
        # Implicitly connect signals (refer to documentation)
        from . import signals