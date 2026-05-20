from __future__ import absolute_import, unicode_literals

import os

from .celery import app as celery_app

__all__ = ["celery_app"]
__openwisp_version__ = os.environ.get("OPENWISP_VERSION")
__openwisp_installation_method__ = "docker-openwisp"

__openwisp_version__ = os.environ.get("OPENWISP_VERSION")
if __openwisp_version__ is None or __openwisp_version__ == "unknown":
    raise RuntimeError(
        "OPENWISP_VERSION not set in image. "
        "This indicates a broken build or image pull."
    )
