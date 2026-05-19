from __future__ import absolute_import, unicode_literals

import os

from .celery import app as celery_app

__all__ = ["celery_app"]
__openwisp_version__ = os.environ.get("OPENWISP_VERSION", "dev")
__openwisp_installation_method__ = "docker-openwisp"
