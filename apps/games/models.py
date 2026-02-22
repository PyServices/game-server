from django.db import models


class Mode(models.TextChoices):
    OFFLINE = "offline"
    REAL_TIME = "real-time"
    TURN_BASED = "turn-based"


class Game(models.Model):
    """Game definition. Optional html_layout (e.g. from _example/game-layout.html) loads at game page."""

    name = models.CharField(max_length=128)
    slug = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="games/images/", blank=True, null=True)
    html_layout = models.FileField(upload_to="games/layouts/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class Scene(models.Model):
    """3D Scene: Babylon JS scene script (*.js), GLB zip, HTML layout, preview image."""

    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    slug = models.CharField(max_length=64)
    game = models.ForeignKey(
        Game, on_delete=models.CASCADE, related_name="scenes", default=None
    )
    image = models.ImageField(upload_to="3d/scenes/images/", blank=True, null=True)

    mode = models.CharField(
        max_length=20,
        choices=Mode.choices,
        default=Mode.OFFLINE,
    )

    infinite = models.BooleanField(default=False)
    min_players = models.IntegerField(default=1, null=True, blank=True)
    max_players = models.IntegerField(default=4, null=True, blank=True)

    team_mode = models.BooleanField(default=False)
    team_count = models.IntegerField(default=2, null=True, blank=True)
    team_size = models.IntegerField(default=2, null=True, blank=True)

    watchable = models.BooleanField(default=True)

    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["game", "slug"], name="unique_scene_slug_per_game"),
        ]

    def __str__(self):
        return f"{self.game.name} - {self.name}"


class Match(models.Model):
    """Active or finished match. Created by matchmaking."""

    class Status(models.TextChoices):
        WAITING = "waiting"
        IN_PROGRESS = "in_progress"
        FINISHED = "finished"

    game_slug = models.CharField(max_length=64)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.WAITING
    )
    channel_name = models.CharField(max_length=128, unique=True)  # Channel group name
    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.game_slug} ({self.channel_name})"


class MatchPlayer(models.Model):
    """Player or spectator in a match."""

    class Role(models.TextChoices):
        PLAYER = "player"
        SPECTATOR = "spectator"

    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="players")
    user_id = models.IntegerField(null=True, blank=True)  # FK to User when auth added
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.PLAYER)
    session_id = models.CharField(max_length=64)  # WebSocket channel name
    name = models.CharField(max_length=64, default="")
    score = models.IntegerField(default=0)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [["match", "session_id"]]
    def __str__(self):
        return self.name