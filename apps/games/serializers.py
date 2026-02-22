from rest_framework import serializers
from .models import Game, Scene


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
