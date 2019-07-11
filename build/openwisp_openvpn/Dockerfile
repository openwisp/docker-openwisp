FROM kylemanna/openvpn:latest

RUN apk add --no-cache postgresql-client supervisor && \
    rm -rf /var/cache/apk/* /tmp/*
CMD ["sh", "init_command.sh"]

COPY ./common/init_command.sh \
    ./common/utils.sh \
    ./openwisp_openvpn/ ./

ENV MODULE_NAME=openvpn \
    DASHBOARD_APP_SERVICE=dashboard \
    DB_NAME=openwisp_db \
    DB_USER=admin \
    DB_PASS=admin \
    DB_HOST=postgres \
    DB_PORT=5432 \
    VPN_NAME=default \
    DEFAULT_ORG=default
