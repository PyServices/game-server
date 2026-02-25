# Consolidated initial migration - UserProfile

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("born", models.DateField(blank=True, null=True)),
                ("meta_data", models.JSONField(blank=True, default=dict)),
                ("phone_number", models.CharField(blank=True, max_length=32)),
                ("device_id", models.CharField(blank=True, db_index=True, max_length=256)),
                ("is_guest", models.BooleanField(default=False)),
                (
                    "role",
                    models.CharField(
                        choices=[("user", "User"), ("admin", "Admin")],
                        default="user",
                        max_length=16,
                    ),
                ),
                (
                    "contents",
                    models.JSONField(
                        blank=True,
                        default=list,
                        help_text="Contents Type: [{key, id}] - content refs e.g. avatar, theme",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
