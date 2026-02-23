"""
User auth per .cursor/docs/core/auth/user-auth.md and update.md

Django User + UserProfile for: name, lastName, born, metaData, phone_number, device_id, is_guest, role
"""
from django.db import models
from django.conf import settings


class UserRole(models.TextChoices):
    USER = "user"
    ADMIN = "admin"


class UserProfile(models.Model):
    """Extended profile: born, metaData, phone_number, device_id, is_guest, role."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    born = models.DateField(null=True, blank=True)
    meta_data = models.JSONField(default=dict, blank=True)
    phone_number = models.CharField(max_length=32, blank=True)
    device_id = models.CharField(max_length=256, blank=True, db_index=True)
    is_guest = models.BooleanField(default=False)
    role = models.CharField(
        max_length=16,
        choices=UserRole.choices,
        default=UserRole.USER,
    )
    contents = models.JSONField(
        default=list,
        blank=True,
        help_text="Contents Type: [{key, id}] - content refs e.g. avatar, theme",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.username}"
