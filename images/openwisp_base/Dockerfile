FROM python:3.12-slim-bullseye AS system

# System requirements:
# 1. gettext: Required by envsubst used in scripts
# 2. openwisp-radius/weasyprint: libcairo2 libpangocairo-1.0
# 3. openwisp-monitoring: fping gdal-bin
# hadolint ignore=DL3008
RUN apt-get update && \
    apt-get install --yes --no-install-recommends \
    libcairo2 apt-utils libpangocairo-1.0-0 \
    gdal-bin gettext fping openssh-client && \
    rm -rf /var/lib/apt/lists/* /root/.cache/pip/* /tmp/*
# hadolint ignore=DL3008, DL3009
RUN apt-get update && \
    apt-get install --yes --no-install-recommends \
    libpq-dev libjpeg-dev libffi-dev python3-dev \
    python3-pip libxml2-dev libxslt1-dev zlib1g-dev g++ procps

RUN useradd --system --password '' --create-home --shell /bin/bash \
    --gid root --uid 1001 openwisp
USER openwisp:root

FROM system AS openwisp_python

ENV PATH="${PATH}:/home/openwisp/.local/bin"
ENV PYTHONPATH=/home/openwisp/.local/lib/python3.10/site-packages

RUN pip install --no-cache-dir --user --upgrade pip~=24.1.2 setuptools~=70.3.0 wheel~=0.43.0
# TODO: Remove when next version of openwisp-monitoring is released
ARG OPENWISP_MONITORING_SOURCE=https://github.com/openwisp/openwisp-monitoring/tarball/6a99044fb8ef3b0c6cbd7a17383482eef00f4c8d
# hadolint ignore=DL3013
RUN pip install --no-cache-dir --user --upgrade ${OPENWISP_MONITORING_SOURCE}
ARG OPENWISP_FIRMWARE_SOURCE=https://github.com/openwisp/openwisp-firmware-upgrader/tarball/1aa3e540800af4ff73263849af4a85414d4aea4b
# hadolint ignore=DL3013
RUN pip install --no-cache-dir --user --upgrade ${OPENWISP_FIRMWARE_SOURCE}
ARG OPENWISP_TOPOLOGY_SOURCE=https://github.com/openwisp/openwisp-network-topology/tarball/df8b92b27f1d696b57aa3dfde899e43a0f0be7c7
# hadolint ignore=DL3013
RUN pip install --no-cache-dir --user --upgrade ${OPENWISP_TOPOLOGY_SOURCE}
ARG OPENWISP_RADIUS_SOURCE=https://github.com/openwisp/openwisp-radius/tarball/f35da16efba9c4e77a597b8451ae310f8b989e77
# hadolint ignore=DL3013
RUN pip install --no-cache-dir --user --upgrade ${OPENWISP_RADIUS_SOURCE}

# here we try to install custom versions of the modules only if the
# supplied argument does not equal the default value, because
# otherwise these modules will have already been installed above
ARG OPENWISP_IPAM_SOURCE=default
# hadolint ignore=DL3013
RUN if [ "$OPENWISP_IPAM_SOURCE" != "default" ] ; then \
        pip install --no-cache-dir --user --upgrade ${OPENWISP_IPAM_SOURCE}; \
    fi
# TODO: Remove when next version of openwisp-controller is released
ARG OPENWISP_CONTROLLER_SOURCE=https://github.com/openwisp/openwisp-controller/tarball/a850fc6d977b6cc6e4134b1247da6a394a0b3fa2
# hadolint ignore=DL3013
RUN if [ "$OPENWISP_CONTROLLER_SOURCE" != "default" ] ; then \
        pip install --no-cache-dir --user --upgrade ${OPENWISP_CONTROLLER_SOURCE}; \
    fi
ARG OPENWISP_NOTIFICATION_SOURCE=default
# hadolint ignore=DL3013
RUN if [ "$OPENWISP_NOTIFICATION_SOURCE" != "default" ] ; then \
        pip install --no-cache-dir --user --upgrade ${OPENWISP_NOTIFICATION_SOURCE}; \
    fi
ARG OPENWISP_USERS_SOURCE=https://github.com/openwisp/openwisp-users/tarball/dcd828d46401ccba47cfa6e3141b8eef59ab9de6
# hadolint ignore=DL3013
RUN if [ "$OPENWISP_USERS_SOURCE" != "default" ] ; then \
        pip install --no-cache-dir --user --upgrade --force-reinstall ${OPENWISP_USERS_SOURCE}; \
    fi
# TODO: Remove when next version of openwisp-utils is released
ARG OPENWISP_UTILS_SOURCE="openwisp-utils[celery,rest] @ https://github.com/openwisp/openwisp-utils/tarball/14578495c9be77dbb963ef97a7c06387cc12df83"
# hadolint ignore=DL3013
RUN if [ "$OPENWISP_UTILS_SOURCE" != "default" ] ; then \
        pip install --no-cache-dir --user --upgrade --force-reinstall "${OPENWISP_UTILS_SOURCE}"; \
    fi
ARG DJANGO_X509_SOURCE=default
# hadolint ignore=DL3013
RUN if [ "$DJANGO_X509_SOURCE" != "default" ]; then \
        pip install --no-cache-dir --user --upgrade --force-reinstall ${DJANGO_X509_SOURCE}; \
    fi

ARG DJANGO_SOURCE=django~=4.2.0
# hadolint ignore=DL3013
RUN pip install --no-cache-dir --user --upgrade ${DJANGO_SOURCE}

COPY ./openwisp_base/requirements.txt /tmp/openwisp-deploy-requirements.txt
RUN pip install --no-cache-dir --user --upgrade -r /tmp/openwisp-deploy-requirements.txt && \
    pip install --no-cache-dir --upgrade urllib3~=2.2.1

FROM system

COPY --from=openwisp_python --chown=openwisp:root /home/openwisp/.local/ /usr/local
COPY --chown=openwisp:root ./common/ /opt/openwisp/
RUN mkdir /opt/openwisp/static && \
    mkdir /opt/openwisp/media && \
    mkdir /opt/openwisp/private && \
    mkdir /opt/openwisp/logs && \
    mkdir /home/openwisp/.ssh && \
    chown -R openwisp:root /opt/openwisp && \
    chown -R openwisp:root /home/openwisp/.ssh
# Maintain backward compatibility with code written for ansible-openwisp2
RUN ln -s /opt/openwisp/openwisp /opt/openwisp/openwisp2

ENV DASHBOARD_APP_SERVICE=dashboard \
    PYTHONUNBUFFERED=1 \
    TZ=UTC \
    DEBUG_MODE=False \
    REDIS_HOST=redis \
    REDIS_PORT=6379 \
    REDIS_PASS= \
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
    INFLUXDB_DEFAULT_RETENTION_POLICY=26280h0m0s \
    EMAIL_BACKEND=djcelery_email.backends.CeleryEmailBackend \
    EMAIL_HOST=postfix \
    EMAIL_HOST_PORT=25 \
    EMAIL_HOST_USER="" \
    EMAIL_HOST_PASSWORD="" \
    EMAIL_HOST_TLS=False \
    EMAIL_TIMEOUT=10 \
    EMAIL_DJANGO_DEFAULT=example@example.org \
    DJANGO_LOG_LEVEL=ERROR \
    DJANGO_LANGUAGE_CODE=en-gb \
    OPENWISP_RADIUS_FREERADIUS_ALLOWED_HOSTS=172.18.0.0/16 \
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
    # SSH Credentials Configurations
    SSH_PRIVATE_KEY_PATH=/home/openwisp/.ssh/id_ed25519 \
    SSH_PUBLIC_KEY_PATH=/home/openwisp/.ssh/id_ed25519.pub \
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
    USE_OPENWISP_CELERY_TASK_ROUTES_DEFAULTS=True \
    # Celery-beat Configurations
    CRON_DELETE_OLD_RADACCT=365 \
    CRON_DELETE_OLD_POSTAUTH=365 \
    CRON_CLEANUP_STALE_RADACCT=365 \
    CRON_DELETE_OLD_RADIUSBATCH_USERS=12 \
    METRIC_COLLECTION=True
