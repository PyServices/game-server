"""
Language per .cursor/docs/core/event/language.md

id, name, description?, contents (Contents Type)
"""
from django.db import models


class Language(models.Model):
    """Language for i18n."""

    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    contents = models.JSONField(default=dict, blank=True)  # Contents Type
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
