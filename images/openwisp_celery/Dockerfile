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

USER root:root
RUN apt install --yes --no-install-recommends \
        iproute2 iptables sudo iputils-ping
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

CMD ["bash", "init_command.sh"]

ARG DASHBOARD_APP_PORT=8000
ENV MODULE_NAME=celery \
    CONTAINER_PORT=$DASHBOARD_APP_PORT
