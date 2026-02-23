from django.contrib import admin
from .models import Content


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ["name", "owner", "type", "access", "created_at"]
    list_filter = ["type", "access"]
    search_fields = ["name", "description"]
