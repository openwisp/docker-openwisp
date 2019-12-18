FROM openwisp/openwisp-base:latest

WORKDIR /opt/openwisp/

COPY ./openwisp_topology/urls.py \
    ./openwisp_topology/module_settings.py \
    /opt/openwisp/openwisp/

CMD ["bash", "init_command.sh"]

ARG TOPOLOGY_APP_PORT=8003
ENV MODULE_NAME=topology \
    CONTAINER_PORT=$TOPOLOGY_APP_PORT \
    DASHBOARD_APP_SERVICE=dashboard

EXPOSE $TOPOLOGY_APP_PORT
