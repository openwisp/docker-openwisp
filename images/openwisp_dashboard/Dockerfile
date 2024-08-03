# hadolint ignore=DL3007
FROM openwisp/openwisp-base:latest
WORKDIR /opt/openwisp/

# Location: /opt/openwisp/
COPY --chown=openwisp:root ./openwisp_dashboard/load_init_data.py \
    ./openwisp_dashboard/openvpn.json \
    /opt/openwisp/
# Location: /opt/openwisp/openwisp/
COPY --chown=openwisp:root ./openwisp_dashboard/module_settings.py \
    ./openwisp_dashboard/urls.py \
    /opt/openwisp/openwisp/

CMD ["bash", "init_command.sh"]

ARG DASHBOARD_APP_PORT=8000
ENV MODULE_NAME=dashboard \
    OPENWISP_GEOCODING_CHECK=True \
    OPENWISP_CELERY_COMMAND_FLAGS=--concurrency=1 \
    USE_OPENWISP_CELERY_NETWORK=True \
    OPENWISP_CELERY_NETWORK_COMMAND_FLAGS=--concurrency=1 \
    USE_OPENWISP_CELERY_MONITORING=True \
    OPENWISP_CELERY_MONITORING_COMMAND_FLAGS=--concurrency=1 \
    OPENWISP_CELERY_MONITORING_CHECKS_COMMAND_FLAGS=--concurrency=1 \
    USE_OPENWISP_CELERY_FIRMWARE=True \
    OPENWISP_CELERY_FIRMWARE_COMMAND_FLAGS=--concurrency=1 \
    CONTAINER_PORT=$DASHBOARD_APP_PORT

EXPOSE $DASHBOARD_APP_PORT
