"""Signals for user lifecycle. isEarnable: grant resources on registration."""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model


def grant_earnable_resources(sender, instance, created, **kwargs):
    """On user creation: grant Currency/Meta with default_amount, Data with isEarnable."""
    if not created:
        return
    try:
        from apps.resources.services import UserResourceService
        UserResourceService.grant_earnable_on_registration(instance.id)
    except Exception:
        pass
