from __future__ import absolute_import, unicode_literals

from pathlib import Path

from .celery import app as celery_app

__all__ = ["celery_app", "__openwisp_version__"]

__openwisp_version__ = Path(__file__).with_name("VERSION").read_text().strip()
__openwisp_installation_method__ = "docker-openwisp"
