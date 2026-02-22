"""Tag and Category services - public API for other modules."""
from django.shortcuts import get_object_or_404

from .models import Tag, Category


class TagService:
    @staticmethod
    def get_by_id(pk: int) -> Tag:
        return get_object_or_404(Tag, pk=pk)

    @staticmethod
    def list_all():
        return Tag.objects.all()

    @staticmethod
    def filter_by_ids(ids: list[int]):
        if not ids:
            return Tag.objects.none()
        return Tag.objects.filter(pk__in=ids)


class CategoryService:
    @staticmethod
    def get_by_id(pk: int) -> Category:
        return get_object_or_404(Category, pk=pk)

    @staticmethod
    def list_all():
        return Category.objects.all()

    @staticmethod
    def filter_by_ids(ids: list[int]):
        if not ids:
            return Category.objects.none()
        return Category.objects.filter(pk__in=ids)
