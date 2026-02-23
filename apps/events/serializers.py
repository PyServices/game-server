from rest_framework import serializers
from .models import Event, UserEvent


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            "id", "name", "event", "category", "tags", "prize_id",
            "readonly", "value_type", "created_at", "updated_at",
        ]
        read_only_fields = ["readonly"]


class UserEventSerializer(serializers.ModelSerializer):
    event_name = serializers.CharField(source="event.event", read_only=True)

    class Meta:
        model = UserEvent
        fields = [
            "id", "event", "event_name", "user", "request_entity_id",
            "target_entity_id", "value", "meta_data", "created_at",
        ]
        read_only_fields = ["event", "user"]


class SendEventSerializer(serializers.Serializer):
    event = serializers.CharField(help_text="Event string, e.g. Menu:Shop")
    value = serializers.JSONField(required=False, allow_null=True)
    metaData = serializers.JSONField(required=False, default=dict)
    requestEntityId = serializers.CharField(required=False, allow_blank=True)
    targetEntityId = serializers.CharField(required=False, allow_blank=True)
