"""Games and Scenes API - REST only. Uses GameService/SceneService (no direct model access)."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .services import GameService, SceneService, MatchService
from .serializers import GameSerializer, SceneSerializer, MatchSerializer
from .models import Match
from apps.commons.mixins import StandardResponseMixin
from apps.commons.response import ResponseCode, api_response


class GameViewSet(StandardResponseMixin, viewsets.ModelViewSet):
    """List and retrieve games."""
    serializer_class = GameSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return GameService.list_games()


class SceneViewSet(StandardResponseMixin, viewsets.ModelViewSet):
    """List and retrieve 3D scenes."""
    serializer_class = SceneSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return SceneService.list_scenes()


class MatchViewSet(StandardResponseMixin, viewsets.ReadOnlyModelViewSet):
    """Lobby/match CRUD and matchmaking actions."""
    serializer_class = MatchSerializer
    lookup_url_kwarg = "id"

    def get_queryset(self):
        game_slug = self.kwargs.get("game_slug")
        if game_slug:
            return MatchService.list_matches_for_game(game_slug)
        return Match.objects.none()

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["game_slug"] = self.kwargs.get("game_slug")
        return ctx

    def create(self, request, *args, **kwargs):
        """Create a new lobby."""
        game_slug = self.kwargs.get("game_slug")
        scene_slug = request.data.get("scene_slug", "")
        mode = request.data.get("mode", "real-time")
        max_players = int(request.data.get("max_players", 4))
        session_id = request.data.get("session_id", "")
        user = getattr(request, "user", None)
        user_id = user.id if user and hasattr(user, "id") else None
        host_name = user.username if user and hasattr(user, "username") else "Host"
        match = MatchService.create_match(
            game_slug=game_slug,
            scene_slug=scene_slug,
            mode=mode,
            host_user_id=user_id,
            max_players=max_players,
            host_session_id=session_id or None,
        )
        # Update host player name
        mp = match.players.first()
        if mp:
            mp.name = host_name
            mp.save(update_fields=["name"])
        return self._success(MatchSerializer(match).data, status=status.HTTP_201_CREATED)

    def join(self, request, game_slug=None, id=None):
        """Join a lobby."""
        mid = id or self.kwargs.get("id")
        session_id = request.data.get("session_id", "")
        name = request.data.get("name", "Player")
        user = getattr(request, "user", None)
        user_id = user.id if user and hasattr(user, "id") else None
        if not session_id:
            return api_response("INVALID_INPUT", meta={"message": "session_id required"}, status=400)
        mp = MatchService.add_player(
            match_id=int(mid),
            session_id=session_id,
            user_id=user_id,
            name=name,
        )
        if not mp:
            return api_response("LOBBY_FULL", meta={"message": "Lobby is full or not waiting"}, status=400)
        match = MatchService.get_match_by_id(int(mid))
        return self._success(MatchSerializer(match).data)

    def leave(self, request, game_slug=None, id=None):
        """Leave a lobby."""
        mid = id or self.kwargs.get("id")
        session_id = request.data.get("session_id", "")
        if not session_id:
            return api_response("INVALID_INPUT", meta={"message": "session_id required"}, status=400)
        MatchService.remove_player(match_id=int(mid), session_id=session_id)
        return self._success(None)

    def start(self, request, game_slug=None, id=None):
        """Start the match (host only)."""
        mid = id or self.kwargs.get("id")
        if not MatchService.start_match(int(mid)):
            return api_response("CANNOT_START", meta={"message": "Match not in waiting state"}, status=400)
        match = MatchService.get_match_by_id(int(mid))
        return self._success(MatchSerializer(match).data)

    def invite(self, request, game_slug=None, id=None):
        """Invite a friend to the lobby."""
        mid = id or self.kwargs.get("id")
        user = getattr(request, "user", None)
        if not user or not hasattr(user, "id"):
            return api_response("UNAUTHORIZED", status=401)
        friend_id = request.data.get("friend_id")
        if not friend_id:
            return api_response("INVALID_INPUT", meta={"message": "friend_id required"}, status=400)
        inv = MatchService.invite_to_match(int(mid), user.id, int(friend_id))
        if not inv:
            return api_response("INVALID_INPUT", meta={"message": "Cannot invite (lobby full or already in)"}, status=400)
        match = MatchService.get_match_by_id(int(mid))
        return self._success(MatchSerializer(match).data)

    def accept_invite(self, request, game_slug=None, id=None):
        """Accept lobby invite (for invitee B): join the match."""
        mid = id or self.kwargs.get("id")
        user = getattr(request, "user", None)
        if not user or not hasattr(user, "id"):
            return api_response("UNAUTHORIZED", status=401)
        session_id = request.data.get("session_id", "")
        name = request.data.get("name", user.username or "Player")
        if not session_id:
            return api_response("INVALID_INPUT", meta={"message": "session_id required"}, status=400)
        mp = MatchService.accept_lobby_invite(
            match_id=int(mid),
            invitee_id=user.id,
            session_id=session_id,
            name=name,
        )
        if not mp:
            return api_response("INVALID_INPUT", meta={"message": "No pending invite or lobby full"}, status=400)
        match = MatchService.get_match_by_id(int(mid))
        return self._success(MatchSerializer(match).data)

    def decline_invite(self, request, game_slug=None, id=None):
        """Decline lobby invite (for invitee B)."""
        mid = id or self.kwargs.get("id")
        user = getattr(request, "user", None)
        if not user or not hasattr(user, "id"):
            return api_response("UNAUTHORIZED", status=401)
        ok = MatchService.decline_lobby_invite(match_id=int(mid), invitee_id=user.id)
        if not ok:
            return api_response("INVALID_INPUT", meta={"message": "No pending invite"}, status=400)
        return self._success(None)
