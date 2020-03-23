from django.urls import include, path
from openwisp_network_topology.api import urls as api

urlpatterns = [
    path('api/', include(api)),
]
