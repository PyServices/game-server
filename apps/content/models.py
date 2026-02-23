"""
Content per .cursor/docs/core/content/

id, name, owner_id, description?, tag_ids[], category_id?, access (private|public),
metadata?, message?, content_url?, type (Text|Image|Video|Sound|File), language_id?, created_at, updated_at
"""
from django.db import models
from django.conf import settings


class ContentAccess(models.TextChoices):
    PRIVATE = "private"
    PUBLIC = "public"


class ContentType(models.TextChoices):
    TEXT = "Text"
    IMAGE = "Image"
    VIDEO = "Video"
    SOUND = "Sound"
    FILE = "File"


class Content(models.Model):
    """Content. Owner can CRUD own; admin can CRUD all."""

    name = models.CharField(max_length=256)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="contents",
    )
    description = models.TextField(blank=True)
    tags = models.ManyToManyField(
        "groups.Tag",
        related_name="content_items",
        blank=True,
    )
    category = models.ForeignKey(
        "groups.Category",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="content_items",
    )
    access = models.CharField(
        max_length=16,
        choices=ContentAccess.choices,
        default=ContentAccess.PRIVATE,
    )
    metadata = models.JSONField(default=dict, blank=True)
    message = models.TextField(blank=True)
    content_url = models.URLField(max_length=512, blank=True)
    type = models.CharField(
        max_length=16,
        choices=ContentType.choices,
        default=ContentType.TEXT,
    )
    language = models.ForeignKey(
        "languages.Language",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="content_items",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
