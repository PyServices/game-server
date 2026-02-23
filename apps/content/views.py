"""Content API - CRUD. Owner can CRUD own; admin can CRUD all."""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, BasePermission
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Content
from .services import ContentService
from .serializers import ContentSerializer
from .filters import ContentFilter
from apps.commons.mixins import StandardResponseMixin


class IsOwnerOrAdmin(BasePermission):
    """Allow owner or staff for object-level actions."""

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.owner_id == request.user.id


class ContentViewSet(StandardResponseMixin, viewsets.ModelViewSet):
    serializer_class = ContentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    filterset_class = ContentFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["name", "description", "message"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return ContentService.list_for_user(
            self.request.user,
            is_staff=self.request.user.is_staff,
        )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
