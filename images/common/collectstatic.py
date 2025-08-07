"""Run ``collectstatic`` only when dependencies have changed.

Speeds up startup time on cloud platforms. To disable this behavior, set
the ``COLLECTSTATIC_WHEN_DEPS_CHANGE`` environment variable to ``False``.
"""

import hashlib
import os
import subprocess
import sys

import django
import redis
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "openwisp.settings")
django.setup()


def get_pip_freeze_hash():
    try:
        pip_freeze_output = subprocess.check_output(["pip", "freeze"]).decode()
        return hashlib.sha256(pip_freeze_output.encode()).hexdigest()
    except subprocess.CalledProcessError as e:
        print(f"Error running 'pip freeze': {e}", file=sys.stderr)
        sys.exit(1)


def run_collectstatic():
    try:
        subprocess.run(
            [sys.executable, "manage.py", "collectstatic", "--noinput"], check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error running 'collectstatic': {e}", file=sys.stderr)
        sys.exit(1)


def main():
    if os.environ.get("COLLECTSTATIC_WHEN_DEPS_CHANGE", "true").lower() == "false":
        run_collectstatic()
        return
    redis_connection = redis.Redis.from_url(settings.CACHES["default"]["LOCATION"])
    current_pip_hash = get_pip_freeze_hash()
    cached_pip_hash = redis_connection.get("pip_freeze_hash")
    if not cached_pip_hash or cached_pip_hash.decode() != current_pip_hash:
        print("Changes in Python dependencies detected, running collectstatic...")
        run_collectstatic()
        redis_connection.set("pip_freeze_hash", current_pip_hash)
    else:
        print("No changes in Python dependencies, skipping collectstatic...")


if __name__ == "__main__":
    main()
