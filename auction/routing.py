from django.urls import path
from auction import consumers

websocket_urlpatterns = [
    path(r'auction/data/', consumers.AuctionConsumer.as_asgi()),
]