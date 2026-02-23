"""Group filters per admin-crud: searchInput."""
import django_filters
from django.db.models import Q
from .models import Tag, Category


class TagFilter(django_filters.FilterSet):
    searchInput = django_filters.CharFilter(method="filter_search")

    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(name__icontains=value)
            | Q(description__icontains=value)
            | Q(label__icontains=value)
        )


class CategoryFilter(django_filters.FilterSet):
    searchInput = django_filters.CharFilter(method="filter_search")

    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(name__icontains=value)
            | Q(description__icontains=value)
            | Q(label__icontains=value)
        )
