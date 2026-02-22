"""Resource service - public API for other modules."""
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import Resource


class ResourceService:
    @staticmethod
    def get_by_id(pk: int) -> Resource:
        return get_object_or_404(Resource, pk=pk)

    @staticmethod
    def list_all():
        return Resource.objects.all()

    @staticmethod
    def get_all_filtered(owner_resource_id=None, resource_type=None, tag_ids=None, search=None):
        qs = Resource.objects.all()
        if owner_resource_id:
            qs = qs.filter(owner_resource_id=owner_resource_id)
        if resource_type:
            qs = qs.filter(type=resource_type)
        if tag_ids:
            qs = qs.filter(tags__id__in=tag_ids).distinct()
        if search:
            qs = qs.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        return qs
