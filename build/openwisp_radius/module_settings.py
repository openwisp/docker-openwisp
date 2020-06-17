INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # all-auth
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'corsheaders',
    'openwisp_users',
    # rest framework
    'rest_framework',
    'django_filters',
    # registration
    'rest_framework.authtoken',
    'rest_auth',
    'rest_auth.registration',
    # social login
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.google',
    # openwisp radius
    'openwisp_radius',
]

# Swapper model definitions
OPENWISP_RADIUS_RADIUSREPLY_MODEL = 'openwisp_radius.RadiusReply'
OPENWISP_RADIUS_RADIUSGROUPREPLY_MODEL = 'openwisp_radius.RadiusGroupReply'
OPENWISP_RADIUS_RADIUSCHECK_MODEL = 'openwisp_radius.RadiusCheck'
OPENWISP_RADIUS_RADIUSGROUPCHECK_MODEL = 'openwisp_radius.RadiusGroupCheck'
OPENWISP_RADIUS_RADIUSACCOUNTING_MODEL = 'openwisp_radius.RadiusAccounting'
OPENWISP_RADIUS_NAS_MODEL = 'openwisp_radius.Nas'
OPENWISP_RADIUS_RADIUSUSERGROUP_MODEL = 'openwisp_radius.RadiusUserGroup'
OPENWISP_RADIUS_RADIUSPOSTAUTH_MODEL = 'openwisp_radius.RadiusPostAuth'
OPENWISP_RADIUS_RADIUSBATCH_MODEL = 'openwisp_radius.RadiusBatch'
OPENWISP_RADIUS_RADIUSGROUP_MODEL = 'openwisp_radius.RadiusGroup'
OPENWISP_RADIUS_RADIUSTOKEN_MODEL = 'openwisp_radius.RadiusToken'
OPENWISP_RADIUS_EXTRA_NAS_TYPES = (('cisco', 'Cisco Router'),)

SOCIALACCOUNT_PROVIDERS = {
    'facebook': {
        'METHOD': 'oauth2',
        'SCOPE': ['email', 'public_profile'],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        'INIT_PARAMS': {'cookie': True},
        'FIELDS': ['id', 'email', 'name', 'first_name', 'last_name', 'verified'],
        'VERIFIED_EMAIL': True,
    },
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    },
}
