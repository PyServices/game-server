"""JWT token helpers for auth flows."""
from rest_framework_simplejwt.tokens import RefreshToken


def get_tokens_for_user(user):
    """Return {token, refreshToken} for user."""
    refresh = RefreshToken.for_user(user)
    return {
        "token": str(refresh.access_token),
        "refreshToken": str(refresh),
    }
