FROM python:3.7.9-slim-buster AS SYSTEM

# System requirements:
# 1. Pillow: zlib1g-dev libjpeg-dev
# 2. gettext: Required by envsubst used in scripts
# 3. openwisp-radius/weasyprint: libcairo2 libpangocairo-1.0
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
ARG OPENWISP_FIRMWARE_SOURCE=https://github.com/openwisp/openwisp-firmware-upgrader/tarball/docker-openwisp-usage
RUN pip install --prefix='/install' --upgrade --force-reinstall ${OPENWISP_FIRMWARE_SOURCE}
ARG OPENWISP_CONTROLLER_SOURCE=openwisp-controller~=0.8.4
RUN pip install --prefix='/install' --upgrade --force-reinstall ${OPENWISP_CONTROLLER_SOURCE}
ARG OPENWISP_NOTIFICATION_SOURCE=openwisp-notifications~=0.3.0
RUN pip install --prefix='/install' --upgrade --force-reinstall ${OPENWISP_NOTIFICATION_SOURCE}
ARG OPENWISP_TOPOLOGY_SOURCE=openwisp-network-topology~=0.5.1
RUN pip install --prefix='/install' --upgrade --force-reinstall ${OPENWISP_TOPOLOGY_SOURCE}
ARG OPENWISP_RADIUS_SOURCE=https://github.com/openwisp/openwisp-radius/tarball/docker-openwisp-usage
RUN pip install --prefix='/install' --upgrade --force-reinstall ${OPENWISP_RADIUS_SOURCE}
ARG OPENWISP_USERS_SOURCE=https://github.com/openwisp/openwisp-users/tarball/docker-openwisp-usage
RUN pip install --prefix='/install' --upgrade --force-reinstall ${OPENWISP_USERS_SOURCE}
ARG DJANGO_X509_SOURCE=django-x509~=0.9.2
RUN pip install --prefix='/install' --upgrade --force-reinstall ${DJANGO_X509_SOURCE}
ARG OPENWISP_UTILS_SOURCE=openwisp-utils~=0.7.2
RUN pip install --prefix='/install' --upgrade --force-reinstall ${OPENWISP_UTILS_SOURCE}
RUN pip install --prefix='/install' channels_redis service_identity django-redis psycopg2 \
                                    uwsgi sentry-sdk supervisor celery django-celery-beat \
                                    django-cors-headers django-rest-auth jinja2~=2.11
ARG DJANGO_SOURCE=django==3.1
RUN pip install --prefix='/install' --upgrade --force-reinstall ${DJANGO_SOURCE}

FROM SYSTEM

COPY --from=PYTHON /install /usr/local
COPY ./common/ /opt/openwisp/

ENV DASHBOARD_APP_SERVICE=dashboard \
    PYTHONUNBUFFERED=1 \
    TZ=UTC \
    DEBUG_MODE=False \
    REDIS_HOST=redis \
    DB_ENGINE=django.contrib.gis.db.backends.postgis \
    DB_NAME=openwisp_db \
    DB_USER=admin \
    DB_PASS=admin \
    DB_HOST=postgres \
    DB_PORT=5432 \
    DB_SSLMODE=disable \
    DB_SSLKEY=None \
    DB_SSLCERT=None \
    DB_SSLROOTCERT=None \
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
    DJANGO_FREERADIUS_ALLOWED_HOSTS=172.18.0.0/16 \
    DJANGO_X509_DEFAULT_CERT_VALIDITY=1825 \
    DJANGO_X509_DEFAULT_CA_VALIDITY=3650 \
    DJANGO_SECRET_KEY=DEFAULT_BAD_KEY \
    DJANGO_CORS_HOSTS=http://localhost \
    DJANGO_SENTRY_DSN="" \
    DJANGO_LEAFET_CENTER_X_AXIS=0 \
    DJANGO_LEAFET_CENTER_Y_AXIS=0 \
    DJANGO_LEAFET_ZOOM=1 \
    # Common Nginx configurations
    NGINX_CLIENT_BODY_SIZE=30 \
    DASHBOARD_APP_PORT=8000 \
    API_APP_PORT=8001 \
    RADIUS_APP_PORT=8002 \
    WEBSOCKET_APP_PORT=8003 \
    DASHBOARD_INTERNAL=dashboard.internal \
    API_INTERNAL=api.internal \
    RADIUS_INTERNAL=radius.internal \
    # VPN Configurations
    VPN_DOMAIN=openvpn.example.com \
    VPN_NAME=default \
    VPN_ORG=default \
    VPN_CLIENT_NAME=default-management-vpn \
    X509_NAME_CA=default \
    X509_NAME_CERT=default \
    X509_COUNTRY_CODE=IN \
    X509_STATE=Delhi \
    X509_CITY="New Delhi" \
    X509_ORGANIZATION_NAME=OpenWISP \
    X509_ORGANIZATION_UNIT_NAME=OpenWISP \
    X509_EMAIL=certificate@example.com \
    X509_COMMON_NAME=OpenWISP \
    # Modules Enabled
    USE_OPENWISP_RADIUS=True \
    USE_OPENWISP_TOPOLOGY=True \
    USE_OPENWISP_FIRMWARE=True \
    # Celery-beat Configurations
    CRON_DELETE_OLD_RADACCT=365 \
    CRON_DELETE_OLD_POSTAUTH=365 \
    CRON_CLEANUP_STALE_RADACCT=365 \
    CRON_DELETE_OLD_USERS=12
