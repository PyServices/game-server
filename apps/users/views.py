"""
User auth endpoints per .cursor/docs/core/auth/update.md

- Update profile (name, lastName, born, metaData)
- UpdatePassword
- Update with OTP (email, phoneNumber) - stub
- UpdateDeviceId
"""
import re
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from apps.commons.response import ResponseCode, api_response
from .serializers import (
    UserAuthSerializer,
    UpdateProfileSerializer,
    UpdatePasswordSerializer,
    UpdateOTPSerializer,
    UpdateDeviceIdSerializer,
)
from .models import UserProfile

User = get_user_model()

# Regex for validation
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
PHONE_REGEX = re.compile(r"^\+?[0-9\s\-()]{10,}$")


def _get_user_auth_data(user):
    """Build UserAuth-like dict for response."""
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email or "",
        "name": user.first_name or "",
        "lastName": user.last_name or "",
        "born": str(profile.born) if profile.born else None,
        "metaData": profile.meta_data,
        "phoneNumber": profile.phone_number or "",
        "deviceId": profile.device_id or "",
    }


@api_view(["GET"])
def me(request):
    """Current user profile."""
    if not request.user.is_authenticated:
        return api_response(ResponseCode.SUCCESS, data={"anonymous": True}, status=200)
    return api_response(ResponseCode.SUCCESS, data=_get_user_auth_data(request.user), status=200)


@api_view(["PATCH", "PUT"])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """Update name, lastName, born, metaData."""
    serializer = UpdateProfileSerializer(data=request.data, partial=True)
    if not serializer.is_valid():
        return api_response("VALIDATION_ERROR", meta=serializer.errors, status=400)
    user = request.user
    data = serializer.validated_data
    if "name" in data:
        user.first_name = data["name"]
    if "lastName" in data:
        user.last_name = data["lastName"]
    user.save()
    profile, _ = UserProfile.objects.get_or_create(user=user)
    if "born" in data:
        profile.born = data["born"]
    if "metaData" in data:
        profile.meta_data = data["metaData"]
    profile.save()
    return api_response(ResponseCode.SUCCESS, data=_get_user_auth_data(user), status=200)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def update_password(request):
    """UpdatePassword(userAuthID, currentPassword, NewPassword)."""
    serializer = UpdatePasswordSerializer(data=request.data)
    if not serializer.is_valid():
        return api_response("VALIDATION_ERROR", meta=serializer.errors, status=400)
    user = request.user
    if not user.check_password(serializer.validated_data["currentPassword"]):
        return api_response(
            ResponseCode.CURRENT_PASSWORD_IS_WRONG,
            status=401,
        )
    user.set_password(serializer.validated_data["newPassword"])
    user.save()
    return api_response(ResponseCode.SUCCESS, data=_get_user_auth_data(user), status=200)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def update_otp(request):
    """
    Update email or phoneNumber with OTP.
    Returns JWT token containing {value, type, otpCode, expire} - stub.
    In production: validate value, send OTP, create JWT.
    """
    serializer = UpdateOTPSerializer(data=request.data)
    if not serializer.is_valid():
        return api_response("VALIDATION_ERROR", meta=serializer.errors, status=400)
    value = serializer.validated_data["value"]
    otp_type = serializer.validated_data["type"]
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    if otp_type == "phoneNumber":
        if not PHONE_REGEX.match(value):
            return api_response(ResponseCode.PHONE_NUMBER_IS_NOT_VALID, status=400)
        if profile.phone_number == value:
            return api_response(ResponseCode.PHONE_NUMBER_IS_SAME, status=400)
    elif otp_type == "email":
        if not EMAIL_REGEX.match(value):
            return api_response(ResponseCode.EMAIL_IS_NOT_VALID, status=400)
        if user.email == value:
            return api_response(ResponseCode.EMAIL_IS_SAME, status=400)

    # Stub: return token. In production: send OTP (SMS/Email), create JWT with {value, type, otpCode, expire}
    import hashlib
    import time
    raw = f"{user.id}:{value}:{otp_type}:{time.time()}"
    token = hashlib.sha256(raw.encode()).hexdigest()
    return api_response(ResponseCode.SUCCESS, data={"token": token}, status=201)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def update_device_id(request):
    """UpdateDeviceId(deviceId)."""
    serializer = UpdateDeviceIdSerializer(data=request.data)
    if not serializer.is_valid():
        return api_response("VALIDATION_ERROR", meta=serializer.errors, status=400)
    device_id = serializer.validated_data.get("deviceId")
    if not device_id or not str(device_id).strip():
        return api_response(ResponseCode.DEVICE_ID_NOT_FOUND, status=400)
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    profile.device_id = str(device_id).strip()
    profile.save()
    # Optional: return token, refreshToken - for now return UserAuth
    return api_response(
        ResponseCode.SUCCESS,
        data=_get_user_auth_data(request.user),
        status=200,
    )
