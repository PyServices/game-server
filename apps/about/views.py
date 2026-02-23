"""Credits API - REST only. Uses CreditService (no direct model access)."""
from rest_framework import viewsets
from rest_framework.decorators import action
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

    @action(detail=False, url_path="by-slug/(?P<slug>[^/.]+)", methods=["get"])
    def by_slug(self, request, slug=None):
        """Retrieve a credit by slug."""
        credit = CreditService.get_credit_by_slug(slug)
        serializer = self.get_serializer(credit)
        return self._success(serializer.data)
