from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"games", views.GameViewSet, basename="game")
router.register(r"scenes", views.SceneViewSet, basename="scene")

urlpatterns = [
    path("", include(router.urls)),
]
