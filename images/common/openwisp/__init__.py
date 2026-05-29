from __future__ import absolute_import, unicode_literals

import os

from .celery import app as celery_app

__all__ = ["celery_app"]

try:
    with open(os.path.join(os.path.dirname(__file__), ".version-info"), "r") as f:
        __openwisp_version__ = f.read().strip()
except FileNotFoundError:
    __openwisp_version__ = "unknown"

__openwisp_installation_method__ = "docker-openwisp"
