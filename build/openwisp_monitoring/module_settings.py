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
    'django_filters',
    # openwisp2 modules
    'openwisp_controller.config',
    'openwisp_controller.connection',
    'openwisp_controller.pki',
    'openwisp_controller.geo',
    'openwisp_users',
    # monitoring
    'openwisp_monitoring.monitoring',
    'openwisp_monitoring.device',
    'openwisp_monitoring.check',
    'nested_admin',
    'openwisp_notifications',
    # admin
    # openwisp2 admin theme
    # (must be loaded here)
    'openwisp_utils.admin_theme',
    'django.contrib.admin',
    'django.forms',
    # other dependencies
    'sortedm2m',
    'reversion',
    'leaflet',
    'flat_json_widget',
    # rest framework
    'rest_framework',
    'rest_framework_gis',
    'drf_yasg',
    # channels
    'channels',
]

EXTENDED_APPS = ['django_x509', 'django_loci']
