from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    allowRegister = serializers.BooleanField(default=False, required=False)


class LoginGuestSerializer(serializers.Serializer):
    deviceId = serializers.CharField()


class LoginOTPSerializer(serializers.Serializer):
    value = serializers.CharField()
    type = serializers.ChoiceField(choices=["email", "phoneNumber"])


class LoginOTPVerifySerializer(serializers.Serializer):
    otpCode = serializers.CharField()
    token = serializers.CharField(required=False)  # Can also come from Authorization header


class LoginEmailPhoneSerializer(serializers.Serializer):
    value = serializers.CharField()
    valueType = serializers.ChoiceField(choices=["Phone", "Email"])
    password = serializers.CharField(write_only=True)


class SignupSerializer(serializers.Serializer):
    username = serializers.CharField(min_length=3, max_length=150)
    password = serializers.CharField(min_length=6, write_only=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    fullName = serializers.CharField(required=False, allow_blank=True, max_length=255)


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
    contents = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        help_text="Contents Type: [{key, id}]",
    )


class UpdatePasswordSerializer(serializers.Serializer):
    currentPassword = serializers.CharField(write_only=True, required=False)
    newPassword = serializers.CharField(write_only=True)


class UpdateOTPSerializer(serializers.Serializer):
    value = serializers.CharField()
    type = serializers.ChoiceField(choices=["email", "phoneNumber"])


class UpdateDeviceIdSerializer(serializers.Serializer):
    deviceId = serializers.CharField()


class TokenRefreshSerializer(serializers.Serializer):
    refreshToken = serializers.CharField(required=False)
    refresh = serializers.CharField(required=False)
