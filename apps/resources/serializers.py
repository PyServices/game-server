from rest_framework import serializers
from .models import Resource, ResourceType


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = [
            "id",
            "name",
            "description",
            "metadata",
            "category",
            "tags",
            "is_consumable",
            "type",
            "owner_resource",
            "contents",
            "stable_value",
            "config",
            "default_amount",
            "data",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["is_consumable"]  # Currency forces True

    def validate_owner_resource(self, value):
        if value and value.type != ResourceType.ASSET:
            raise serializers.ValidationError("Owner Resource must be of type Asset.")
        return value
