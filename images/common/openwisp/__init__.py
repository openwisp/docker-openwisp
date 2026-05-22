from __future__ import absolute_import, unicode_literals

from ._version import __version__ as __openwisp_version__
from .celery import app as celery_app

__all__ = ["celery_app", "__openwisp_version__"]

__openwisp_installation_method__ = "docker-openwisp"
