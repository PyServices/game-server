"""Lobby invites - list and accept."""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from apps.games.services import MatchService
from apps.commons.response import api_response


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_lobby_invites(request):
    """List pending lobby invites for current user."""
    user = getattr(request, "user", None)
    if not user or not hasattr(user, "id"):
        return api_response("UNAUTHORIZED", status=401)
    data = MatchService.list_lobby_invites_for_user(user.id)
    return api_response("SUCCESS", data=data, status=200)
