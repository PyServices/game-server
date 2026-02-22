"""
Admin CRUD mixin per .cursor/docs/architecture/admin-crud.md

GetAll(tagsId[]=null, categoryIds[]=null, searchInput=null, pageNum=1, limitItem=10)
- Filter by tags, category, search
- Sort by createdAt, updatedAt
- Pagination
"""
from rest_framework import mixins, viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.commons.response import ResponseCode, api_response


class StandardResponseMixin:
    """Wrap list/retrieve responses in {code, data} format."""

    def _success(self, data, status=200):
        return api_response(ResponseCode.SUCCESS, data=data, status=status)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return self._success(response.data, status=response.status_code)

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return self._success(response.data, status=response.status_code)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return self._success(response.data, status=response.status_code)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return self._success(response.data, status=response.status_code)

    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        return self._success(response.data, status=response.status_code)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return self._success(None, status=200)


class FilterSortSearchMixin:
    """
    Add filter (tags, category), search, sort (created_at, updated_at), pagination.
    Override filter_tags_param, filter_category_param, search_fields, ordering_fields as needed.
    """
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]
    search_fields = []  # Override: ["name", "description"]
    filterset_fields = []  # Override for simple filters
    # For M2M tags / FK category - override get_queryset in viewset
