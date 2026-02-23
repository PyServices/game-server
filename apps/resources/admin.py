from django.contrib import admin
from .models import Resource, UserResource


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "type", "is_consumable", "stable_value", "created_at"]
    list_filter = ["type", "is_consumable"]
    search_fields = ["name", "description"]
    filter_horizontal = ["tags"]


@admin.register(UserResource)
class UserResourceAdmin(admin.ModelAdmin):
    list_display = ["user", "resource", "value", "created_at"]
    list_filter = ["resource"]
    search_fields = ["user__username"]
