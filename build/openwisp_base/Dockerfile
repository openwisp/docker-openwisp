FROM python:3.7.5-slim-buster AS SYSTEM

# System requirements:
# 1. Pillow: zlib1g-dev libjpeg-dev
# 2. gettext: Required by envsubst used in scripts
# 3. django-freeradius/weasyprint: libcairo2 libpangocairo-1.0
RUN apt update && \
    apt install --yes --no-install-recommends zlib1g-dev libjpeg-dev \
                libcairo2 libpangocairo-1.0 gdal-bin gettext && \
    rm -rf /var/lib/apt/lists/* /root/.cache/pip/* /tmp/*

FROM SYSTEM AS PYTHON

# Build requirements:
# 1. Twisted: gcc
# 2. Postgresql: libpq-dev
RUN apt update && \
    apt install --yes --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/* /root/.cache/pip/* /tmp/*

ENV PYTHONPATH=/install/lib/python3.7/site-packages
# Python Packages
RUN pip install https://github.com/openwisp/openwisp-controller/tarball/74600dc85f3ff0d4383c96c54bc00db122292a22 \
                --upgrade --prefix='/install'
RUN pip install https://github.com/openwisp/openwisp-network-topology/tarball/417ebec33ee38885501d0915cb7e37a415ed413d \
                --upgrade --prefix='/install'
RUN pip install https://github.com/openwisp/django-freeradius/tarball/4fbf6ca98cea726d22dae54a0684c9468fc752a1 \
                --upgrade --prefix='/install'
RUN pip install https://github.com/openwisp/openwisp-radius/tarball/af89345626076e27c81168c20daaa98f922223a0 \
                --upgrade --prefix='/install'
RUN pip install https://github.com/openwisp/django-netjsonconfig/tarball/ce0a694f1917f8c65baf0b88bb4f8ed014a577a9 \
                --upgrade --prefix='/install'
RUN pip install https://github.com/openwisp/django-netjsongraph/tarball/e18e5245724e58f0ef5310f0c57ba5347b8e32e7 \
                --upgrade --prefix='/install'
RUN pip install --prefix='/install' --upgrade openwisp-users~=0.1
RUN pip install --prefix='/install' --upgrade django-x509~=0.5
RUN pip install --prefix='/install' --upgrade openwisp-utils~=0.3
RUN pip install --prefix='/install' asgi_redis service_identity django-redis psycopg2 uwsgi sentry-sdk \
                                    supervisor celery django-celery-beat redis==2.10.6

FROM SYSTEM

COPY --from=PYTHON /install /usr/local
COPY ./common/ /opt/openwisp/

ENV DASHBOARD_APP_SERVICE=dashboard \
    PYTHONUNBUFFERED=1 \
    TZ=UTC \
    SET_RADIUS_TASKS=True \
    SET_TOPOLOGY_TASKS=True \
    DEBUG_MODE=False \
    REDIS_HOST=redis \
    DB_ENGINE=django.contrib.gis.db.backends.postgis \
    DB_NAME=openwisp_db \
    DB_USER=admin \
    DB_PASS=admin \
    DB_HOST=postgres \
    DB_PORT=5432 \
    DB_OPTIONS={} \
    EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend \
    EMAIL_HOST=postfix \
    EMAIL_HOST_PORT=25 \
    EMAIL_HOST_USER="" \
    EMAIL_HOST_PASSWORD="" \
    EMAIL_HOST_TLS=False \
    EMAIL_DJANGO_DEFAULT=example@example.org \
    DJANGO_LOG_LEVEL=ERROR \
    DJANGO_LANGUAGE_CODE=en-gb \
    DJANGO_ALLOWED_HOSTS=* \
    DJANGO_X509_DEFAULT_CERT_VALIDITY=1825 \
    DJANGO_X509_DEFAULT_CA_VALIDITY=3650 \
    DJANGO_SECRET_KEY=DEFAULT_BAD_KEY \
    DJANGO_CORS_ORIGIN_ALLOW_ALL=True \
    DJANGO_SENTRY_DSN="" \
    DJANGO_LEAFET_CENTER_X_AXIS=0 \
    DJANGO_LEAFET_CENTER_Y_AXIS=0 \
    DJANGO_LEAFET_ZOOM=1 \
    DASHBOARD_APP_PORT=8000 \
    CONTROLLER_APP_PORT=8001 \
    RADIUS_APP_PORT=8002 \
    TOPOLOGY_APP_PORT=8003 \
    WEBSOCKET_APP_PORT=8004 \
    # Radius Settings
    FREERADIUS_ORGANIZATION=default \
    DASHBOARD_URI=http://dashboard-internal \
    # VPN Configurations
    VPN_NAME=default \
    VPN_ORG=default \
    VPN_CLIENT_NAME="Default Management Vpn" \
    X509_NAME_CA=default \
    X509_NAME_CERT=default \
    X509_COUNTRY_CODE=IN \
    X509_STATE=Delhi \
    X509_CITY="New Delhi" \
    X509_ORGANIZATION_NAME=OpenWISP \
    X509_ORGANIZATION_UNIT_NAME=OpenWISP \
    X509_EMAIL=certificate@example.com \
    X509_COMMON_NAME=OpenWISP \
    # Celery-beat cron Configurations
    CRON_DELETE_OLD_RADACCT=365 \
    CRON_DELETE_OLD_POSTAUTH=365 \
    CRON_CLEANUP_STALE_RADACCT=365 \
    CRON_DELETE_OLD_USERS=12
