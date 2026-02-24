"""Friends API - uses FriendService."""
from rest_framework import viewsets, status
from rest_framework.decorators import action

from apps.social.models import Friendship
from apps.social.serializers import FriendshipSerializer
from apps.social.services import FriendService
from apps.users.services import UserService
from apps.commons.mixins import StandardResponseMixin
from apps.commons.response import api_response


class FriendsViewSet(StandardResponseMixin, viewsets.ReadOnlyModelViewSet):
    """List friends, send/accept requests, remove."""
    serializer_class = FriendshipSerializer

    def get_queryset(self):
        user = getattr(self.request, "user", None)
        if not user or not hasattr(user, "id"):
            return Friendship.objects.none()
        return FriendService.list_friends(user.id)

    def list(self, request, *args, **kwargs):
        """List friends with username. Use FriendListSerializer for richer data."""
        user = getattr(request, "user", None)
        if not user or not hasattr(user, "id"):
            return api_response("UNAUTHORIZED", status=401)
        friendships = FriendService.list_friends(user.id)
        data = []
        for fs in friendships:
            other_id = fs.friend_id if fs.user_id == user.id else fs.user_id
            other = UserService.get_user(other_id)
            data.append({
                "id": fs.id,
                "friend_id": other_id,
                "username": other.username if other else f"user_{other_id}",
            })
        return self._success(data)

    def create(self, request):
        """Send friend request."""
        user = getattr(request, "user", None)
        if not user or not hasattr(user, "id"):
            return api_response("UNAUTHORIZED", status=401)
        friend_id = request.data.get("friend_id")
        if not friend_id:
            return api_response("INVALID_INPUT", meta={"message": "friend_id required"}, status=400)
        try:
            fs = FriendService.send_request(user.id, int(friend_id))
            return self._success(FriendshipSerializer(fs).data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return api_response("INVALID_INPUT", meta={"message": str(e)}, status=400)

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        """Accept friend request (pk = friendship id)."""
        user = getattr(request, "user", None)
        if not user or not hasattr(user, "id"):
            return api_response("UNAUTHORIZED", status=401)
        try:
            fs = FriendService.accept_request(int(pk), user.id)
            return self._success(FriendshipSerializer(fs).data)
        except ValueError as e:
            return api_response("INVALID_INPUT", meta={"message": str(e)}, status=400)

    @action(detail=True, methods=["post"])
    def decline(self, request, pk=None):
        """Decline friend request (pk = friendship id)."""
        user = getattr(request, "user", None)
        if not user or not hasattr(user, "id"):
            return api_response("UNAUTHORIZED", status=401)
        try:
            FriendService.decline_request(int(pk), user.id)
            return self._success(None)
        except ValueError as e:
            return api_response("INVALID_INPUT", meta={"message": str(e)}, status=400)

    @action(detail=False, methods=["get"], url_path="requests")
    def list_requests(self, request):
        """List incoming friend requests (pending)."""
        user = getattr(request, "user", None)
        if not user or not hasattr(user, "id"):
            return api_response("UNAUTHORIZED", status=401)
        requests_qs = FriendService.list_incoming_requests(user.id)
        data = []
        for fs in requests_qs:
            other = UserService.get_user(fs.user_id)
            data.append({
                "id": fs.id,
                "user_id": fs.user_id,
                "username": other.username if other else f"user_{fs.user_id}",
                "status": fs.status,
                "created_at": fs.created_at.isoformat() if fs.created_at else None,
            })
        return self._success(data)

    @action(detail=False, methods=["get"], url_path="pending-ids")
    def list_pending_ids(self, request):
        """List user_ids we've sent pending requests to (for UI to hide Add button)."""
        user = getattr(request, "user", None)
        if not user or not hasattr(user, "id"):
            return api_response("UNAUTHORIZED", status=401)
        ids = list(FriendService.list_pending_user_ids(user.id))
        return self._success(ids)

    @action(detail=False, methods=["post"], url_path="remove")
    def remove_friend(self, request):
        """Remove friend. Body: { friend_id: int }."""
        user = getattr(request, "user", None)
        if not user or not hasattr(user, "id"):
            return api_response("UNAUTHORIZED", status=401)
        friend_id = request.data.get("friend_id")
        if not friend_id:
            return api_response("INVALID_INPUT", meta={"message": "friend_id required"}, status=400)
        FriendService.remove_friend(user.id, int(friend_id))
        return self._success(None)
