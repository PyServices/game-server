"""
WebSocket URL routing. Includes matchmaking + all game consumers.
"""
from django.urls import re_path

# Import consumers when they are created
# from apps.games.base.matchmaking.consumer import MatchmakingConsumer

websocket_urlpatterns = [
    # Matchmaking: ws://host/ws/matchmaking/<game_slug>/
    # re_path(r'ws/matchmaking/(?P<game_slug>[\w-]+)/$', MatchmakingConsumer.as_asgi()),
    # Game rooms will be added here
]
