from django.contrib import admin
from .models import Game, Scene, Mode


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    list_display_links = ("name",)
    list_editable = ("slug",)
    search_fields = ("name", "slug")
    list_filter = ("created_at",)
    list_per_page = 10
    list_max_show_all = 100

    fieldsets = (
        (
            "General",
            {
                "fields": ("name", "slug", "description", "image", "html_layout"),
            },
        ),
    )
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj:
            fieldsets = [
                (None, {"fields": ("name", "slug", "description", "image")}),
            ]
        return fieldsets


@admin.register(Scene)
class SceneAdmin(admin.ModelAdmin):
    list_display = ("name", "game", "mode", "team_mode", "watchable")
    search_fields = ("name",)
    list_filter = ("game", "mode", "team_mode")
    list_per_page = 10
    list_max_show_all = 100

    fieldsets = (
        ("General", {"fields": ("name", "description", "slug", "game", "image")}),
        ("Game Mode", {"fields": ("mode",)}),
        (
            "Player limits (real-time / turn-based)",
            {
                "fields": ("infinite", "min_players", "max_players"),
                "description": "Shown only when mode is real-time or turn-based.",
            },
        ),
        ("Multiplayer", {"fields": ("team_mode",)}),
        (
            "Team settings",
            {
                "fields": ("team_count", "team_size"),
                "description": "Shown only when team mode is enabled.",
            },
        ),
        ("Watch", {"fields": ("watchable",)}),
        ("Metadata", {"fields": ("metadata",)}),
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj is None:
            return fieldsets
        result = []
        for name, opts in fieldsets:
            if name == "Player limits (real-time / turn-based)":
                if obj.mode not in (Mode.REAL_TIME, Mode.TURN_BASED):
                    continue
            if name == "Team settings":
                if not obj.team_mode:
                    continue
            result.append((name, opts))
        return result