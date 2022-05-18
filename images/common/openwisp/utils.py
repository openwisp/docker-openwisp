# Utility functions for django modules
# that are used in multiple openwisp modules
import json
import logging
import os
import socket


class HostFilter(logging.Filter):
    # Used in logging for printing hostname
    # of the container with log details
    def filter(self, record):
        record.host = socket.gethostname()
        return True


def is_string_env_json(env_json):
    try:
        json.loads(env_json)
    except ValueError:
        return False
    return True


def is_string_env_bool(env):
    return env.lower() in ['true', 'yes', 'false', 'no']


def env_bool(env):
    return env.lower() in ['true', 'yes']


def request_scheme():
    # os.environ['SSL_CERT_MODE'] can have different
    # values: True | False | External | SelfSigned
    if os.environ['SSL_CERT_MODE'] in ['False', 'false', 'FALSE', 'No', 'no', 'NO']:
        return 'http'
    return 'https'


def openwisp_controller_urls():
    # Setting correct urlpatterns for the
    # modules -- used in urls.py
    from openwisp_controller.urls import urlpatterns as controller_urls

    exclude = ['openwisp_users.accounts.urls']
    for url in controller_urls[:]:
        if url.urlconf_module.__name__ in exclude:
            controller_urls.remove(url)
    return controller_urls
