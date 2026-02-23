"""
Resource per .cursor/docs/core/resource.md

Types: Currency, Meta, Asset, Data, Other
- Currency: IsConsumable=True (fixed), has default_amount
- Owner Resource: FK to Resource of type Asset only
- stable_value: for exchange between resources
- config: type-specific (JSON)
- data: JSON, only for type=Data, shown when user obtains resource
"""
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class ResourceType(models.TextChoices):
    CURRENCY = "currency"
    META = "meta"
    ASSET = "asset"
    DATA = "data"
    OTHER = "other"


class Resource(models.Model):
    """Resource: Currency, Meta, Asset, Data, Other."""

    name = models.CharField(max_length=128, unique=True)
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    category = models.ForeignKey(
        "groups.Category",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resources",
    )
    tags = models.ManyToManyField(
        "groups.Tag",
        related_name="resources",
        blank=True,
    )
    is_consumable = models.BooleanField(default=False)
    type = models.CharField(
        max_length=32,
        choices=ResourceType.choices,
        default=ResourceType.OTHER,
    )
    owner_resource = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owned_resources",
        limit_choices_to={"type": ResourceType.ASSET},
    )
    contents = models.JSONField(default=dict, blank=True)
    stable_value = models.FloatField(default=1.0, help_text="Value for exchange between resources")
    config = models.JSONField(default=dict, blank=True, help_text="Type-specific config")
    default_amount = models.FloatField(
        default=0,
        null=True,
        blank=True,
        help_text="Initial amount for consumables (e.g. XP=0, Money=500)",
    )
    data = models.JSONField(
        default=None,
        null=True,
        blank=True,
        help_text="Only for type=Data; shown when user obtains resource",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def clean(self):
        if self.type == ResourceType.CURRENCY:
            self.is_consumable = True
        if self.owner_resource_id and self.owner_resource:
            if self.owner_resource.type != ResourceType.ASSET:
                raise ValidationError({"owner_resource": "Owner Resource must be of type Asset."})

    def save(self, *args, **kwargs):
        if self.type == ResourceType.CURRENCY:
            self.is_consumable = True
        super().save(*args, **kwargs)


class UserResource(models.Model):
    """User's resource instance. value is JSON per type: Currency/Meta {value}, Asset {childs}, Data {value, valueType}."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_resources",
    )
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        related_name="user_resources",
    )
    owner_user_resource = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="child_resources",
    )
    value = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "resource"],
                condition=models.Q(owner_user_resource__isnull=True),
                name="unique_user_resource_top",
            ),
            models.UniqueConstraint(
                fields=["user", "resource", "owner_user_resource"],
                condition=models.Q(owner_user_resource__isnull=False),
                name="unique_user_resource_child",
            ),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user_id}:{self.resource.name}"
