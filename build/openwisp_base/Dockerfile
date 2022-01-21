FROM python:3.10-slim-bullseye AS SYSTEM

# System requirements:
# 1. gettext: Required by envsubst used in scripts
# 2. openwisp-radius/weasyprint: libcairo2 libpangocairo-1.0
# 3. openwisp-monitoring: fping gdal-bin
RUN apt update && \
    apt install --yes --no-install-recommends libcairo2 libpangocairo-1.0-0 gdal-bin \
                                              gettext fping \
    && rm -rf /var/lib/apt/lists/* /root/.cache/pip/* /tmp/*

FROM SYSTEM AS PYTHON

RUN apt update && \
    apt install --yes --no-install-recommends gcc libpq-dev libjpeg-dev libffi-dev python3-dev \
                                              python3-pip libxml2-dev libxslt1-dev zlib1g-dev g++

ENV PYTHONPATH=/install/lib/python3.10/site-packages
# Python Packages
## TODO: We need to temporarily lock the version of pip to avoid using
## the new version of the dependency resolver which is not compatible
## with openwisp modules
RUN pip install --upgrade pip==20.2.4
ARG OPENWISP_MONITORING_SOURCE=https://github.com/openwisp/openwisp-monitoring/tarball/docker-openwisp-usage
RUN pip install --prefix='/install' --upgrade --force-reinstall ${OPENWISP_MONITORING_SOURCE}
ARG OPENWISP_FIRMWARE_SOURCE=https://github.com/openwisp/openwisp-firmware-upgrader/tarball/docker-openwisp-usage
RUN pip install --prefix='/install' --upgrade --force-reinstall ${OPENWISP_FIRMWARE_SOURCE}
ARG OPENWISP_CONTROLLER_SOURCE=https://github.com/openwisp/openwisp-controller/tarball/docker-openwisp-usage
RUN pip install --prefix='/install' --upgrade --force-reinstall ${OPENWISP_CONTROLLER_SOURCE}
ARG OPENWISP_NOTIFICATION_SOURCE=https://github.com/openwisp/openwisp-notifications/tarball/docker-openwisp-usage
RUN pip install --prefix='/install' --upgrade --force-reinstall ${OPENWISP_NOTIFICATION_SOURCE}
ARG OPENWISP_TOPOLOGY_SOURCE=https://github.com/openwisp/openwisp-network-topology/tarball/docker-openwisp-usage
RUN pip install --prefix='/install' --upgrade --force-reinstall ${OPENWISP_TOPOLOGY_SOURCE}
ARG OPENWISP_RADIUS_SOURCE=https://github.com/openwisp/openwisp-radius/tarball/docker-openwisp-usage
RUN pip install --prefix='/install' --upgrade --force-reinstall ${OPENWISP_RADIUS_SOURCE}
ARG OPENWISP_IPAM_SOURCE=https://github.com/openwisp/openwisp-ipam/tarball/docker-openwisp-usage
RUN pip install --prefix='/install' --upgrade --force-reinstall ${OPENWISP_IPAM_SOURCE}
ARG OPENWISP_USERS_SOURCE=https://github.com/openwisp/openwisp-users/tarball/docker-openwisp-usage
RUN pip install --prefix='/install' --upgrade --force-reinstall ${OPENWISP_USERS_SOURCE}
ARG DJANGO_X509_SOURCE=https://github.com/openwisp/django-x509/tarball/docker-openwisp-usage
RUN pip install --prefix='/install' --upgrade --force-reinstall ${DJANGO_X509_SOURCE}
ARG OPENWISP_UTILS_SOURCE=https://github.com/openwisp/openwisp-utils/tarball/docker-openwisp-usage
RUN pip install --prefix='/install' --upgrade --force-reinstall ${OPENWISP_UTILS_SOURCE}
RUN pip install --prefix='/install' channels_redis service_identity django-redis psycopg2 \
                                    uwsgi sentry-sdk supervisor celery django-celery-beat \
                                    django-cors-headers django-rest-auth jinja2
ARG DJANGO_SOURCE=django~=4.0.0
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
    INFLUXDB_USER=admin \
    INFLUXDB_PASS=admin \
    INFLUXDB_NAME=openwisp \
    INFLUXDB_HOST=influxdb \
    INFLUXDB_PORT=8086 \
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
    USE_OPENWISP_MONITORING=True \
    # Celery-beat Configurations
    CRON_DELETE_OLD_RADACCT=365 \
    CRON_DELETE_OLD_POSTAUTH=365 \
    CRON_CLEANUP_STALE_RADACCT=365 \
    CRON_DELETE_OLD_USERS=12
