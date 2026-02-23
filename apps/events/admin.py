from django.contrib import admin
from .models import Event, UserEvent


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ["event", "name", "value_type", "readonly", "created_at"]
    list_filter = ["readonly", "value_type"]
    search_fields = ["event", "name"]


@admin.register(UserEvent)
class UserEventAdmin(admin.ModelAdmin):
    list_display = ["event", "user", "value", "created_at"]
    list_filter = ["event", "created_at"]
    search_fields = ["request_entity_id", "target_entity_id"]
