FROM nginx:1.27.4-alpine

RUN apk add --update --no-cache \
            openssl~=3.3.3-r0 \
            py3-pip~=24.3.1-r0 \
            certbot~=3.0.1-r0 \
            certbot-nginx~=3.0.1-r0 && \
    rm -rf /var/cache/apk/* /tmp/*

WORKDIR /etc/nginx/
CMD ["sh", "init_command.sh"]
EXPOSE 80 443

# DL3018
COPY ./common/services.py \
    ./common/init_command.sh \
    ./common/utils.sh \
    ./openwisp_nginx/ \
    /etc/nginx/

RUN pip install --break-system-packages --no-cache-dir -r requirements.txt

ENV MODULE_NAME=nginx \
    PYTHONUNBUFFERED=1 \
    DOLLAR=$ \
    TZ=UTC \
    SSL_CERT_MODE=Yes \
    CERT_ADMIN_EMAIL=example@example.com \
    NGINX_HTTP2=http2 \
    NGINX_CLIENT_BODY_SIZE=30 \
    NGINX_ADMIN_ALLOW_NETWORK=all \
    NGINX_HTTPS_ALLOWED_IPS=all \
    NGINX_HTTP_ALLOW=False \
    NGINX_SERVER_NAME_HASH_BUCKET=32 \
    NGINX_SSL_CONFIG='' \
    NGINX_IP6_STRING='' \
    NGINX_IP6_80_STRING='' \
    NGINX_80_CONFIG='' \
    NGINX_GZIP_SWITCH=on \
    NGINX_GZIP_LEVEL=6 \
    NGINX_GZIP_PROXIED=any \
    NGINX_GZIP_MIN_LENGTH=1000 \
    NGINX_GZIP_TYPES='text/plain image/svg+xml application/json application/javascript text/xml text/css application/xml application/x-font-ttf font/opentype' \
    NGINX_CUSTOM_FILE=False \
    NINGX_REAL_REMOTE_ADDR='$real_ip' \
    # USWGI pass_port
    DASHBOARD_APP_PORT=8000 \
    API_APP_PORT=8001 \
    WEBSOCKET_APP_PORT=8002 \
    # Application Service Name
    DASHBOARD_APP_SERVICE=dashboard \
    API_APP_SERVICE=api \
    WEBSOCKET_APP_SERVICE=websocket \
    # Listen domains
    DASHBOARD_DOMAIN=dashboard.example.com \
    API_DOMAIN=api.example.com \
    # Inter container communication domains
    DASHBOARD_INTERNAL=dashboard.internal \
    API_INTERNAL=api.internal
