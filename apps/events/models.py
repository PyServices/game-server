"""
Event and UserEvent per .cursor/docs/core/event/

Event: id, name, event (unique), category, tags, prize_id?, readonly, value_type
UserEvent: event_id, user_id, request_entity_id?, target_entity_id?, value, meta_data, created_at
"""
from django.db import models
from django.conf import settings


class EventValueType(models.TextChoices):
    NONE = "none"
    STRING = "string"
    BOOL = "bool"
    NUMBER = "number"


class Event(models.Model):
    """Event definition. event string is unique, used by client; id used for server relations."""

    name = models.CharField(max_length=256)
    event = models.CharField(max_length=256, unique=True, db_index=True)
    category = models.ForeignKey(
        "groups.Category",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
    )
    tags = models.ManyToManyField(
        "groups.Tag",
        related_name="events",
        blank=True,
    )
    prize_id = models.IntegerField(null=True, blank=True, help_text="Optional prize reference")
    readonly = models.BooleanField(
        default=False,
        help_text="System-created; admin cannot edit",
    )
    value_type = models.CharField(
        max_length=16,
        choices=EventValueType.choices,
        default=EventValueType.NONE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.event} ({self.name})"


class UserEvent(models.Model):
    """User event record. value stored as JSON to support none|number|string|bool."""

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="user_events",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_events",
    )
    request_entity_id = models.CharField(max_length=256, blank=True)
    target_entity_id = models.CharField(max_length=256, blank=True)
    value = models.JSONField(default=None, null=True, blank=True)
    meta_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["event", "user", "created_at"]),
        ]

    def __str__(self):
        return f"{self.event.event} by user {self.user_id}"
