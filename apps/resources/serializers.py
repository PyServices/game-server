from rest_framework import serializers
from .models import Resource, ResourceType, UserResource


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

    def validate(self, attrs):
        """type and owner_resource are immutable after creation (per docs)."""
        if self.instance:
            if "type" in attrs and attrs["type"] != self.instance.type:
                raise serializers.ValidationError({"type": "Cannot change after creation."})
            if "owner_resource" in attrs:
                new_id = attrs["owner_resource"].pk if attrs["owner_resource"] else None
                if new_id != self.instance.owner_resource_id:
                    raise serializers.ValidationError({"owner_resource": "Cannot change after creation."})
        return attrs


class UserResourceSerializer(serializers.ModelSerializer):
    resource_name = serializers.CharField(source="resource.name", read_only=True)

    class Meta:
        model = UserResource
        fields = ["id", "user", "resource", "resource_name", "owner_user_resource", "value", "created_at", "updated_at"]


class UserResourceAddSerializer(serializers.Serializer):
    resourceId = serializers.IntegerField()
    value = serializers.FloatField()


class UserResourceSetSerializer(serializers.Serializer):
    resourceId = serializers.IntegerField()
    value = serializers.JSONField()


class UserResourceUseSerializer(serializers.Serializer):
    resourceId = serializers.IntegerField()
    value = serializers.FloatField(required=False, allow_null=True)


class UserResourceGiveSerializer(serializers.Serializer):
    resourceId = serializers.IntegerField()
