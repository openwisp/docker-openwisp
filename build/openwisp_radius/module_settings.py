INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # openwisp admin theme
    'openwisp_utils.admin_theme',
    # all-auth
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'corsheaders',
    'openwisp_users',
    # admin
    'django.contrib.admin',
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

EXTENDED_APPS = ['django_freeradius']

# Swapper model definitions
DJANGO_FREERADIUS_RADIUSREPLY_MODEL = 'openwisp_radius.RadiusReply'
DJANGO_FREERADIUS_RADIUSGROUPREPLY_MODEL = 'openwisp_radius.RadiusGroupReply'
DJANGO_FREERADIUS_RADIUSCHECK_MODEL = 'openwisp_radius.RadiusCheck'
DJANGO_FREERADIUS_RADIUSGROUPCHECK_MODEL = 'openwisp_radius.RadiusGroupCheck'
DJANGO_FREERADIUS_RADIUSACCOUNTING_MODEL = 'openwisp_radius.RadiusAccounting'
DJANGO_FREERADIUS_NAS_MODEL = 'openwisp_radius.Nas'
DJANGO_FREERADIUS_RADIUSUSERGROUP_MODEL = 'openwisp_radius.RadiusUserGroup'
DJANGO_FREERADIUS_RADIUSPOSTAUTH_MODEL = 'openwisp_radius.RadiusPostAuth'
DJANGO_FREERADIUS_RADIUSBATCH_MODEL = 'openwisp_radius.RadiusBatch'
DJANGO_FREERADIUS_RADIUSGROUP_MODEL = 'openwisp_radius.RadiusGroup'
DJANGO_FREERADIUS_RADIUSTOKEN_MODEL = 'openwisp_radius.RadiusToken'

SOCIALACCOUNT_PROVIDERS = {
    'facebook': {
        'METHOD': 'oauth2',
        'SCOPE': ['email', 'public_profile'],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        'INIT_PARAMS': {'cookie': True},
        'FIELDS': [
            'id',
            'email',
            'name',
            'first_name',
            'last_name',
            'verified',
        ],
        'VERIFIED_EMAIL': True,
    },
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}

DJANGO_FREERADIUS_EXTRA_NAS_TYPES = (
    ('cisco', 'Cisco Router'),
)
