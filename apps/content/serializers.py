from rest_framework import serializers
from .models import Content


class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = [
            "id", "name", "owner", "description", "tags", "category",
            "access", "metadata", "message", "content_url", "type",
            "language", "created_at", "updated_at",
        ]
        read_only_fields = ["owner"]
