FROM openwisp/openwisp-base:latest

WORKDIR /opt/openwisp/

COPY --chown=openwisp:root ./openwisp_api/urls.py \
    ./openwisp_api/module_settings.py \
    /opt/openwisp/openwisp/

CMD ["bash", "init_command.sh"]

ARG API_APP_PORT=8001
ENV MODULE_NAME=api \
    CONTAINER_PORT=$API_APP_PORT \
    DASHBOARD_APP_PORT=8000

EXPOSE $API_APP_PORT
