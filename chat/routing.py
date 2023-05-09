from django.urls import path
from chat import consumers

websocket_urlpatterns = [
    path('chat/data', consumers.MyConsumer.as_asgi()),
]
