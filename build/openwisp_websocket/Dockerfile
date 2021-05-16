FROM openwisp/openwisp-base:latest

WORKDIR /opt/openwisp/

COPY ./common/ \
    ./openwisp_websocket/daphne.conf \
    /opt/openwisp/
COPY ./openwisp_websocket/module_settings.py \
    ./openwisp_websocket/urls.py \
    /opt/openwisp/openwisp/

ARG WEBSOCKET_APP_PORT=8003
ENV MODULE_NAME=websocket \
    DJANGO_WEBSOCKET_HOST=0.0.0.0 \
    CONTAINER_PORT=$WEBSOCKET_APP_PORT

EXPOSE $WEBSOCKET_APP_PORT
CMD ["supervisord", "--nodaemon", "--configuration", "daphne.conf"]
