import os

from openwisp.settings import MIDDLEWARE
from openwisp.utils import request_scheme

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
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
    'openwisp_controller.subnet_division',
    # openwisp-monitoring
    'openwisp_monitoring.monitoring',
    'openwisp_monitoring.device',
    'openwisp_monitoring.check',
    'nested_admin',
    # openwisp-notification
    'openwisp_notifications',
    # openwisp-ipam
    'openwisp_ipam',
    # openwisp-network-topology
    'openwisp_network_topology',
    # openwisp-firmware-upgrader
    'openwisp_firmware_upgrader',
    # openwisp-radius
    'openwisp_radius',
    # admin
    'openwisp_utils.admin_theme',
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
    'dj_rest_auth',
    'dj_rest_auth.registration',
    # social login
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.google',
    # other dependencies
    'flat_json_widget',
    'private_storage',
    'drf_yasg',
    'channels',
    'pipeline',
]

EXTENDED_APPS = [
    'django_x509',
    'django_loci',
]
MIDDLEWARE += [
    'pipeline.middleware.MinifyHTMLMiddleware',
]
# HTML minification with django pipeline
PIPELINE = {'PIPELINE_ENABLED': True}
# static files minification and invalidation with django-compress-staticfiles
STATICFILES_STORAGE = 'openwisp_utils.storage.CompressStaticFilesStorage'
BROTLI_STATIC_COMPRESSION = False
# pregenerate static gzip files to save CPU
GZIP_STATIC_COMPRESSION = True

API_BASEURL = f'{request_scheme()}://{os.environ["API_DOMAIN"]}'

OPENWISP_NETWORK_TOPOLOGY_API_URLCONF = 'openwisp_network_topology.urls'
OPENWISP_MONITORING_API_URLCONF = 'openwisp_monitoring.urls'
OPENWISP_RADIUS_API_URLCONF = 'openwisp_radius.urls'
OPENWISP_NETWORK_TOPOLOGY_API_BASEURL = API_BASEURL
OPENWISP_MONITORING_API_BASEURL = API_BASEURL
OPENWISP_FIRMWARE_API_BASEURL = API_BASEURL
OPENWISP_RADIUS_API_BASEURL = API_BASEURL
