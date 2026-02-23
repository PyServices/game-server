from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"resources", views.ResourceViewSet, basename="resource")

urlpatterns = [
    path("", include(router.urls)),
    path("user-resources/", views.list_user_resources),
    path("user-resources/add/", views.user_resource_add),
    path("user-resources/set/", views.user_resource_set),
    path("user-resources/use/", views.user_resource_use),
    path("user-resources/give/", views.user_resource_give),
]
