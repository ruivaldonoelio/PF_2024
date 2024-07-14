from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('forum/<int:forum_id>/', consumers.ChatConsumer.as_asgi()),
]
