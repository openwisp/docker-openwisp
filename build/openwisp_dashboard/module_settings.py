import os
from openwisp.controller_settings import *
from openwisp.radius_settings import *
from openwisp.topology_settings import *

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
    # openwisp modules
    'openwisp_users',
    # openwisp-controller
    'openwisp_controller.pki',
    'openwisp_controller.config',
    'openwisp_controller.geo',
    # openwisp-network-topology
    'openwisp_network_topology',
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
    'django_filters',
    # channels
    'channels',
    # registration
    'rest_framework.authtoken',
    'rest_auth',
    'rest_auth.registration',
    # social login
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.google',
    # openwisp-radius
    'openwisp_radius',
]

# Overwrite all previously set EXTENDED_APPS
# To ensure the desired order is maintained
# and we have no unpredictable migrations
# by any future changes.
EXTENDED_APPS = ['django_freeradius',
                 'django_netjsongraph',
                 'django_netjsonconfig',
                 'django_x509',
                 'django_loci']

CORS_ORIGIN_ALLOW_ALL = bool(
    os.environ['DJANGO_DASHBOARD_CORS_ORIGIN_ALLOW_ALL'])
