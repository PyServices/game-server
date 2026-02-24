"""Chat service - public API for chat module."""
from django.shortcuts import get_object_or_404
from django.utils import timezone

from apps.social.models import ChatRoom, ChatMessage, ChatRoomMember


class ChatService:
    @staticmethod
    def get_or_create_dm(user_id: int, other_user_id: int) -> ChatRoom:
        """Get or create DM room between two users."""
        if user_id == other_user_id:
            raise ValueError("Cannot DM yourself")
        for room in ChatRoom.objects.filter(room_type=ChatRoom.RoomType.DM):
            uids = room.metadata.get("user_ids", [])
            if set(uids) == {user_id, other_user_id}:
                return room
        room = ChatRoom.objects.create(
            room_type=ChatRoom.RoomType.DM,
            name="",
            metadata={"user_ids": [user_id, other_user_id]},
        )
        ChatRoomMember.objects.bulk_create([
            ChatRoomMember(room=room, user_id=user_id),
            ChatRoomMember(room=room, user_id=other_user_id),
        ])
        return room

    @staticmethod
    def create_lobby_chat(match_id: int, name: str = "") -> ChatRoom:
        """Create chat room for a lobby."""
        room, _ = ChatRoom.objects.get_or_create(
            match_id=match_id,
            room_type=ChatRoom.RoomType.LOBBY,
            defaults={"name": name or f"Lobby {match_id}"},
        )
        return room

    @staticmethod
    def create_game_chat(match_id: int, name: str = "") -> ChatRoom:
        """Create chat room for a game (all players)."""
        room, _ = ChatRoom.objects.get_or_create(
            match_id=match_id,
            room_type=ChatRoom.RoomType.GAME,
            defaults={"name": name or f"Game {match_id}"},
        )
        return room

    @staticmethod
    def create_ally_chat(match_id: int, team_id: str, name: str = "") -> ChatRoom:
        """Create chat room for ally team."""
        room, _ = ChatRoom.objects.get_or_create(
            match_id=match_id,
            team_id=team_id,
            room_type=ChatRoom.RoomType.ALLY,
            defaults={"name": name or f"Team {team_id}"},
        )
        return room

    @staticmethod
    def add_member(room_id: int, user_id: int) -> ChatRoomMember:
        """Add user to room."""
        member, _ = ChatRoomMember.objects.get_or_create(
            room_id=room_id, user_id=user_id
        )
        return member

    @staticmethod
    def send_message(room_id: int, user_id: int, content: str) -> ChatMessage:
        """Send message to room."""
        room = get_object_or_404(ChatRoom, pk=room_id)
        return ChatMessage.objects.create(
            room=room, user_id=user_id, content=content[:4096]
        )

    @staticmethod
    def list_rooms_for_user(user_id: int):
        """List chat rooms the user is in."""
        return ChatRoom.objects.filter(members__user_id=user_id).distinct().order_by("-updated_at")

    @staticmethod
    def mark_read(room_id: int, user_id: int) -> None:
        """Mark room as read for user."""
        ChatRoomMember.objects.filter(
            room_id=room_id, user_id=user_id
        ).update(last_read_at=timezone.now())
