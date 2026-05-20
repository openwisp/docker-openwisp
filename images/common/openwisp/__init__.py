from __future__ import absolute_import, unicode_literals

import os

from .celery import app as celery_app

__all__ = ["celery_app"]

_VERSION_FILE = "/opt/openwisp/OPENWISP_VERSION"


def _read_version() -> str:
    # Early return if file is not found
    if not os.path.exists(_VERSION_FILE):
        raise RuntimeError(f"Could not find {_VERSION_FILE}")

    try:
        with open(_VERSION_FILE) as _f:
            return _f.read().strip()
    except OSError as err:
        raise RuntimeError(
            f"Could not read version from {_VERSION_FILE}. "
            "This file should be baked into the Docker image at build time. "
            "If you are running outside Docker, this is expected."
        ) from err


__openwisp_version__ = _read_version()
__openwisp_installation_method__ = "docker-openwisp"
