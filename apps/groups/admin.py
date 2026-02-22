from django.contrib import admin
from .models import Tag, Category


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "label", "created_at"]
    search_fields = ["name", "description"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "label", "created_at"]
    search_fields = ["name", "description"]
