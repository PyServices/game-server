from django.contrib import admin
from .models import Friendship, ChatRoom, ChatMessage, ChatRoomMember
from apps.users.services import UserService


def _username(user_id: int) -> str:
    u = UserService.get_user(user_id)
    return u.username if u else f"#{user_id}"


@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ["id", "user_display", "friend_display", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["user_id", "friend_id"]

    def user_display(self, obj):
        return _username(obj.user_id)

    user_display.short_description = "User"
    user_display.admin_order_field = "user_id"

    def friend_display(self, obj):
        return _username(obj.friend_id)

    friend_display.short_description = "Friend"
    friend_display.admin_order_field = "friend_id"


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ["id", "room_type", "name", "match_id", "created_at"]
    list_filter = ["room_type"]


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ["id", "room", "user_display", "content_preview", "created_at"]
    list_filter = ["room"]

    def user_display(self, obj):
        return _username(obj.user_id)

    user_display.short_description = "User"
    user_display.admin_order_field = "user_id"

    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

    content_preview.short_description = "Content"


@admin.register(ChatRoomMember)
class ChatRoomMemberAdmin(admin.ModelAdmin):
    list_display = ["id", "room", "user_display", "last_read_at", "joined_at"]
    list_filter = ["room"]

    def user_display(self, obj):
        return _username(obj.user_id)

    user_display.short_description = "User"
    user_display.admin_order_field = "user_id"
