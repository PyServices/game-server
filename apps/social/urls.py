from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FriendsViewSet, ChatRoomViewSet, ChatMessageViewSet, list_lobby_invites

router = DefaultRouter()
router.register(r"friends", FriendsViewSet, basename="friend")
# GET /api/social/friends/requests/ - list incoming requests
router.register(r"rooms", ChatRoomViewSet, basename="chatroom")

urlpatterns = [
    path("", include(router.urls)),
    path("lobby-invites/", list_lobby_invites),
    path(
        "rooms/<int:room_id>/messages/",
        ChatMessageViewSet.as_view({"get": "list", "post": "create"}),
        name="chat-messages",
    ),
]
