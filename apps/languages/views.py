from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .services import LanguageService
from .serializers import LanguageSerializer
from apps.commons.mixins import StandardResponseMixin


class LanguageViewSet(StandardResponseMixin, viewsets.ModelViewSet):
    serializer_class = LanguageSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return LanguageService.list_all()
