FROM nginx:alpine

RUN apk add --update --no-cache certbot openssl && \
    rm -rf /var/cache/apk/* /tmp/*

WORKDIR /etc/nginx/
CMD ["sh", "init_command.sh"]
EXPOSE 80 443

COPY ./common/services.py \
    ./common/init_command.sh \
    ./common/utils.sh \
    ./openwisp_nginx/ \
    /etc/nginx/

ENV MODULE_NAME=nginx \
    PYTHONUNBUFFERED=1 \
    DOLLAR=$ \
    TZ=UTC \
    SSL_CERT_MODE=True \
    CERT_ADMIN_EMAIL=example@example.com \
    NGINX_CLIENT_BODY_SIZE=5M \
    NGINX_ADMIN_ALLOW_NETWORK=all \
    NGINX_HTTPS_ALLOWED_IPS=all \
    NGINX_HTTP_ALLOW=False \
    NGINX_SERVER_NAME_HASH_BUCKET=32 \
    NGINX_SSL_CONFIG='' \
    NGINX_80_CONFIG='' \
    NGINX_GZIP_SWITCH=off \
    NGINX_GZIP_LEVEL=6 \
    NGINX_GZIP_PROXIED=any \
    NGINX_GZIP_MIN_LENGTH=1000 \
    NGINX_GZIP_TYPES=* \
    NGINX_CUSTOM_FILE=False \
    NINGX_REAL_REMOTE_ADDR='$http_x_forwarded_for' \
    # USWGI pass_port
    DASHBOARD_APP_PORT=8000 \
    CONTROLLER_APP_PORT=8001 \
    RADIUS_APP_PORT=8002 \
    TOPOLOGY_APP_PORT=8003 \
    WEBSOCKET_APP_PORT=8004 \
    # Application Service Name
    DASHBOARD_APP_SERVICE=dashboard \
    CONTROLLER_APP_SERVICE=controller \
    RADIUS_APP_SERVICE=radius \
    TOPOLOGY_APP_SERVICE=topology \
    WEBSOCKET_APP_SERVICE=daphne \
    # Listen domains
    DASHBOARD_DOMAIN=dashboard.example.com \
    CONTROLLER_DOMAIN=controller.example.com \
    RADIUS_DOMAIN=radius.example.com \
    TOPOLOGY_DOMAIN=topology.example.com
