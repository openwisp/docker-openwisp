import os
from openwisp.utils import env_bool
from openwisp.radius_settings import *
from openwisp.topology_settings import *
from openwisp.controller_settings import *
from openwisp.utils import request_scheme

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
    'corsheaders',
    # openwisp modules
    'openwisp_users',
    # openwisp-controller
    'openwisp_controller.pki',
    'openwisp_controller.config',
    'openwisp_controller.geo',
    'openwisp_controller.connection',
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

EXTENDED_APPS = ['django_freeradius',
                 'django_netjsongraph',
                 'django_netjsonconfig',
                 'django_x509',
                 'django_loci']

TOPOLOGY_API_URLCONF = 'openwisp_network_topology.urls'
TOPOLOGY_API_BASEURL = f'{request_scheme()}://{os.environ["TOPOLOGY_DOMAIN"]}'

if not env_bool(os.environ['USE_OPENWISP_RADIUS']):
    EXTENDED_APPS.remove('django_freeradius')
    INSTALLED_APPS.remove('openwisp_radius')
if not env_bool(os.environ['USE_OPENWISP_TOPOLOGY']):
    EXTENDED_APPS.remove('django_netjsongraph')
    INSTALLED_APPS.remove('openwisp_network_topology')
