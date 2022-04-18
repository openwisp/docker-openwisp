import os

from django.urls import include, path
from openwisp.utils import env_bool, openwisp_controller_urls
from openwisp_users.api.urls import get_api_urls as ipam_api
from openwisp_users.api.urls import get_api_urls as users_api

urlpatterns = openwisp_controller_urls() + [
    path('api/v1/', include((users_api(), 'users'), namespace='users')),
    path('api/v1/', include('openwisp_utils.api.urls')),
    path('api/v1/', include((ipam_api(), 'ipam'), namespace='ipam')),
]

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
            '',
            include('openwisp_monitoring.device.api.urls', namespace='monitoring'),
        )
    ]

if env_bool(os.environ['USE_OPENWISP_RADIUS']):
    urlpatterns += [path('', include(('openwisp_radius.urls', 'radius')))]
