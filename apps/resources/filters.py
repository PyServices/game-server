import django_filters
from django.db.models import Q
from .models import Resource


class BaseIntegerInFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    pass


class ResourceFilter(django_filters.FilterSet):
    ownerResourceId = django_filters.NumberFilter(field_name="owner_resource_id")
    resourceType = django_filters.CharFilter(field_name="type")
    searchInput = django_filters.CharFilter(method="filter_search")
    tagsId = BaseIntegerInFilter(field_name="tags__id", lookup_expr="in")

    class Meta:
        model = Resource
        fields = ["owner_resource_id", "type"]

    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(Q(name__icontains=value) | Q(description__icontains=value))
