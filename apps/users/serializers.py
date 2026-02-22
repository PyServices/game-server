from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserAuthSerializer(serializers.ModelSerializer):
    """UserAuth representation for API responses."""

    name = serializers.CharField(source="first_name", required=False)
    lastName = serializers.CharField(source="last_name", required=False)
    metaData = serializers.JSONField(source="profile.meta_data", required=False)
    born = serializers.DateField(source="profile.born", required=False)
    phoneNumber = serializers.CharField(source="profile.phone_number", required=False)
    deviceId = serializers.CharField(source="profile.device_id", required=False)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "name",
            "lastName",
            "born",
            "metaData",
            "phoneNumber",
            "deviceId",
        ]
        read_only_fields = ["id", "username"]


class UpdateProfileSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, max_length=150)
    lastName = serializers.CharField(required=False, max_length=150)
    born = serializers.DateField(required=False, allow_null=True)
    metaData = serializers.JSONField(required=False)


class UpdatePasswordSerializer(serializers.Serializer):
    currentPassword = serializers.CharField(write_only=True)
    newPassword = serializers.CharField(write_only=True)


class UpdateOTPSerializer(serializers.Serializer):
    value = serializers.CharField()
    type = serializers.ChoiceField(choices=["email", "phoneNumber"])


class UpdateDeviceIdSerializer(serializers.Serializer):
    deviceId = serializers.CharField()
