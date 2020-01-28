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
    apt install --yes --no-install-recommends gcc libpq-dev

ENV PYTHONPATH=/install/lib/python3.7/site-packages
# Python Packages
ARG OPENWISP_CONTROLLER_SOURCE=openwisp-controller~=0.4.0
RUN pip install --upgrade --prefix='/install' ${OPENWISP_CONTROLLER_SOURCE}
ARG OPENWISP_TOPOLOGY_SOURCE=openwisp-network-topology~=0.2.0
RUN pip install --upgrade --prefix='/install' ${OPENWISP_TOPOLOGY_SOURCE}
ARG DJANGO_FREERADIUS_SOURCE=https://github.com/openwisp/django-freeradius/tarball/79f96a13e65bc95b81d41e643d4f8280bf357caa
RUN pip install --upgrade --prefix='/install' ${DJANGO_FREERADIUS_SOURCE}
ARG OPENWISP_RADIUS_SOURCE=https://github.com/openwisp/openwisp-radius/tarball/7150e28ffa985120accac1f47afbae9263c8c140
RUN pip install --upgrade --prefix='/install' ${OPENWISP_RADIUS_SOURCE}
ARG OPENWISP_USERS_SOURCE=openwisp-users~=0.1.0
RUN pip install --upgrade --prefix='/install' ${OPENWISP_USERS_SOURCE}
ARG DJANGO_NETJSONCONFIG_SOURCE=django-netjsonconfig~=0.9.0
RUN pip install --upgrade --prefix='/install' ${DJANGO_NETJSONCONFIG_SOURCE}
ARG DJANGO_NETJSONGRAPH_SOURCE=django-netjsongraph~=0.5.0
RUN pip install --upgrade --prefix='/install' ${DJANGO_NETJSONGRAPH_SOURCE}
ARG DJANGO_X509_SOURCE=django-x509~=0.5.0
RUN pip install --upgrade --prefix='/install' ${DJANGO_X509_SOURCE}
ARG OPENWISP_UTILS_SOURCE=openwisp-utils~=0.4.0
RUN pip install --upgrade --prefix='/install' ${OPENWISP_UTILS_SOURCE}
RUN pip install asgi_redis service_identity django-redis psycopg2 uwsgi sentry-sdk \
                supervisor celery django-celery-beat \
                --prefix='/install'
ARG DJANGO_SOURCE=django==2.1
RUN pip install --upgrade --prefix='/install' ${DJANGO_SOURCE}

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
