import os
import sys
import json

from openwisp.utils import env_bool, request_scheme

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
DEBUG = env_bool(os.environ['DEBUG_MODE'])

ALLOWED_HOSTS = [
    'localhost',
    os.environ['DASHBOARD_INTERNAL'],
    os.environ['CONTROLLER_INTERNAL'],
    os.environ['RADIUS_INTERNAL'],
    os.environ['TOPOLOGY_INTERNAL'],
] + os.environ['DJANGO_ALLOWED_HOSTS'].split(',')

AUTH_USER_MODEL = 'openwisp_users.User'
SITE_ID = 1
LOGIN_REDIRECT_URL = 'admin:index'
ACCOUNT_LOGOUT_REDIRECT_URL = LOGIN_REDIRECT_URL
ROOT_URLCONF = 'openwisp.urls'

# CORS
CORS_ORIGIN_WHITELIST = [
    f'{request_scheme()}://{os.environ["DASHBOARD_DOMAIN"]}',
    f'{request_scheme()}://{os.environ["CONTROLLER_DOMAIN"]}',
    f'{request_scheme()}://{os.environ["RADIUS_DOMAIN"]}',
    f'{request_scheme()}://{os.environ["TOPOLOGY_DOMAIN"]}',
] + os.environ['DJANGO_CORS_HOSTS'].split(',')

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'openwisp_utils.staticfiles.DependencyFinder',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'OPTIONS': {
            'loaders': [
                ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                    'openwisp_utils.loaders.DependencyLoader'
                ]),
            ],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

if 'MODULE_NAME' == 'dashboard':
    TEMPLATES[0]['OPTIONS']['context_processors'] \
        .append('openwisp_utils.admin_theme.context_processor.menu_items')

FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

WSGI_APPLICATION = 'openwisp.wsgi.application'
ASGI_APPLICATION = 'openwisp_controller.geo.channels.routing.channel_routing'

REDIS_HOST = os.environ['REDIS_HOST']
CELERY_BROKER_URL = 'redis://'+REDIS_HOST+':6379/1'

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases


DB_OPTIONS = {
    "sslmode": os.environ['DB_SSLMODE'],
    'sslkey': os.environ['DB_SSLKEY'],
    'sslcert': os.environ['DB_SSLCERT'],
    'sslrootcert': os.environ['DB_SSLROOTCERT']
}
DB_OPTIONS.update(json.loads(os.environ['DB_OPTIONS']))

DATABASES = {
    'default': {
        'ENGINE': os.environ['DB_ENGINE'],
        'NAME': os.environ['DB_NAME'],
        'USER': os.environ['DB_USER'],
        'PASSWORD': os.environ['DB_PASS'],
        'HOST': os.environ['DB_HOST'],
        'PORT': os.environ['DB_PORT'],
        'OPTIONS': DB_OPTIONS
    },
}

# Channels(Websocket)
# https://channels.readthedocs.io/en/latest/topics/channel_layers.html#configuration

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {'hosts': [(REDIS_HOST, 6379)]},
    },
}

# Cache
# https://docs.djangoproject.com/en/2.2/ref/settings/#caches

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://'+REDIS_HOST+':6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Leaflet Configurations
# https://django-leaflet.readthedocs.io/en/latest/templates.html#configuration

LEAFLET_CONFIG = {
    'DEFAULT_CENTER': [
        int(os.environ['DJANGO_LEAFET_CENTER_X_AXIS']),
        int(os.environ['DJANGO_LEAFET_CENTER_Y_AXIS']),
    ],
    'DEFAULT_ZOOM': int(os.environ['DJANGO_LEAFET_ZOOM']),
}

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = os.environ['DJANGO_LANGUAGE_CODE']
TIME_ZONE = os.environ['TZ']
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_ROOT = '%s/static' % BASE_DIR
MEDIA_ROOT = '%s/media' % BASE_DIR
STATIC_URL = '/static/'
MEDIA_URL = '/media/'

# Email Configurations

DEFAULT_FROM_EMAIL = os.environ['EMAIL_DJANGO_DEFAULT']
EMAIL_BACKEND = os.environ['EMAIL_BACKEND']
EMAIL_HOST = os.environ['EMAIL_HOST']
EMAIL_PORT = os.environ['EMAIL_HOST_PORT']
EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
EMAIL_USE_TLS = env_bool(os.environ['EMAIL_HOST_TLS'])

# Logging
# http://docs.djangoproject.com/en/dev/topics/logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'user_filter': {
            '()': 'openwisp.utils.HostFilter',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'formatters': {
        'verbose': {
            'format': ('\n[%(host)s] - %(levelname)s, time: [%(asctime)s],'
                       'process: %(process)d, thread: %(thread)d\n%(message)s')
        },
    },
    'handlers': {
        'console': {
            'level': os.environ['DJANGO_LOG_LEVEL'],
            'class': 'logging.StreamHandler',
            'filters': ['user_filter'],
            'formatter': 'verbose',
            'stream': sys.stdout,
        },
        'mail_admins': {
            'level': os.environ['DJANGO_LOG_LEVEL'],
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false', 'user_filter'],
        },
    },
    'root': {
        'level': os.environ['DJANGO_LOG_LEVEL'],
        'handlers': [
            'console',
            'mail_admins',
        ]
    },
}

# Sentry
# https://sentry.io/for/django/

if os.environ['DJANGO_SENTRY_DSN']:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    sentry_sdk.init(dsn=os.environ['DJANGO_SENTRY_DSN'],
                    integrations=[DjangoIntegration()])

try:
    from openwisp.module_settings import *
except ImportError:
    pass
