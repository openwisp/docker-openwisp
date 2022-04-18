INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'django.contrib.humanize',
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
    # openwisp radius
    'openwisp_radius',
    # Admin theme required for the templates
    # stored in openwisp_utils/admin_theme
    'openwisp_utils.admin_theme',
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
    'dj_rest_auth',
    'dj_rest_auth.registration',
    # social login
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.google',
    # other packages
    'private_storage',
    'drf_yasg',
    'channels',
]

EXTENDED_APPS = [
    'django_x509',
    'django_loci',
]
