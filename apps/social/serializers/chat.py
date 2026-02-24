from rest_framework import serializers
from apps.social.models import ChatRoom, ChatMessage, ChatRoomMember
from apps.users.services import UserService


class ChatMessageSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = ["id", "room_id", "user_id", "username", "content", "metadata", "created_at"]
        read_only_fields = fields

    def get_username(self, obj):
        user = UserService.get_user(obj.user_id)
        return user.username if user else f"user_{obj.user_id}"


class ChatRoomMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoomMember
        fields = ["id", "user_id", "last_read_at", "joined_at"]


class ChatRoomSerializer(serializers.ModelSerializer):
    members = ChatRoomMemberSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = [
            "id",
            "room_type",
            "name",
            "match_id",
            "team_id",
            "metadata",
            "members",
            "last_message",
            "unread_count",
            "created_at",
            "updated_at",
        ]

    def get_last_message(self, obj):
        msg = obj.messages.order_by("-created_at").first()
        if msg:
            return ChatMessageSerializer(msg).data
        return None

    def get_unread_count(self, obj):
        request = self.context.get("request")
        if not request:
            return 0
        user = getattr(request, "user", None)
        if not user or not hasattr(user, "id"):
            return 0
        user_id = user.id
        if not user_id:
            return 0
        try:
            member = obj.members.get(user_id=user_id)
            if not member.last_read_at:
                return obj.messages.count()
            return obj.messages.filter(created_at__gt=member.last_read_at).count()
        except ChatRoomMember.DoesNotExist:
            return 0
