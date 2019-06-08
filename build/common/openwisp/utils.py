# Utility functions for django modules
# that are used in multiple openwisp modules


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
