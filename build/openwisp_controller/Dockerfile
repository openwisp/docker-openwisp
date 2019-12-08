FROM openwisp/openwisp-base:latest

WORKDIR /opt/openwisp/

COPY ./openwisp_controller/urls.py \
    ./openwisp_controller/module_settings.py \
    /opt/openwisp/openwisp/

CMD ["bash", "init_command.sh"]

ARG CONTROLLER_APP_PORT=8001
ENV MODULE_NAME=controller \
    CONTAINER_PORT=$CONTROLLER_APP_PORT \
    DASHBOARD_APP_PORT=8000

EXPOSE $CONTROLLER_APP_PORT
