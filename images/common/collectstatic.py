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


def get_dir_shasum(directory_path):
    """Return a sha256 hexdigest of all files (names + contents) under directory_path.

    If the directory does not exist, return the hash of empty contents.
    """
    if not os.path.exists(directory_path):
        return hashlib.sha256(b"").hexdigest()
    hasher = hashlib.sha256()
    for root, dirs, files in os.walk(directory_path):
        dirs.sort()
        files.sort()
        for fname in files:
            fpath = os.path.join(root, fname)
            relpath = os.path.relpath(fpath, directory_path)
            hasher.update(relpath.encode())
            try:
                with open(fpath, "rb") as fh:
                    for chunk in iter(lambda: fh.read(4096), b""):
                        hasher.update(chunk)
            except OSError:
                # If a file can't be read, skip it but continue hashing others
                continue
    return hasher.hexdigest()


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
    current_static_hash = get_dir_shasum(
        os.path.join(settings.BASE_DIR, "static_custom")
    )
    cached_pip_hash = redis_connection.get("pip_freeze_hash")
    cached_static_hash = redis_connection.get("static_custom_hash")
    pip_changed = not cached_pip_hash or cached_pip_hash.decode() != current_pip_hash
    static_changed = (
        not cached_static_hash or cached_static_hash.decode() != current_static_hash
    )
    if pip_changed or static_changed:
        print(
            "Changes in Python dependencies or static_custom detected,"
            " running collectstatic..."
        )
        run_collectstatic()
        try:
            redis_connection.set("pip_freeze_hash", current_pip_hash)
            redis_connection.set("static_custom_hash", current_static_hash)
        except Exception:
            # If caching fails, don't crash the startup; collectstatic already ran
            pass
    else:
        print(
            "No changes in Python dependencies or static_custom,"
            " skipping collectstatic..."
        )


if __name__ == "__main__":
    main()
