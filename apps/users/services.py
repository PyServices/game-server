"""User service - public API for other modules. Never import User model from here for cross-module use."""
from django.contrib.auth import get_user_model

User = get_user_model()


class UserService:
    """Bridge for user entity access. Other modules use get_user() instead of importing User."""

    @staticmethod
    def get_user(user_id: int) -> User | None:
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    @staticmethod
    def get_user_or_none(user_id: int | None) -> User | None:
        if user_id is None:
            return None
        return UserService.get_user(user_id)

    @staticmethod
    def get_or_create_profile(user: User):
        """Get or create UserProfile for user."""
        from .models import UserProfile
        profile, _ = UserProfile.objects.get_or_create(user=user, defaults={})
        return profile
