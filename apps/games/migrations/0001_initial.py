# Consolidated initial migration - Game, Scene, Match, MatchPlayer, MatchInvite

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Game",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=128)),
                ("slug", models.CharField(max_length=64, unique=True)),
                ("description", models.TextField(blank=True)),
                ("image", models.ImageField(blank=True, null=True, upload_to="games/images/")),
                ("html_layout", models.FileField(blank=True, null=True, upload_to="games/layouts/")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="Scene",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=128)),
                ("description", models.TextField(blank=True)),
                ("slug", models.CharField(max_length=64)),
                ("image", models.ImageField(blank=True, null=True, upload_to="3d/scenes/images/")),
                (
                    "mode",
                    models.CharField(
                        choices=[
                            ("offline", "Offline"),
                            ("real-time", "Real Time"),
                            ("turn-based", "Turn Based"),
                        ],
                        default="offline",
                        max_length=20,
                    ),
                ),
                ("infinite", models.BooleanField(default=False)),
                ("min_players", models.IntegerField(blank=True, default=1, null=True)),
                ("max_players", models.IntegerField(blank=True, default=4, null=True)),
                ("team_mode", models.BooleanField(default=False)),
                ("team_count", models.IntegerField(blank=True, default=2, null=True)),
                ("team_size", models.IntegerField(blank=True, default=2, null=True)),
                ("watchable", models.BooleanField(default=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "game",
                    models.ForeignKey(
                        default=None,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="scenes",
                        to="games.game",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddConstraint(
            model_name="scene",
            constraint=models.UniqueConstraint(fields=("game", "slug"), name="unique_scene_slug_per_game"),
        ),
        migrations.CreateModel(
            name="Match",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("game_slug", models.CharField(max_length=64)),
                ("scene_slug", models.CharField(blank=True, max_length=64)),
                (
                    "mode",
                    models.CharField(
                        choices=[
                            ("offline", "Offline"),
                            ("real-time", "Real Time"),
                            ("turn-based", "Turn Based"),
                        ],
                        default="real-time",
                        max_length=20,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("waiting", "Waiting"),
                            ("in_progress", "In Progress"),
                            ("finished", "Finished"),
                        ],
                        default="waiting",
                        max_length=20,
                    ),
                ),
                ("channel_name", models.CharField(max_length=128, unique=True)),
                ("host_user_id", models.IntegerField(blank=True, null=True)),
                ("max_players", models.IntegerField(default=4)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("finished_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="MatchPlayer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("user_id", models.IntegerField(blank=True, null=True)),
                (
                    "role",
                    models.CharField(
                        choices=[("player", "Player"), ("spectator", "Spectator")],
                        default="player",
                        max_length=20,
                    ),
                ),
                ("session_id", models.CharField(max_length=64)),
                ("name", models.CharField(default="", max_length=64)),
                ("score", models.IntegerField(default=0)),
                ("joined_at", models.DateTimeField(auto_now_add=True)),
                (
                    "match",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="players",
                        to="games.match",
                    ),
                ),
            ],
            options={"unique_together": {("match", "session_id")}},
        ),
        migrations.CreateModel(
            name="MatchInvite",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("invitee_id", models.IntegerField()),
                ("inviter_id", models.IntegerField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("accepted", "Accepted"),
                            ("declined", "Declined"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "match",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="invites",
                        to="games.match",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "unique_together": {("match", "invitee_id")},
            },
        ),
    ]
