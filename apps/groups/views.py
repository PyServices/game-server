from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .services import TagService, CategoryService
from .serializers import TagSerializer, CategorySerializer
from .filters import TagFilter, CategoryFilter
from apps.commons.mixins import StandardResponseMixin


class TagViewSet(StandardResponseMixin, viewsets.ModelViewSet):
    serializer_class = TagSerializer
    filterset_class = TagFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["name", "description", "label"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return TagService.list_all()


class CategoryViewSet(StandardResponseMixin, viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    filterset_class = CategoryFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["name", "description", "label"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return CategoryService.list_all()
