"""Content service - public API. Owner can CRUD own; admin can CRUD all."""
from django.db.models import Q

from .models import Content


class ContentService:
    @staticmethod
    def list_for_user(user, is_staff=False):
        """List contents: own for regular user, all for staff."""
        if is_staff:
            return Content.objects.all().prefetch_related("tags", "category", "language")
        return Content.objects.filter(owner=user).prefetch_related("tags", "category", "language")

    @staticmethod
    def get_by_id(pk: int, user=None, is_staff=False):
        """Get content by id. Owner or staff only."""
        try:
            obj = Content.objects.get(pk=pk)
        except Content.DoesNotExist:
            return None
        if is_staff:
            return obj
        if obj.owner_id == user.id:
            return obj
        return None
