from rest_framework import serializers
from .models import Credit


class CreditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Credit
        fields = [
            "id",
            "name",
            "slug",
            "about",
            "role",
            "image",
            "order",
            "created_at",
        ]
        read_only_fields = fields
