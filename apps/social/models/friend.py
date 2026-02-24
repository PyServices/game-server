from django.db import models


class Friendship(models.Model):
    """Friendship between two users. League-style: see status, watch games, invite to lobby."""

    class Status(models.TextChoices):
        PENDING = "pending"
        ACCEPTED = "accepted"
        DECLINED = "declined"
        BLOCKED = "blocked"

    user_id = models.IntegerField()  # FK to User
    friend_id = models.IntegerField()  # FK to User
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = [["user_id", "friend_id"]]
        indexes = [
            models.Index(fields=["user_id"]),
            models.Index(fields=["friend_id"]),
        ]

    def __str__(self):
        from apps.users.services import UserService
        u1 = UserService.get_user(self.user_id)
        u2 = UserService.get_user(self.friend_id)
        n1 = u1.username if u1 else f"#{self.user_id}"
        n2 = u2.username if u2 else f"#{self.friend_id}"
        return f"{n1} <-> {n2} ({self.status})"
