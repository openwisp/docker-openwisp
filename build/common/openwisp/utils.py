# Utility functions for django modules
# that are used in multiple openwisp modules
import logging
import socket


class HostFilter(logging.Filter):
    # Used in logging for printing hostname
    # of the container with log details
    def filter(self, record):
        record.host = socket.gethostname()
        return True


# Setting correct urlpatterns for the
# modules -- used in urls.py
def openwisp_topology_urls():
    from openwisp_network_topology.urls import urlpatterns as network_topology_urls
    exclude = ["openwisp_users.accounts.urls"]
    for url in network_topology_urls[:]:
        if url.urlconf_module.__name__ in exclude:
            network_topology_urls.remove(url)
    return network_topology_urls


def openwisp_controller_urls():
    from openwisp_controller.urls import urlpatterns as controller_urls
    exclude = ["openwisp_users.accounts.urls"]
    for url in controller_urls[:]:
        if url.urlconf_module.__name__ in exclude:
            controller_urls.remove(url)
    return controller_urls
