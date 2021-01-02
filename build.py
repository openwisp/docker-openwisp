# This python script will take care of anything
# required during building the images. It is
# used by Makefile.

import random
import re
import sys


def randomize_key_value(key, value):
    # Update the generated secret key
    # in the .env file.

    file_handle = open('.env', 'r')
    file_string = file_handle.read()
    file_handle.close()
    file_string = re.sub(fr'{key}=.*', fr'{key}={value}', file_string)
    if file_string[-1] != '\n':
        file_string += '\n'
    if f'{key}' not in file_string:
        file_string += f'{key}={value}'
    file_handle = open('.env', 'w')
    file_handle.write(file_string)
    file_handle.close()


def get_secret_key():
    chars = (
        'abcdefghijklmnopqrstuvwxyz'
        'ABCDEFGHIJKLMNOPQRSTUVXYZ'
        '0123456789'
        '#^[]-_*%&=+/'
    )
    keygen = ''.join([random.SystemRandom().choice(chars) for _ in range(50)])
    print(keygen)
    return keygen


if __name__ == '__main__':
    arguments = sys.argv[1:]
    if 'get-secret-key' in arguments:
        get_secret_key()
    if 'change-secret-key' in arguments:
        keygen = get_secret_key()
        randomize_key_value('DJANGO_SECRET_KEY', keygen)
    if 'default-secret-key' in arguments:
        randomize_key_value('DJANGO_SECRET_KEY', 'default_secret_key')
    if 'change-database-credentials' in arguments:
        keygen1 = get_secret_key()
        keygen2 = get_secret_key()
        randomize_key_value("DB_USER", keygen1)
        randomize_key_value("DB_PASS", keygen2)
