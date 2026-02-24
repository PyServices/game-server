from django.db import models


class ChatRoom(models.Model):
    """Chat room - DM, lobby, game, or ally. League-style chat system."""

    class RoomType(models.TextChoices):
        DM = "dm"  # 2 users
        LOBBY = "lobby"  # Lobby members
        GAME = "game"  # All clients in a game
        ALLY = "ally"  # Ally team members in a game

    room_type = models.CharField(max_length=20, choices=RoomType.choices)
    name = models.CharField(max_length=128, blank=True)  # Display name for group chats
    # For DM: null. For lobby: match_id. For game: match_id. For ally: match_id + team_id
    match_id = models.IntegerField(null=True, blank=True)
    team_id = models.CharField(max_length=64, blank=True)  # For ally only
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["room_type"]),
            models.Index(fields=["match_id"]),
        ]

    def __str__(self):
        return f"{self.room_type} {self.name or self.id}"


class ChatRoomMember(models.Model):
    """User membership in a chat room."""

    room = models.ForeignKey(
        ChatRoom, on_delete=models.CASCADE, related_name="members"
    )
    user_id = models.IntegerField()
    last_read_at = models.DateTimeField(null=True, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [["room", "user_id"]]
        indexes = [models.Index(fields=["user_id"])]

    def __str__(self):
        from apps.users.services import UserService
        u = UserService.get_user(self.user_id)
        name = u.username if u else f"#{self.user_id}"
        return f"Room {self.room_id} {name}"


class ChatMessage(models.Model):
    """Message in a chat room."""

    room = models.ForeignKey(
        ChatRoom, on_delete=models.CASCADE, related_name="messages"
    )
    user_id = models.IntegerField()
    content = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["room"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        from apps.users.services import UserService
        u = UserService.get_user(self.user_id)
        name = u.username if u else f"#{self.user_id}"
        return f"Room {self.room_id} by {name}: {self.content[:30]}..."
