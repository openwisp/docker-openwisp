INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    # all-auth
    "django.contrib.sites",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    # openwisp modules
    "openwisp_users",
    # openwisp-controller
    "openwisp_controller.pki",
    "openwisp_controller.config",
    "openwisp_controller.geo",
    "openwisp_controller.connection",
    "openwisp_controller.subnet_division",
    "flat_json_widget",
    "openwisp_notifications",
    # openwisp-ipam
    "openwisp_ipam",
    # openwisp-network-topology
    "openwisp_network_topology",
    # openwisp-radius
    "dj_rest_auth",
    "dj_rest_auth.registration",
    "openwisp_radius",
    # admin
    "openwisp_utils.admin_theme",
    "django.contrib.admin",
    "django.forms",
    # other dependencies
    "sortedm2m",
    "reversion",
    "leaflet",
    # rest framework
    "rest_framework",
    "rest_framework_gis",
    "rest_framework.authtoken",
    "django_filters",
    # other packages
    "private_storage",
    "channels",
    "drf_yasg",
]

EXTENDED_APPS = [
    "django_x509",
    "django_loci",
]
