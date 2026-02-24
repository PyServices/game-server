"""Friend service - public API for friends module."""
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
        """Send friend request. Allows re-send if previously declined."""
        if user_id == friend_id:
            raise ValueError("Cannot friend yourself")
        fs, created = Friendship.objects.get_or_create(
            user_id=min(user_id, friend_id),
            friend_id=max(user_id, friend_id),
            defaults={"status": Friendship.Status.PENDING},
        )
        if not created:
            if fs.status == Friendship.Status.DECLINED:
                fs.status = Friendship.Status.PENDING
                fs.save(update_fields=["status", "updated_at"])
            elif fs.status != Friendship.Status.PENDING:
                raise ValueError("Already friends or blocked")
        return fs

    @staticmethod
    def accept_request(friendship_id: int, user_id: int) -> Friendship:
        """Accept a friend request."""
        fs = get_object_or_404(Friendship, pk=friendship_id)
        if fs.friend_id != user_id and fs.user_id != user_id:
            raise ValueError("Not your request")
        fs.status = Friendship.Status.ACCEPTED
        fs.save(update_fields=["status", "updated_at"])
        return fs

    @staticmethod
    def decline_request(friendship_id: int, user_id: int) -> bool:
        """Decline a friend request (recipient only). Sets status to declined."""
        fs = get_object_or_404(Friendship, pk=friendship_id)
        if fs.friend_id != user_id and fs.user_id != user_id:
            raise ValueError("Not your request")
        if fs.status != Friendship.Status.PENDING:
            raise ValueError("Request already accepted or declined")
        fs.status = Friendship.Status.DECLINED
        fs.save(update_fields=["status", "updated_at"])
        return True

    @staticmethod
    def remove_friend(user_id: int, friend_id: int) -> bool:
        """Remove friendship."""
        deleted, _ = Friendship.objects.filter(
            user_id=min(user_id, friend_id),
            friend_id=max(user_id, friend_id),
        ).delete()
        return deleted > 0

    @staticmethod
    def list_incoming_requests(user_id: int):
        """List pending friend requests where user is the recipient (friend_id)."""
        return Friendship.objects.filter(
            friend_id=user_id, status=Friendship.Status.PENDING
        ).order_by("-created_at")

    @staticmethod
    def list_pending_user_ids(user_id: int):
        """Get user_ids we have any pending relationship with (sent or received)."""
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
        return sent | received
