"""
User auth endpoints per .cursor/docs/core/auth/

- Login: guest (deviceId), username/password (+allowRegister), OTP (request + verify), email/phone + password
- Signup, Logout
- Update profile, UpdatePassword, Update OTP, UpdateDeviceId
"""
import re
import uuid
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema

from apps.commons.response import ResponseCode, api_response
from .serializers import (
    LoginSerializer,
    LoginGuestSerializer,
    LoginOTPSerializer,
    LoginOTPVerifySerializer,
    LoginEmailPhoneSerializer,
    SignupSerializer,
    UpdateProfileSerializer,
    UpdatePasswordSerializer,
    UpdateOTPSerializer,
    UpdateDeviceIdSerializer,
    TokenRefreshSerializer,
)
from .models import UserProfile
from .auth_utils import get_tokens_for_user
from .otp_token import generate_otp_code, create_otp_token, decode_otp_token
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

# Regex for validation
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
PHONE_REGEX = re.compile(r"^\+?[0-9\s\-()]{10,}$")


def _get_user_auth_data(user):
    """Build UserAuth-like dict for response."""
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return {
        "id": user.id,
        "username": user.username or "",
        "email": user.email or "",
        "name": user.first_name or "",
        "lastName": user.last_name or "",
        "born": str(profile.born) if profile.born else None,
        "metaData": profile.meta_data,
        "contents": profile.contents,
        "phoneNumber": profile.phone_number or "",
        "deviceId": profile.device_id or "",
        "isGuest": profile.is_guest,
        "role": profile.role,
    }


@extend_schema(request=LoginGuestSerializer, responses={200: None, 201: None})
@csrf_exempt
@api_view(["POST"])
def login_guest(request):
    """Login(deviceId) - guest login. Creates UserAuth+UserProfile with isGuest=true if new."""
    serializer = LoginGuestSerializer(data=request.data)
    if not serializer.is_valid():
        return api_response("VALIDATION_ERROR", meta=serializer.errors, status=400)
    device_id = serializer.validated_data["deviceId"].strip()
    if not device_id:
        return api_response(ResponseCode.DEVICE_ID_NOT_FOUND, status=400)
    profile = UserProfile.objects.filter(device_id=device_id).select_related("user").first()
    if profile:
        user = profile.user
        login(request, user)
        tokens = get_tokens_for_user(user)
        data = {**_get_user_auth_data(user), **tokens}
        return api_response(ResponseCode.SUCCESS, data=data, status=200)
    username = f"guest_{uuid.uuid4().hex[:16]}"
    user = User.objects.create_user(username=username)
    profile = UserProfile.objects.create(user=user, device_id=device_id, is_guest=True)
    login(request, user)
    tokens = get_tokens_for_user(user)
    data = {**_get_user_auth_data(user), **tokens}
    return api_response(ResponseCode.SUCCESS, data=data, status=201)


@extend_schema(request=LoginSerializer, responses={200: None, 201: None})
@csrf_exempt
@api_view(["POST"])
def login_view(request):
    """Login(username, password, allowRegister) - username/password with optional auto-register."""
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return api_response("VALIDATION_ERROR", meta=serializer.errors, status=400)
    username = serializer.validated_data["username"]
    password = serializer.validated_data["password"]
    allow_register = serializer.validated_data.get("allowRegister", False)
    user = User.objects.filter(username=username).first()
    if user is None:
        if not allow_register:
            return api_response(ResponseCode.USER_NOT_FOUND, status=404)
        user = User.objects.create_user(username=username, password=password)
        UserProfile.objects.get_or_create(user=user)
        login(request, user)
        tokens = get_tokens_for_user(user)
        data = {**_get_user_auth_data(user), **tokens}
        return api_response(ResponseCode.SUCCESS, data=data, status=201)
    if not user.check_password(password):
        return api_response(ResponseCode.PASSWORD_IS_WRONG, status=401)
    login(request, user)
    tokens = get_tokens_for_user(user)
    data = {**_get_user_auth_data(user), **tokens}
    return api_response(ResponseCode.SUCCESS, data=data, status=200)


@extend_schema(request=SignupSerializer, responses={201: None})
@csrf_exempt
@api_view(["POST"])
def signup_view(request):
    """Create new user account."""
    serializer = SignupSerializer(data=request.data)
    if not serializer.is_valid():
        return api_response("VALIDATION_ERROR", meta=serializer.errors, status=400)
    data = serializer.validated_data
    if User.objects.filter(username=data["username"]).exists():
        return api_response("USERNAME_ALREADY_EXISTS", status=400)
    user = User.objects.create_user(
        username=data["username"],
        password=data["password"],
        email=data.get("email") or "",
        first_name=data.get("fullName") or "",
    )
    UserProfile.objects.get_or_create(user=user)
    login(request, user)
    tokens = get_tokens_for_user(user)
    data_resp = {**_get_user_auth_data(user), **tokens}
    return api_response(ResponseCode.SUCCESS, data=data_resp, status=201)


@extend_schema(request=LoginOTPSerializer, responses={201: None})
@csrf_exempt
@api_view(["POST"])
def login_otp(request):
    """Login(value, type) - request OTP. Validates value, sends OTP (stub), returns JWT token."""
    serializer = LoginOTPSerializer(data=request.data)
    if not serializer.is_valid():
        return api_response("VALIDATION_ERROR", meta=serializer.errors, status=400)
    value = serializer.validated_data["value"].strip()
    otp_type = serializer.validated_data["type"]
    if otp_type == "phoneNumber" and not PHONE_REGEX.match(value):
        return api_response(ResponseCode.PHONE_NUMBER_IS_NOT_VALID, status=400)
    if otp_type == "email" and not EMAIL_REGEX.match(value):
        return api_response(ResponseCode.EMAIL_IS_NOT_VALID, status=400)
    user = None
    if otp_type == "phoneNumber":
        profile = UserProfile.objects.filter(phone_number=value).select_related("user").first()
        user = profile.user if profile else None
    else:
        user = User.objects.filter(email=value).first()
    user_id = user.id if user else None
    otp_code = generate_otp_code()
    token = create_otp_token(user_id=user_id, value=value, otp_type=otp_type, otp_code=otp_code)
    # Stub: send OTP via SMS/Email - in production integrate with SMS/Email provider
    return api_response(ResponseCode.SUCCESS, data={"token": token}, status=201)


@extend_schema(request=LoginOTPVerifySerializer, responses={200: None})
@csrf_exempt
@api_view(["POST"])
def login_otp_verify(request):
    """Verify(otpCode) - token required. Login or register on success."""
    serializer = LoginOTPVerifySerializer(data=request.data)
    if not serializer.is_valid():
        return api_response("VALIDATION_ERROR", meta=serializer.errors, status=400)
    otp_code = serializer.validated_data["otpCode"]
    token = serializer.validated_data.get("token") or (
        request.headers.get("Authorization", "").replace("Bearer ", "").strip()
    )
    if not token:
        return api_response("VALIDATION_ERROR", meta={"token": "Required"}, status=400)
    payload = decode_otp_token(token)
    if not payload or payload.get("otpCode") != otp_code:
        return api_response("VALIDATION_ERROR", meta={"otpCode": "Invalid or expired"}, status=400)
    user_id = payload.get("userAuthId")
    value = payload.get("value")
    otp_type = payload.get("type")
    user = User.objects.get(pk=user_id) if user_id else None
    if user is None:
        username = f"user_{uuid.uuid4().hex[:12]}"
        user = User.objects.create_user(username=username)
        profile = UserProfile.objects.create(user=user, is_guest=False)
        if otp_type == "email":
            user.email = value
        else:
            profile.phone_number = value
        user.save()
        profile.save()
    else:
        profile, _ = UserProfile.objects.get_or_create(user=user)
        if otp_type == "email" and user.email != value:
            user.email = value
            user.save()
        elif otp_type == "phoneNumber" and profile.phone_number != value:
            profile.phone_number = value
            profile.save()
    login(request, user)
    tokens = get_tokens_for_user(user)
    data = {**_get_user_auth_data(user), **tokens}
    return api_response(ResponseCode.SUCCESS, data=data, status=200)


@extend_schema(request=LoginEmailPhoneSerializer, responses={200: None})
@csrf_exempt
@api_view(["POST"])
def login_email_phone(request):
    """Login(value, valueType, password) - login with email or phone + password."""
    serializer = LoginEmailPhoneSerializer(data=request.data)
    if not serializer.is_valid():
        return api_response("VALIDATION_ERROR", meta=serializer.errors, status=400)
    value = serializer.validated_data["value"].strip()
    value_type = serializer.validated_data["valueType"]
    password = serializer.validated_data["password"]
    user = None
    if value_type == "Email":
        user = User.objects.filter(email=value).first()
    else:
        profile = UserProfile.objects.filter(phone_number=value).select_related("user").first()
        user = profile.user if profile else None
    if user is None:
        return api_response(ResponseCode.USER_NOT_FOUND, status=404)
    if not user.check_password(password):
        return api_response(ResponseCode.PASSWORD_IS_WRONG, status=401)
    login(request, user)
    tokens = get_tokens_for_user(user)
    data = {**_get_user_auth_data(user), **tokens}
    return api_response(ResponseCode.SUCCESS, data=data, status=200)


@extend_schema(request=TokenRefreshSerializer, responses={200: None})
@csrf_exempt
@api_view(["POST"])
def token_refresh(request):
    """Refresh JWT. Accepts refreshToken or refresh in body. Returns {token, refreshToken}."""
    refresh_str = (
        request.data.get("refreshToken")
        or request.data.get("refresh")
    )
    if not refresh_str:
        return api_response("VALIDATION_ERROR", meta={"refreshToken": "Required"}, status=400)
    try:
        refresh = RefreshToken(refresh_str)
        tokens = {
            "token": str(refresh.access_token),
            "refreshToken": str(refresh),
        }
        return api_response(ResponseCode.SUCCESS, data=tokens, status=200)
    except Exception:
        return api_response("VALIDATION_ERROR", meta={"refreshToken": "Invalid or expired"}, status=400)


@extend_schema(request=None, responses={200: None})
@csrf_exempt
@api_view(["POST"])
def logout_view(request):
    """Logout current user."""
    logout(request)
    return api_response(ResponseCode.SUCCESS, data=None, status=200)


@extend_schema(responses={200: None})
@api_view(["GET"])
def me(request):
    """Current user profile."""
    if not request.user.is_authenticated:
        return api_response(ResponseCode.SUCCESS, data={"anonymous": True}, status=200)
    return api_response(ResponseCode.SUCCESS, data=_get_user_auth_data(request.user), status=200)


@extend_schema(responses={200: None})
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_users(request):
    """Search users by username. GET ?q=username (min 2 chars)."""
    q = (request.GET.get("q") or "").strip()
    if len(q) < 2:
        return api_response(ResponseCode.SUCCESS, data=[], status=200)
    users = User.objects.filter(username__icontains=q).exclude(pk=request.user.id)[:20]
    data = [{"id": u.id, "username": u.username or ""} for u in users]
    return api_response(ResponseCode.SUCCESS, data=data, status=200)


@extend_schema(request=UpdateProfileSerializer, responses={200: None})
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
    if "contents" in data:
        profile.contents = data["contents"]
    profile.save()
    return api_response(ResponseCode.SUCCESS, data=_get_user_auth_data(user), status=200)


@extend_schema(request=UpdatePasswordSerializer, responses={200: None})
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def update_password(request):
    """UpdatePassword - set or change password. No currentPassword needed for guests (no password)."""
    serializer = UpdatePasswordSerializer(data=request.data)
    if not serializer.is_valid():
        return api_response("VALIDATION_ERROR", meta=serializer.errors, status=400)
    user = request.user
    new_password = serializer.validated_data["newPassword"]
    current_password = serializer.validated_data.get("currentPassword")
    if user.has_usable_password():
        if not current_password:
            return api_response("VALIDATION_ERROR", meta={"currentPassword": "Required"}, status=400)
        if not user.check_password(current_password):
            return api_response(ResponseCode.CURRENT_PASSWORD_IS_WRONG, status=401)
    user.set_password(new_password)
    user.save()
    return api_response(ResponseCode.SUCCESS, data=_get_user_auth_data(user), status=200)


@extend_schema(request=UpdateOTPSerializer, responses={201: None})
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

    otp_code = generate_otp_code()
    token = create_otp_token(user_id=user.id, value=value, otp_type=otp_type, otp_code=otp_code)
    # Stub: send OTP via SMS/Email - in production integrate with SMS/Email provider
    return api_response(ResponseCode.SUCCESS, data={"token": token}, status=201)


@extend_schema(request=UpdateDeviceIdSerializer, responses={200: None})
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
    tokens = get_tokens_for_user(request.user)
    data = {**_get_user_auth_data(request.user), **tokens}
    return api_response(ResponseCode.SUCCESS, data=data, status=200)
