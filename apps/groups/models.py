"""
Tag and Category per .cursor/docs/core/groups/tag.md and category.md

Both have: id, name, description?, label?, metadata?, contents (Contents Type)
"""
from django.db import models


class Tag(models.Model):
    """Tag for grouping and filtering."""

    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    label = models.CharField(max_length=64, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    contents = models.JSONField(default=dict, blank=True)  # Contents Type: {contents: [{key, id}]}
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class Category(models.Model):
    """Category for grouping and filtering."""

    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    label = models.CharField(max_length=64, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    contents = models.JSONField(default=dict, blank=True)  # Contents Type
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
