from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .services import ResourceService
from .serializers import ResourceSerializer
from .filters import ResourceFilter as ResourceFilterSet
from apps.commons.mixins import StandardResponseMixin


class ResourceViewSet(StandardResponseMixin, viewsets.ModelViewSet):
    serializer_class = ResourceSerializer
    filterset_class = ResourceFilterSet
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return ResourceService.list_all()
