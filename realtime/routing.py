from django.urls import re_path
from .consumers import NotificationConsumer, LeaderboardConsumer ,ContestConsumer, EventConsumer

websocket_urlpatterns = [
    re_path(r"ws/notifications/$", NotificationConsumer.as_asgi()),
    re_path(r"ws/leaderboard/$", LeaderboardConsumer.as_asgi()),
    re_path(r"ws/contest-control/$", ContestConsumer.as_asgi()),
    re_path(r"ws/inflation-announcement/$", EventConsumer.as_asgi()),
]