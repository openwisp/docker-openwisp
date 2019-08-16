'''
Load initial data before starting the server.
- Add superuser `admin`.
'''

from django.conf import settings
from django.contrib.auth import get_user_model

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'openwisp.settings')
django.setup()

User = get_user_model()


def create_admin():
    '''
    Creates superuser `admin` if it does not exist.
    '''
    User.objects.filter(is_superuser=True).exists() or \
        User.objects.create_superuser("admin", "admin@example.com", "admin")


if __name__ == "__main__":
    create_admin()
