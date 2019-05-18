"""
Creates the admin user when openwisp2 is installed
"""

from django.conf import settings
from django.contrib.auth import get_user_model

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'openwisp.settings')
django.setup()

User = get_user_model()

User.objects.filter(is_superuser=True).exists() or \
    User.objects.create_superuser("admin", "admin@example.com", "admin")
