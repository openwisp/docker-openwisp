# This python script will take care of anything
# required during building the images. It is
# used by Makefile.

import random
import re
import sys


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


def update_makefile_version(new_version: str):
    # Update RELEASE_VERSION in the Makefile to new_version.

    makefile_path = "Makefile"
    with open(makefile_path, "r") as fh:
        content = fh.read()

    updated = re.sub(
        r"^(RELEASE_VERSION\s*=\s*).*$",
        rf"\g<1>{new_version}",
        content,
        flags=re.MULTILINE,
    )
    if updated == content:
        raise RuntimeError(
            f"WARNING: RELEASE_VERSION not found in {makefile_path}; "
            "no changes written."
        )

    with open(makefile_path, "w") as fh:
        fh.write(updated)


def generate_version_module(version: str):
    # Generate images/common/openwisp/_version.py with the given version.

    version_file = "images/common/openwisp/_version.py"
    content = (
        "# This file is auto-generated at Docker image build time.\n"
        "# Do not edit manually.\n"
        f'__version__ = "{version}"\n'
    )
    with open(version_file, "w") as fh:
        fh.write(content)


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

    if "update-version" in arguments:
        try:
            new_version = arguments[arguments.index("update-version") + 1]
        except IndexError:
            print("update-version requires a version argument")
            sys.exit(1)
        update_makefile_version(new_version)
    if "generate-version" in arguments:
        try:
            new_version = arguments[arguments.index("generate-version") + 1]
        except IndexError:
            print("generate-version requires a version argument")
            sys.exit(1)
        generate_version_module(new_version)
