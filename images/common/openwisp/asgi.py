"""ASGI entrypoint.

Configures Django and then runs the application defined in the
ASGI_APPLICATION setting.
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from openwisp.utils import env_bool

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "openwisp.settings")
django_asgi_app = get_asgi_application()

from openwisp_controller.routing import (  # noqa: E402
    get_routes as get_controller_routes,
)

routes = []
routes.extend(get_controller_routes())

if env_bool(os.environ.get("USE_OPENWISP_TOPOLOGY")):
    from openwisp_network_topology.routing import (  # noqa: E402
        websocket_urlpatterns as network_topology_routes,
    )

    routes.extend(network_topology_routes)

if env_bool(os.environ.get("USE_OPENWISP_FIRMWARE")):
    from openwisp_firmware_upgrader.routing import (  # noqa: E402
        websocket_urlpatterns as firmware_upgrader_routes,
    )

    routes.extend(firmware_upgrader_routes)
if env_bool(os.environ["USE_OPENWISP_RADIUS"]):
    from openwisp_radius.routing import websocket_urlpatterns as radius_routes

    routes.extend(radius_routes)

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(routes))
        ),
    }
)
