"""Game and Scene services - public API for other modules."""
from django.shortcuts import get_object_or_404

from .models import Game, Scene


class GameService:
    """Bridge for game entity access. Other modules use this instead of importing Game."""

    @staticmethod
    def get_game_by_slug(slug: str) -> Game:
        return get_object_or_404(Game, slug=slug)

    @staticmethod
    def get_game_by_id(pk: int) -> Game | None:
        try:
            return Game.objects.get(pk=pk)
        except Game.DoesNotExist:
            return None

    @staticmethod
    def list_games():
        return Game.objects.all()


class SceneService:
    """Bridge for scene entity access."""

    @staticmethod
    def get_scenes_for_game_id(game_id: int):
        return Scene.objects.filter(game_id=game_id)

    @staticmethod
    def get_scene_by_game_and_slug(game_id: int, scene_slug: str) -> Scene:
        return get_object_or_404(Scene, game_id=game_id, slug=scene_slug)

    @staticmethod
    def list_scenes():
        return Scene.objects.all()
