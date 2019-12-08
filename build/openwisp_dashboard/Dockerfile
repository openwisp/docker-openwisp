FROM openwisp/openwisp-base:latest

WORKDIR /opt/openwisp/

# Location: /opt/openwisp/
COPY ./openwisp_dashboard/load_init_data.py \
    ./openwisp_dashboard/openvpn.json \
    /opt/openwisp/
# Location: /opt/openwisp/openwisp/
COPY ./openwisp_controller/module_settings.py /opt/openwisp/openwisp/controller_settings.py
COPY ./openwisp_topology/module_settings.py /opt/openwisp/openwisp/topology_settings.py
COPY ./openwisp_radius/module_settings.py /opt/openwisp/openwisp/radius_settings.py
COPY ./openwisp_dashboard/module_settings.py \
    ./openwisp_dashboard/urls.py \
    /opt/openwisp/openwisp/

CMD ["bash", "init_command.sh"]

ARG DASHBOARD_APP_PORT=8000
ARG WEBSOCKET_APP_PORT=8004
ENV MODULE_NAME=dashboard \
    CONTAINER_PORT=$DASHBOARD_APP_PORT

EXPOSE $DASHBOARD_APP_PORT $WEBSOCKET_APP_PORT 25
