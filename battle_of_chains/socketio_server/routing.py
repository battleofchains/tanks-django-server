from django.conf.urls import re_path, url
from sockpuppet.consumer import SockpuppetConsumerAsgi as SockpuppetConsumer

from . import consumers

websocket_urlpatterns = [
    url(r'^socket.io/', consumers.app),
    re_path(r'ws/sockpuppet-sync', SockpuppetConsumer.as_asgi()),
]
