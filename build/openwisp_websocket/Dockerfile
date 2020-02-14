FROM openwisp/openwisp-base:latest

WORKDIR /opt/openwisp/

COPY ./common/ \
    ./openwisp_websocket/daphne.conf \
    /opt/openwisp/
COPY ./openwisp_websocket/module_settings.py \
    ./openwisp_websocket/urls.py \
    /opt/openwisp/openwisp/

ARG WEBSOCKET_APP_PORT=8004
ENV MODULE_NAME=websocket \
    CONTAINER_PORT=$WEBSOCKET_APP_PORT

EXPOSE $WEBSOCKET_APP_PORT
CMD ["supervisord", "--nodaemon", "--configuration", "daphne.conf"]
