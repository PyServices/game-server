"""Credit service - public API for other modules. Uses UserService for user data."""
from django.shortcuts import get_object_or_404

from apps.users.services import UserService

from .models import Credit


class CreditService:
    """Bridge for credit entity access. Uses UserService, never imports User directly."""

    @staticmethod
    def list_credits():
        return Credit.objects.all()

    @staticmethod
    def get_credit_by_user_id(user_id: int) -> Credit:
        return get_object_or_404(Credit, user_id=user_id)

    @staticmethod
    def get_credit_by_slug(slug: str) -> Credit:
        return get_object_or_404(Credit, slug=slug)

    @staticmethod
    def get_credit_by_identifier(identifier: str) -> Credit:
        """Identifier can be user_id (int) or slug (str)."""
        try:
            uid = int(identifier)
            return CreditService.get_credit_by_user_id(uid)
        except ValueError:
            return CreditService.get_credit_by_slug(identifier)

    @staticmethod
    def get_user_for_credit(credit: Credit):
        """Resolve user via service layer."""
        return UserService.get_user_or_none(credit.user_id) if credit.user_id else None
