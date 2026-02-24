from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"games", views.GameViewSet, basename="game")
router.register(r"scenes", views.SceneViewSet, basename="scene")

urlpatterns = [
    path("", include(router.urls)),
    # Nested: /api/games/<game_slug>/matches/
    path(
        "<str:game_slug>/matches/",
        views.MatchViewSet.as_view({"get": "list", "post": "create"}),
        name="match-list",
    ),
    path(
        "<str:game_slug>/matches/<int:id>/",
        views.MatchViewSet.as_view({"get": "retrieve"}),
        name="match-detail",
    ),
    path(
        "<str:game_slug>/matches/<int:id>/join/",
        views.MatchViewSet.as_view({"post": "join"}),
        name="match-join",
    ),
    path(
        "<str:game_slug>/matches/<int:id>/leave/",
        views.MatchViewSet.as_view({"post": "leave"}),
        name="match-leave",
    ),
    path(
        "<str:game_slug>/matches/<int:id>/start/",
        views.MatchViewSet.as_view({"post": "start"}),
        name="match-start",
    ),
    path(
        "<str:game_slug>/matches/<int:id>/invite/",
        views.MatchViewSet.as_view({"post": "invite"}),
        name="match-invite",
    ),
    path(
        "<str:game_slug>/matches/<int:id>/accept-invite/",
        views.MatchViewSet.as_view({"post": "accept_invite"}),
        name="match-accept-invite",
    ),
    path(
        "<str:game_slug>/matches/<int:id>/decline-invite/",
        views.MatchViewSet.as_view({"post": "decline_invite"}),
        name="match-decline-invite",
    ),
]
