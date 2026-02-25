"""Friend service - public API for friends module."""
from django.db.models import Q
from django.shortcuts import get_object_or_404

from apps.social.models import Friendship


class FriendService:
    @staticmethod
    def list_friends(user_id: int, status: str = "accepted"):
        """List friends for a user."""
        qs1 = Friendship.objects.filter(user_id=user_id, status=status)
        qs2 = Friendship.objects.filter(friend_id=user_id, status=status)
        return (qs1 | qs2).order_by("-updated_at")

    @staticmethod
    def list_friend_ids(user_id: int):
        """Get set of friend user_ids."""
        friends = Friendship.objects.filter(
            user_id=user_id, status=Friendship.Status.ACCEPTED
        ).values_list("friend_id", flat=True)
        reverse = Friendship.objects.filter(
            friend_id=user_id, status=Friendship.Status.ACCEPTED
        ).values_list("user_id", flat=True)
        return set(friends) | set(reverse)

    @staticmethod
    def send_request(user_id: int, friend_id: int) -> Friendship:
        """Send friend request. Stores (sender=user_id, recipient=friend_id). Allows re-send if previously declined."""
        if user_id == friend_id:
            raise ValueError("Cannot friend yourself")
        # Check existing in either direction (we store direction: user_id = sender, friend_id = recipient)
        existing = Friendship.objects.filter(
            Q(user_id=user_id, friend_id=friend_id) | Q(user_id=friend_id, friend_id=user_id)
        ).first()
        if existing:
            if existing.status == Friendship.Status.ACCEPTED:
                raise ValueError("Already friends or blocked")
            if existing.status == Friendship.Status.PENDING:
                if existing.user_id == user_id:
                    return existing  # I already sent
                raise ValueError("They already sent you a request")
            # DECLINED: allow re-send
            if existing.user_id == user_id and existing.friend_id == friend_id:
                existing.status = Friendship.Status.PENDING
                existing.save(update_fields=["status", "updated_at"])
                return existing
            # They had sent, we declined; now we send. Replace with (us, them).
            existing.delete()
        return Friendship.objects.create(
            user_id=user_id, friend_id=friend_id, status=Friendship.Status.PENDING
        )

    @staticmethod
    def accept_request(friendship_id: int, user_id: int) -> Friendship:
        """Accept a friend request (recipient = friend_id only)."""
        fs = get_object_or_404(Friendship, pk=friendship_id)
        if fs.friend_id != user_id:
            raise ValueError("Not your request")
        fs.status = Friendship.Status.ACCEPTED
        fs.save(update_fields=["status", "updated_at"])
        return fs

    @staticmethod
    def decline_request(friendship_id: int, user_id: int) -> bool:
        """Decline a friend request (recipient = friend_id only). Sets status to declined."""
        fs = get_object_or_404(Friendship, pk=friendship_id)
        if fs.friend_id != user_id:
            raise ValueError("Not your request")
        if fs.status != Friendship.Status.PENDING:
            raise ValueError("Request already accepted or declined")
        fs.status = Friendship.Status.DECLINED
        fs.save(update_fields=["status", "updated_at"])
        return True

    @staticmethod
    def remove_friend(user_id: int, friend_id: int) -> bool:
        """Remove friendship (row may be stored as (A,B) or (B,A))."""
        deleted, _ = Friendship.objects.filter(
            Q(user_id=user_id, friend_id=friend_id) | Q(user_id=friend_id, friend_id=user_id)
        ).delete()
        return deleted > 0

    @staticmethod
    def list_incoming_requests(user_id: int):
        """List pending friend requests where user is the recipient (friend_id); sender is user_id."""
        return Friendship.objects.filter(
            friend_id=user_id, status=Friendship.Status.PENDING
        ).order_by("-created_at")

    @staticmethod
    def list_pending_user_ids(user_id: int):
        """User_ids we've sent pending requests to, or who've sent us one (for UI to hide Add)."""
        sent = set(
            Friendship.objects.filter(
                user_id=user_id, status=Friendship.Status.PENDING
            ).values_list("friend_id", flat=True)
        )
        received = set(
            Friendship.objects.filter(
                friend_id=user_id, status=Friendship.Status.PENDING
            ).values_list("user_id", flat=True)
        )
        return list(sent | received)
