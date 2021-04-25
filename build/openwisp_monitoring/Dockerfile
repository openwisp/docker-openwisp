FROM openwisp/openwisp-base:latest

WORKDIR /opt/openwisp/

COPY ./openwisp_monitoring/urls.py \
    ./openwisp_monitoring/module_settings.py \
    /opt/openwisp/openwisp/

CMD ["bash", "init_command.sh"]

ARG MONITORING_APP_PORT=8005
ENV MODULE_NAME=monitoring \
    CONTAINER_PORT=$MONITORING_APP_PORT

EXPOSE $MONITORING_APP_PORT
