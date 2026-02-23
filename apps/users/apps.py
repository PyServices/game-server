from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'

    def ready(self):
        from django.contrib.auth import get_user_model
        from . import signals
        from django.db.models.signals import post_save
        post_save.connect(signals.grant_earnable_resources, sender=get_user_model())
