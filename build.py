# This python script will take care of anything
# required during building the images. It is
# used by Makefile.

import random
import re
import sys
from pathlib import Path

VERSION_FILE = Path("images/common/openwisp/VERSION")


def update_env_file(key, value):
    # Update the generated secret key
    # in the .env file.

    with open(".env", "r") as file_handle:
        file_string = file_handle.read()
    file_string = re.sub(rf"{key}=.*", rf"{key}={value}", file_string)
    if file_string[-1] != "\n":
        file_string += "\n"
    if f"{key}" not in file_string:
        file_string += f"{key}={value}"
    with open(".env", "w") as file_handle:
        file_handle.write(file_string)


def get_secret_key(allow_special_chars=True):
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVXYZ0123456789"
    if allow_special_chars:
        chars += "#^[]-_*%&=+/"
    keygen = "".join([random.SystemRandom().choice(chars) for _ in range(50)])
    print(keygen)
    return keygen


def update_version_file(version: str):
    if not VERSION_FILE.exists():
        raise RuntimeError(f"{VERSION_FILE} not found; no changes written.")
    VERSION_FILE.write_text(f"{version}\n")


if __name__ == "__main__":
    arguments = sys.argv[1:]
    if "get-secret-key" in arguments:
        get_secret_key()
    if "change-secret-key" in arguments:
        keygen = get_secret_key()
        update_env_file("DJANGO_SECRET_KEY", keygen)
    if "default-secret-key" in arguments:
        update_env_file("DJANGO_SECRET_KEY", "default_secret_key")
    if "change-database-credentials" in arguments:
        keygen1 = get_secret_key(allow_special_chars=False)
        keygen2 = get_secret_key()
        update_env_file("DB_USER", keygen1)
        update_env_file("DB_PASS", keygen2)
    if "bump-version" in arguments:
        try:
            new_version = arguments[arguments.index("bump-version") + 1]
        except IndexError:
            print("bump-version requires a version argument")
            sys.exit(1)
        update_version_file(new_version)
