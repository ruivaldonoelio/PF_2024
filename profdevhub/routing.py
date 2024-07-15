from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/forum/<int:forum_id>/', consumers.ChatConsumer.as_asgi()),
]
