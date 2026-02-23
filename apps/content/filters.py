"""Content filters per admin-crud: tagsId, categoryIds, searchInput."""
import django_filters
from django.db.models import Q
from .models import Content


class BaseIntegerInFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    pass


class ContentFilter(django_filters.FilterSet):
    tagsId = BaseIntegerInFilter(field_name="tags__id", lookup_expr="in")
    categoryIds = BaseIntegerInFilter(field_name="category_id", lookup_expr="in")
    searchInput = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = Content
        fields = ["access", "type", "category", "owner", "language"]

    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(name__icontains=value)
            | Q(description__icontains=value)
            | Q(message__icontains=value)
        )
