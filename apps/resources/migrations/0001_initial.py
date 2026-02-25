# Consolidated initial migration - Resource, UserResource

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("groups", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Resource",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=128, unique=True)),
                ("description", models.TextField(blank=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("is_consumable", models.BooleanField(default=False)),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("currency", "Currency"),
                            ("meta", "Meta"),
                            ("asset", "Asset"),
                            ("data", "Data"),
                            ("other", "Other"),
                        ],
                        default="other",
                        max_length=32,
                    ),
                ),
                ("contents", models.JSONField(blank=True, default=dict)),
                (
                    "stable_value",
                    models.FloatField(default=1.0, help_text="Value for exchange between resources"),
                ),
                ("config", models.JSONField(blank=True, default=dict, help_text="Type-specific config")),
                (
                    "default_amount",
                    models.FloatField(
                        blank=True,
                        default=0,
                        help_text="Initial amount for consumables (e.g. XP=0, Money=500)",
                        null=True,
                    ),
                ),
                (
                    "data",
                    models.JSONField(
                        blank=True,
                        default=None,
                        help_text="Only for type=Data; shown when user obtains resource",
                        null=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "category",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="resources",
                        to="groups.category",
                    ),
                ),
                (
                    "owner_resource",
                    models.ForeignKey(
                        blank=True,
                        limit_choices_to={"type": "asset"},
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="owned_resources",
                        to="resources.resource",
                    ),
                ),
                (
                    "tags",
                    models.ManyToManyField(blank=True, related_name="resources", to="groups.tag"),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="UserResource",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("value", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "owner_user_resource",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="child_resources",
                        to="resources.userresource",
                    ),
                ),
                (
                    "resource",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_resources",
                        to="resources.resource",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_resources",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "constraints": [
                    models.UniqueConstraint(
                        condition=models.Q(("owner_user_resource__isnull", True)),
                        fields=("user", "resource"),
                        name="unique_user_resource_top",
                    ),
                    models.UniqueConstraint(
                        condition=models.Q(("owner_user_resource__isnull", False)),
                        fields=("user", "resource", "owner_user_resource"),
                        name="unique_user_resource_child",
                    ),
                ],
            },
        ),
    ]
