"""OTP flow JWT - contains {userAuthId?, value, type, otpCode, expire} per auth docs."""
import secrets
from datetime import datetime, timedelta
from django.conf import settings
import jwt


OTP_EXPIRE_MINUTES = 10
OTP_LENGTH = 6


def generate_otp_code() -> str:
    """Generate 6-digit OTP code."""
    return "".join(secrets.choice("0123456789") for _ in range(OTP_LENGTH))


def create_otp_token(user_id: int | None, value: str, otp_type: str, otp_code: str) -> str:
    """Create JWT with OTP payload. user_id is None for new user registration."""
    expire = datetime.utcnow() + timedelta(minutes=OTP_EXPIRE_MINUTES)
    payload = {
        "userAuthId": user_id,
        "value": value,
        "type": otp_type,
        "otpCode": otp_code,
        "expire": expire.isoformat(),
        "exp": expire,
    }
    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm="HS256",
    )


def decode_otp_token(token: str) -> dict | None:
    """Decode and validate OTP token. Returns payload or None if invalid."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"],
        )
        return payload
    except jwt.InvalidTokenError:
        return None
