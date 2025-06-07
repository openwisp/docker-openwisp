import hashlib
import os
import subprocess

import django
import redis
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "openwisp.settings")
django.setup()


def get_pip_freeze_hash():
    output = subprocess.check_output(["pip", "freeze"]).decode()
    return hashlib.sha256(output.encode()).hexdigest()


def main():
    r = redis.Redis.from_url(settings.CACHES["default"]["LOCATION"])
    new_hash = get_pip_freeze_hash()
    stored_hash = r.get("pip_freeze_hash")
    if stored_hash is None or stored_hash.decode() != new_hash:
        print("pip freeze hash changed or missing, running collectstatic...")
        subprocess.run(
            ["python", "manage.py", "collectstatic", "--noinput"], check=True
        )
        r.set("pip_freeze_hash", new_hash)
    else:
        print("pip freeze hash unchanged, skipping collectstatic.")
