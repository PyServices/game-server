from rest_framework import serializers
from apps.social.models import Friendship
from apps.users.services import UserService


class FriendshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friendship
        fields = ["id", "user_id", "friend_id", "status", "created_at", "updated_at"]
        read_only_fields = fields


class FriendListSerializer(serializers.Serializer):
    """Friend with username for list views."""
    id = serializers.IntegerField()
    friend_id = serializers.IntegerField()
    username = serializers.CharField()
