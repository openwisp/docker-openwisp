import os
from django.urls import include, path
from openwisp.utils import env_bool, openwisp_controller_urls

urlpatterns = openwisp_controller_urls()

if env_bool(os.environ['USE_OPENWISP_TOPOLOGY']):
    from openwisp_network_topology.api import views
    from openwisp_network_topology.utils import get_api_urls as topology_api

    urlpatterns += [path('api/v1/', include(topology_api(views)))]

if env_bool(os.environ['USE_OPENWISP_FIRMWARE']):
    urlpatterns += [
        path(
            'api/v1/',
            include('openwisp_firmware_upgrader.api.urls', namespace='firmware'),
        ),
        path('', include('openwisp_firmware_upgrader.private_storage.urls')),
    ]

if env_bool(os.environ['USE_OPENWISP_MONITORING']):
    urlpatterns += [
        path(
            '', include('openwisp_monitoring.device.api.urls', namespace='monitoring'),
        )
    ]
