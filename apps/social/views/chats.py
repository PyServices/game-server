"""Chat API - uses ChatService."""
from rest_framework import viewsets, status

from apps.social.models import ChatRoom, ChatMessage
from apps.social.serializers import ChatRoomSerializer, ChatMessageSerializer
from apps.social.services import ChatService
from apps.commons.mixins import StandardResponseMixin
from apps.commons.response import api_response


class ChatRoomViewSet(StandardResponseMixin, viewsets.ReadOnlyModelViewSet):
    """List chat rooms, create DM, get room."""
    serializer_class = ChatRoomSerializer

    def get_queryset(self):
        user = getattr(self.request, "user", None)
        if not user or not hasattr(user, "id"):
            return ChatRoom.objects.none()
        return ChatService.list_rooms_for_user(user.id)

    def create(self, request):
        """Create or get DM with another user."""
        user = getattr(request, "user", None)
        if not user or not hasattr(user, "id"):
            return api_response("UNAUTHORIZED", status=401)
        other_id = request.data.get("user_id")
        if not other_id:
            return api_response("INVALID_INPUT", meta={"message": "user_id required"}, status=400)
        try:
            room = ChatService.get_or_create_dm(user.id, int(other_id))
            return self._success(
                ChatRoomSerializer(room, context={"request": request}).data,
                status=status.HTTP_201_CREATED,
            )
        except ValueError as e:
            return api_response("INVALID_INPUT", meta={"message": str(e)}, status=400)

    def retrieve(self, request, *args, **kwargs):
        """Get room with messages."""
        room = self.get_object()
        user = getattr(request, "user", None)
        if user and hasattr(user, "id"):
            ChatService.mark_read(room.id, user.id)
        return self._success(ChatRoomSerializer(room, context={"request": request}).data)


class ChatMessageViewSet(StandardResponseMixin, viewsets.ReadOnlyModelViewSet):
    """List messages in a room, send message."""
    serializer_class = ChatMessageSerializer

    def get_queryset(self):
        room_id = self.kwargs.get("room_id")
        if not room_id:
            return ChatMessage.objects.none()
        return ChatMessage.objects.filter(room_id=room_id).order_by("created_at")

    def create(self, request, *args, **kwargs):
        """Send message to room."""
        room_id = kwargs.get("room_id")
        if not room_id:
            return api_response("INVALID_INPUT", meta={"message": "room_id required"}, status=400)
        user = getattr(request, "user", None)
        if not user or not hasattr(user, "id"):
            return api_response("UNAUTHORIZED", status=401)
        content = request.data.get("content", "").strip()
        if not content:
            return api_response("INVALID_INPUT", meta={"message": "content required"}, status=400)
        msg = ChatService.send_message(int(room_id), user.id, content)
        return self._success(ChatMessageSerializer(msg).data, status=status.HTTP_201_CREATED)
