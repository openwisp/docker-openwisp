FROM openwisp/openwisp-base:latest

WORKDIR /opt/openwisp/

COPY ./openwisp_radius/urls.py \
    ./openwisp_radius/module_settings.py \
    /opt/openwisp/openwisp/

CMD ["bash", "init_command.sh"]

ARG RADIUS_APP_PORT=8002
ENV MODULE_NAME=radius \
    CONTAINER_PORT=$RADIUS_APP_PORT

EXPOSE $RADIUS_APP_PORT
