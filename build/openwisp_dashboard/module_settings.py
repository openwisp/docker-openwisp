import os
from openwisp.utils import env_bool
from openwisp.radius_settings import *
from openwisp.topology_settings import *
from openwisp.api_settings import *
from openwisp.utils import request_scheme

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    # all-auth
    'django.contrib.sites',
    'openwisp_users.accounts',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'corsheaders',
    'django_extensions',
    # openwisp modules
    'openwisp_users',
    # openwisp-controller
    'openwisp_controller.pki',
    'openwisp_controller.config',
    'openwisp_controller.geo',
    'openwisp_controller.connection',
    'flat_json_widget',
    'openwisp_notifications',
    'openwisp_utils.admin_theme',
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
    # registration
    'rest_framework.authtoken',
    'rest_auth',
    'rest_auth.registration',
    # social login
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.google',
    # openwisp-radius
    'openwisp_radius',
    # other dependencies
    'private_storage',
    'drf_yasg',
    'channels',
]

EXTENDED_APPS = [
    'django_x509',
    'django_loci',
]

OPENWISP_NETWORK_TOPOLOGY_API_URLCONF = 'openwisp_network_topology.urls'
OPENWISP_NETWORK_TOPOLOGY_API_BASEURL = (
    f'{request_scheme()}://{os.environ["TOPOLOGY_DOMAIN"]}'
)

if not env_bool(os.environ['USE_OPENWISP_RADIUS']):
    INSTALLED_APPS.remove('openwisp_radius')
if not env_bool(os.environ['USE_OPENWISP_TOPOLOGY']):
    INSTALLED_APPS.remove('openwisp_network_topology')
