from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"events", views.EventViewSet, basename="event")

urlpatterns = [
    path("", include(router.urls)),
    path("send/", views.send_event),
    path("user-events/", views.get_user_events),
    path("user-events/latest/", views.get_latest_event),
]
