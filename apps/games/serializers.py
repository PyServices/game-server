from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from .models import Game, Scene, Match, MatchPlayer, MatchInvite


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "image",
            "created_at",
        ]
        read_only_fields = fields


class MatchPlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchPlayer
        fields = ["id", "user_id", "role", "session_id", "name", "score", "joined_at"]
        read_only_fields = fields


class MatchInviteSerializer(serializers.ModelSerializer):
    invitee_username = serializers.SerializerMethodField()

    class Meta:
        model = MatchInvite
        fields = ["id", "invitee_id", "invitee_username", "inviter_id", "status", "created_at"]
        read_only_fields = fields

    @extend_schema_field(serializers.CharField())
    def get_invitee_username(self, obj):
        from apps.users.services import UserService
        u = UserService.get_user(obj.invitee_id)
        return u.username if u else f"user_{obj.invitee_id}"


class MatchSerializer(serializers.ModelSerializer):
    players = MatchPlayerSerializer(many=True, read_only=True)
    invites = MatchInviteSerializer(many=True, read_only=True)

    class Meta:
        model = Match
        fields = [
            "id",
            "game_slug",
            "scene_slug",
            "mode",
            "status",
            "channel_name",
            "host_user_id",
            "max_players",
            "metadata",
            "players",
            "invites",
            "created_at",
            "finished_at",
        ]
        read_only_fields = fields


class SceneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scene
        fields = [
            "id",
            "name",
            "description",
            "slug",
            "game",
            "image",
            "mode",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields
