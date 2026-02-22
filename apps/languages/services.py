"""Language service - public API for other modules."""
from django.shortcuts import get_object_or_404

from .models import Language


class LanguageService:
    @staticmethod
    def get_by_id(pk: int) -> Language:
        return get_object_or_404(Language, pk=pk)

    @staticmethod
    def list_all():
        return Language.objects.all()
