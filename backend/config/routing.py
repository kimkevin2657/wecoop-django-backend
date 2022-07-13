from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

import api.v1.chat.routing
import api.v1.conference.routing
from config.ws_middleware import TokenAuthMiddlewareStack

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': TokenAuthMiddlewareStack(
        URLRouter([
            *api.v1.chat.routing.websocket_urlpatterns,
            *api.v1.conference.routing.websocket_urlpatterns,
        ]),
    ),
})
