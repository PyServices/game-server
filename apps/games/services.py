"""Game and Scene services - public API for other modules."""
import uuid
from django.shortcuts import get_object_or_404

from .models import Game, Scene, Match, MatchPlayer, MatchInvite


class GameService:
    """Bridge for game entity access. Other modules use this instead of importing Game."""

    @staticmethod
    def get_game_by_slug(slug: str) -> Game:
        return get_object_or_404(Game, slug=slug)

    @staticmethod
    def get_game_by_id(pk: int) -> Game | None:
        try:
            return Game.objects.get(pk=pk)
        except Game.DoesNotExist:
            return None

    @staticmethod
    def list_games():
        return Game.objects.all()


class SceneService:
    """Bridge for scene entity access."""

    @staticmethod
    def get_scenes_for_game_id(game_id: int):
        return Scene.objects.filter(game_id=game_id)

    @staticmethod
    def get_scene_by_game_and_slug(game_id: int, scene_slug: str) -> Scene:
        return get_object_or_404(Scene, game_id=game_id, slug=scene_slug)

    @staticmethod
    def list_scenes():
        return Scene.objects.all()


class MatchService:
    """Lobby/match creation and matchmaking."""

    @staticmethod
    def create_match(
        game_slug: str,
        scene_slug: str = "",
        mode: str = "real-time",
        host_user_id: int | None = None,
        max_players: int = 4,
        host_session_id: str | None = None,
    ) -> Match:
        """Create a new lobby (match). channel_name is unique room id for fast-game."""
        channel = f"{game_slug}|{uuid.uuid4().hex[:12]}"
        match = Match.objects.create(
            game_slug=game_slug,
            scene_slug=scene_slug,
            mode=mode,
            channel_name=channel,
            host_user_id=host_user_id,
            max_players=max_players,
        )
        # Add host as first player
        sid = host_session_id or str(uuid.uuid4())[:12]
        MatchPlayer.objects.create(
            match=match,
            user_id=host_user_id,
            session_id=sid,
            name="Host",
            role=MatchPlayer.Role.PLAYER,
        )
        return match

    @staticmethod
    def get_match_by_id(pk: int) -> Match | None:
        try:
            return Match.objects.get(pk=pk)
        except Match.DoesNotExist:
            return None

    @staticmethod
    def get_match_by_channel(channel_name: str) -> Match | None:
        try:
            return Match.objects.get(channel_name=channel_name)
        except Match.DoesNotExist:
            return None

    @staticmethod
    def list_matches_for_game(game_slug: str, status: str | None = None):
        qs = Match.objects.filter(game_slug=game_slug)
        if status:
            qs = qs.filter(status=status)
        return qs.order_by("-created_at")

    @staticmethod
    def add_player(
        match_id: int,
        session_id: str,
        user_id: int | None = None,
        name: str = "Player",
        role: str = "player",
    ) -> MatchPlayer | None:
        match = MatchService.get_match_by_id(match_id)
        if not match or match.status != Match.Status.WAITING:
            return None
        players = match.players.count()
        if players >= match.max_players:
            return None
        mp, _ = MatchPlayer.objects.get_or_create(
            match_id=match_id,
            session_id=session_id,
            defaults={"user_id": user_id, "name": name, "role": role},
        )
        return mp

    @staticmethod
    def remove_player(match_id: int, session_id: str) -> bool:
        deleted, _ = MatchPlayer.objects.filter(
            match_id=match_id, session_id=session_id
        ).delete()
        return deleted > 0

    @staticmethod
    def start_match(match_id: int) -> bool:
        match = MatchService.get_match_by_id(match_id)
        if not match or match.status != Match.Status.WAITING:
            return False
        match.status = Match.Status.IN_PROGRESS
        match.save(update_fields=["status"])
        return True

    @staticmethod
    def invite_to_match(match_id: int, inviter_id: int, friend_id: int) -> MatchInvite | None:
        """Invite a friend to the lobby."""
        match = MatchService.get_match_by_id(match_id)
        if not match or match.status != Match.Status.WAITING:
            return None
        if match.players.count() >= match.max_players:
            return None
        if match.players.filter(user_id=friend_id).exists():
            return None  # Already in lobby
        inv, _ = MatchInvite.objects.get_or_create(
            match_id=match_id,
            invitee_id=friend_id,
            defaults={"inviter_id": inviter_id, "status": MatchInvite.Status.PENDING},
        )
        return inv

    @staticmethod
    def list_lobby_invites_for_user(user_id: int):
        """List pending lobby invites for a user (invitee)."""
        from apps.users.services import UserService
        invites = MatchInvite.objects.filter(
            invitee_id=user_id, status=MatchInvite.Status.PENDING
        ).select_related("match").order_by("-created_at")
        result = []
        for inv in invites:
            match = inv.match
            inviter = UserService.get_user(inv.inviter_id)
            result.append({
                "id": inv.id,
                "match_id": match.id,
                "game_slug": match.game_slug,
                "inviter_id": inv.inviter_id,
                "inviter_username": inviter.username if inviter else f"user_{inv.inviter_id}",
                "scene_slug": match.scene_slug,
                "mode": match.mode,
                "created_at": inv.created_at.isoformat() if inv.created_at else None,
            })
        return result

    @staticmethod
    def accept_lobby_invite(
        match_id: int, invitee_id: int, session_id: str, name: str = "Player"
    ) -> MatchPlayer | None:
        """Accept lobby invite: add invitee to match, mark invite accepted."""
        inv = MatchInvite.objects.filter(
            match_id=match_id, invitee_id=invitee_id, status=MatchInvite.Status.PENDING
        ).first()
        if not inv:
            return None
        mp = MatchService.add_player(
            match_id=match_id,
            session_id=session_id,
            user_id=invitee_id,
            name=name,
        )
        if mp:
            inv.status = MatchInvite.Status.ACCEPTED
            inv.save(update_fields=["status"])
        return mp

    @staticmethod
    def decline_lobby_invite(match_id: int, invitee_id: int) -> bool:
        """Decline lobby invite: mark invite as declined."""
        updated = MatchInvite.objects.filter(
            match_id=match_id, invitee_id=invitee_id, status=MatchInvite.Status.PENDING
        ).update(status=MatchInvite.Status.DECLINED)
        return updated > 0
