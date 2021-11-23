"""
ASGI config for Battle of Chains project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/deployment/asgi/

"""
import os
import sys
from pathlib import Path
from urllib.parse import parse_qs

from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

# This allows easy placement of apps within the interior
# battle_of_chains directory.
ROOT_DIR = Path(__file__).resolve(strict=True).parent.parent
sys.path.append(str(ROOT_DIR / "battle_of_chains"))

# If DJANGO_SETTINGS_MODULE is unset, default to the local settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

# This application object is used by any ASGI server configured to use this file.
django_application = get_asgi_application()
from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token

from battle_of_chains.socketio_server.routing import websocket_urlpatterns


@database_sync_to_async
def get_user_by_token(token_key):
    try:
        return Token.objects.get(key=token_key).user
    except Token.DoesNotExist:
        return AnonymousUser()


class TokenAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        user = scope.get('user')
        if not user or user.is_anonymous:
            qs = parse_qs(scope["query_string"].decode())
            token = qs.get('token')
            if token:
                scope['user'] = await get_user_by_token(token[0])

        return await self.app(scope, receive, send)


application = ProtocolTypeRouter({
  "http": get_asgi_application(),
  "websocket": AuthMiddlewareStack(
        TokenAuthMiddleware(
            URLRouter(
                websocket_urlpatterns
            )
        )
    ),
})
