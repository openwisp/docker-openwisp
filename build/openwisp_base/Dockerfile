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

ARG OPENWISP_CONTROLLER_SOURCE=openwisp-controller
ARG OPENWISP_TOPOLOGY_SOURCE=openwisp-network-topology
ARG DJANGO_FREERADIUS_SOURCE=django-freeradius
ARG OPENWISP_RADIUS_SOURCE=openwisp-radius
ARG OPENWISP_USERS_SOURCE=openwisp-users
ARG DJANGO_NETJSONCONFIG_SOURCE=openwisp-users
ARG DJANGO_NETJSONGRAPH_SOURCE=django-netjsongraph
ARG DJANGO_X509_SOURCE=django-x509
ARG OPENWISP_UTILS_SOURCE=openwisp-utils

ENV PYTHONPATH=/install/lib/python3.7/site-packages
# Python Packages
RUN pip install --upgrade --prefix='/install' ${OPENWISP_CONTROLLER_SOURCE}
RUN pip install --upgrade --prefix='/install' ${OPENWISP_TOPOLOGY_SOURCE}
RUN pip install --upgrade --prefix='/install' ${DJANGO_FREERADIUS_SOURCE}
RUN pip install --upgrade --prefix='/install' ${OPENWISP_RADIUS_SOURCE}
RUN pip install --upgrade --prefix='/install' ${OPENWISP_USERS_SOURCE}
RUN pip install --upgrade --prefix='/install' ${DJANGO_NETJSONCONFIG_SOURCE}
RUN pip install --upgrade --prefix='/install' ${DJANGO_NETJSONGRAPH_SOURCE}
RUN pip install --upgrade --prefix='/install' ${DJANGO_X509_SOURCE}
RUN pip install --upgrade --prefix='/install' ${OPENWISP_UTILS_SOURCE}
RUN pip install asgi_redis service_identity django-redis psycopg2 uwsgi sentry-sdk \
                supervisor celery django-celery-beat redis==2.10.6 \
                --prefix='/install'

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
