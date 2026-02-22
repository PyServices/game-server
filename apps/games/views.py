"""Games and Scenes API - REST only. Uses GameService/SceneService (no direct model access)."""
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .services import GameService, SceneService
from .serializers import GameSerializer, SceneSerializer
from apps.commons.mixins import StandardResponseMixin


class GameViewSet(StandardResponseMixin, viewsets.ModelViewSet):
    """List and retrieve games."""
    serializer_class = GameSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return GameService.list_games()


class SceneViewSet(StandardResponseMixin, viewsets.ModelViewSet):
    """List and retrieve 3D scenes."""
    serializer_class = SceneSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return SceneService.list_scenes()
