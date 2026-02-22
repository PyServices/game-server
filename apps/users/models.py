"""
User auth per .cursor/docs/core/auth/user-auth.md and update.md

Django User + UserProfile for: name, lastName, born, metaData, phone_number, device_id
"""
from django.db import models
from django.conf import settings


class UserProfile(models.Model):
    """Extended profile: born, metaData, phone_number, device_id."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    born = models.DateField(null=True, blank=True)
    meta_data = models.JSONField(default=dict, blank=True)
    phone_number = models.CharField(max_length=32, blank=True)
    device_id = models.CharField(max_length=256, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.username}"
