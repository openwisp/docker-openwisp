import os

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    # all-auth
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'django_extensions',
    'corsheaders',
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
    'rest_framework.authtoken',
    'django_filters',
    'private_storage',
    'drf_yasg',
    'channels',
]

EXTENDED_APPS = [
    'django_x509',
    'django_loci',
]

# TODO: Remove when https://github.com/openwisp/docker-openwisp/issues/156 is fixed
OPENWISP_NETWORK_TOPOLOGY_API_AUTH_REQUIRED = False

DJANGO_X509_DEFAULT_CERT_VALIDITY = int(os.environ['DJANGO_X509_DEFAULT_CERT_VALIDITY'])
DJANGO_X509_DEFAULT_CA_VALIDITY = int(os.environ['DJANGO_X509_DEFAULT_CA_VALIDITY'])
