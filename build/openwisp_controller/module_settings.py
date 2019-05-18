import os

# When you change the INSTALLED_APPS here
# Ensure that you change the 
# openwisp_dashboard/migrate_settings.py 
# as well to ensure that correct migrations
# take place.
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    # openwisp admin theme
    # (must be loaded here)
    'openwisp_utils.admin_theme',
    # all-auth
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'django_extensions',
    # openwisp modules
    'openwisp_users',
    'openwisp_controller.pki',
    'openwisp_controller.config',
    'openwisp_controller.geo',
    # admin
    'django.contrib.admin',
    'django.forms',
    # other dependencies
    'sortedm2m',
    'reversion',
    'leaflet',
    # rest framework
    'rest_framework',
    'rest_framework_gis',
    # channels
    'channels'
]

# When you change the EXTENDED_APPS here
# Ensure that you change the
# openwisp_dashboard/migrate_settings.py
# as well to ensure that correct migrations
# take place.
EXTENDED_APPS = [
    'django_netjsonconfig',
    'django_x509',
    'django_loci',
]

REDIS_HOST = os.environ['REDIS_HOST']

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'asgi_redis.RedisChannelLayer',
        'CONFIG': {'hosts': [(REDIS_HOST, 6379)]},
        'ROUTING': 'openwisp_controller.geo.channels.routing.channel_routing',
    },
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://"+REDIS_HOST+":6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

DJANGO_X509_DEFAULT_CERT_VALIDITY = os.environ['DJANGO_X509_DEFAULT_CERT_VALIDITY']
DJANGO_X509_DEFAULT_CA_VALIDITY = os.environ['DJANGO_X509_DEFAULT_CA_VALIDITY']

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'
