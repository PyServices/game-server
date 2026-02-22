"""Credits API - REST only. Uses CreditService (no direct model access)."""
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .services import CreditService
from .serializers import CreditSerializer
from apps.commons.mixins import StandardResponseMixin


class CreditViewSet(StandardResponseMixin, viewsets.ModelViewSet):
    """List and retrieve credits."""
    serializer_class = CreditSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["name", "about", "role"]
    ordering_fields = ["order", "created_at"]
    ordering = ["order"]

    def get_queryset(self):
        return CreditService.list_credits()
