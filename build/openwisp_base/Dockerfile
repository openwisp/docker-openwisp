FROM python:3.10-slim-bullseye AS SYSTEM

# System requirements:
# 1. gettext: Required by envsubst used in scripts
# 2. openwisp-radius/weasyprint: libcairo2 libpangocairo-1.0
# 3. openwisp-monitoring: fping gdal-bin
# 4. sudo
RUN apt update && \
    apt install --yes --no-install-recommends \
                libcairo2 apt-utils libpangocairo-1.0-0 \
                gdal-bin gettext fping && \
    rm -rf /var/lib/apt/lists/* /root/.cache/pip/* /tmp/*

RUN apt update && \
    apt install --yes --no-install-recommends \
                gcc libpq-dev libjpeg-dev libffi-dev python3-dev \
                python3-pip libxml2-dev libxslt1-dev zlib1g-dev g++

RUN useradd --system --password '' --create-home --shell /bin/bash \
   --gid root --uid 1001 openwisp
USER openwisp:root

FROM SYSTEM AS PYTHON

ENV PATH="${PATH}:/home/openwisp/.local/bin"
ENV PYTHONPATH=/home/openwisp/.local/lib/python3.10/site-packages

RUN pip install --user --upgrade pip
ARG OPENWISP_MONITORING_SOURCE=https://github.com/openwisp/openwisp-monitoring/tarball/docker-openwisp-usage
RUN pip install --user --upgrade ${OPENWISP_MONITORING_SOURCE}
ARG OPENWISP_FIRMWARE_SOURCE=https://github.com/openwisp/openwisp-firmware-upgrader/tarball/docker-openwisp-usage
RUN pip install --user --upgrade ${OPENWISP_FIRMWARE_SOURCE}
ARG OPENWISP_TOPOLOGY_SOURCE=https://github.com/openwisp/openwisp-network-topology/tarball/docker-openwisp-usage
RUN pip install --user --upgrade ${OPENWISP_TOPOLOGY_SOURCE}
ARG OPENWISP_RADIUS_SOURCE=https://github.com/openwisp/openwisp-radius/tarball/docker-openwisp-usage
RUN pip install --user --upgrade ${OPENWISP_RADIUS_SOURCE}

# here we try to install custom versions of the modules only if the
# supplied argument does not equal the default value, because
# otherwise these modules will have already been installed above
ARG OPENWISP_IPAM_SOURCE=default
RUN if [ "$OPENWISP_IPAM_SOURCE" != "default" ] ; then \
    pip install --user --upgrade ${OPENWISP_IPAM_SOURCE}; \
    fi
ARG OPENWISP_CONTROLLER_SOURCE=default
RUN if [ "$OPENWISP_CONTROLLER_SOURCE" != "default" ] ; then \
    pip install --user --upgrade ${OPENWISP_CONTROLLER_SOURCE}; \
    fi
ARG OPENWISP_NOTIFICATION_SOURCE=default
RUN if [ "$OPENWISP_NOTIFICATION_SOURCE" != "default" ] ; then \
    pip install --user --upgrade ${OPENWISP_NOTIFICATION_SOURCE}; \
    fi
ARG OPENWISP_USERS_SOURCE=default
RUN if [ "$OPENWISP_USERS_SOURCE" != "default" ] ; then \
    pip install --user --upgrade --force-reinstall ${OPENWISP_USERS_SOURCE}; \
    fi
ARG OPENWISP_UTILS_SOURCE=default
RUN if [ "$OPENWISP_UTILS_SOURCE" != "default" ] ; then \
    pip install --user --upgrade --force-reinstall ${OPENWISP_UTILS_SOURCE}; \
    fi
ARG DJANGO_X509_SOURCE=default
RUN if [ "$DJANGO_X509_SOURCE" != "default" ]; then \
    pip install --user --upgrade --force-reinstall ${DJANGO_X509_SOURCE}; \
    fi

ARG DJANGO_SOURCE=django~=4.0.0
RUN pip install --user --upgrade ${DJANGO_SOURCE}

RUN if [ "$EMAIL_BACKEND" = "djcelery_email.backends.CeleryEmailBackend" ]; then \
    pip install --prefix='/install' django-celery-email; \
    fi

COPY ./openwisp_base/requirements.txt /tmp/openwisp-deploy-requirements.txt
RUN pip install --user --upgrade -r /tmp/openwisp-deploy-requirements.txt

FROM SYSTEM

COPY --from=PYTHON --chown=openwisp:root /home/openwisp/.local/ /usr/local
COPY --chown=openwisp:root ./common/ /opt/openwisp/
RUN mkdir /opt/openwisp/static && mkdir /opt/openwisp/media && mkdir /opt/openwisp/logs && chown -R openwisp:root /opt/openwisp

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
    EMAIL_BACKEND=djcelery_email.backends.CeleryEmailBackend \
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
    WEBSOCKET_APP_PORT=8002 \
    DASHBOARD_INTERNAL=dashboard.internal \
    API_INTERNAL=api.internal \
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
