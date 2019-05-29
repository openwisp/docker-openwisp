# This python script will take care of anything
# required during building the images. It is
# used by Makefile.

import random
import re
import sys


def change_secret_key(keygen):
    # Update the generated secret key
    # in the .env file.

    file_handle = open(".env", 'r')
    file_string = file_handle.read()
    file_handle.close()
    file_string = re.sub(r'DJANGO_SECRET_KEY=.*',
                         r'DJANGO_SECRET_KEY=' + keygen,
                         file_string)
    if file_string[-1] != "\n":
        file_string += "\n"
    if "DJANGO_SECRET_KEY" not in file_string:
        file_string += "DJANGO_SECRET_KEY=" + keygen
    file_handle = open(".env", 'w')
    file_handle.write(file_string)
    file_handle.close()


def get_secret_key():
    chars = 'abcdefghijklmnopqrstuvwxyz' \
            'ABCDEFGHIJKLMNOPQRSTUVXYZ' \
            '0123456789' \
            '#^[]-_*%&=+/'
    keygen = ''.join([random.SystemRandom().choice(chars)
                      for _ in range(50)])
    print(keygen)
    return keygen


if __name__ == "__main__":
    arguments = sys.argv[1:]
    if "get-secret-key" in arguments:
        get_secret_key()
    if "change-secret-key" in arguments:
        keygen = get_secret_key()
        change_secret_key(keygen)
    if "default-secret-key" in arguments:
        change_secret_key("default_secret_key")
