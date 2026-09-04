# No readily available Nginx image includes the Brotli static module.
# Build the module against nginx.org's nginx package used by this image.
# Alpine's nginx module packages target Alpine's own nginx build.
# PLEASE KEEP THIS LITERAL OR DEPENDABOT WILL NOT BE ABLE TO UPDATE IT.
FROM nginx:1.31.4-alpine AS brotli-builder

ARG NGX_BROTLI_COMMIT=25f86f0bac1101b6512135eac5f93c49c63609e3
ARG NGINX_ARUT_SIGNING_KEY_FINGERPRINT=43387825DDB1BB97EC36BA5D007C8D7C15D87369
ARG NGINX_PLUKNET_SIGNING_KEY_FINGERPRINT=D6786CE303D9A9022998DC6CC8464D549AF75C0A
ARG NGINX_SB_SIGNING_KEY_FINGERPRINT=7338973069ED3F443F4D37DFA64FD5B17ADB39A8
ARG NGINX_THRESH_SIGNING_KEY_FINGERPRINT=13C82A63B603576156E30A4EA0EA981B66B0D967

# hadolint ignore=DL3003,DL3018
RUN NGINX_VERSION="$(nginx -v 2>&1)" && \
    NGINX_VERSION="${NGINX_VERSION##*/}" && \
    apk add --update --no-cache \
            brotli-dev \
            build-base \
            git \
            gnupg \
            linux-headers \
            openssl-dev \
            pcre2-dev \
            zlib-dev && \
    git init /tmp/ngx_brotli && \
    git -C /tmp/ngx_brotli remote add origin https://github.com/google/ngx_brotli.git && \
    git -C /tmp/ngx_brotli fetch --depth 1 origin "${NGX_BROTLI_COMMIT}" && \
    git -C /tmp/ngx_brotli checkout --detach FETCH_HEAD && \
    git -C /tmp/ngx_brotli submodule update --init --recursive --depth 1 && \
    mkdir -m 0700 /tmp/gnupg /tmp/nginx_signing_keys && \
    wget -q https://nginx.org/keys/arut.key \
            -O /tmp/nginx_signing_keys/arut.key && \
    wget -q https://nginx.org/keys/pluknet.key \
            -O /tmp/nginx_signing_keys/pluknet.key && \
    wget -q https://nginx.org/keys/sb.key \
            -O /tmp/nginx_signing_keys/sb.key && \
    wget -q https://nginx.org/keys/thresh.key \
            -O /tmp/nginx_signing_keys/thresh.key && \
    GNUPGHOME=/tmp/gnupg gpg --batch --show-keys --with-colons \
            /tmp/nginx_signing_keys/*.key \
            > /tmp/nginx_signing_key_details && \
    for fingerprint in \
            "${NGINX_ARUT_SIGNING_KEY_FINGERPRINT}" \
            "${NGINX_PLUKNET_SIGNING_KEY_FINGERPRINT}" \
            "${NGINX_SB_SIGNING_KEY_FINGERPRINT}" \
            "${NGINX_THRESH_SIGNING_KEY_FINGERPRINT}"; do \
        grep -Fqx "fpr:::::::::${fingerprint}:" /tmp/nginx_signing_key_details || exit 1; \
    done && \
    printf '%s\n' \
            "${NGINX_ARUT_SIGNING_KEY_FINGERPRINT}" \
            "${NGINX_PLUKNET_SIGNING_KEY_FINGERPRINT}" \
            "${NGINX_SB_SIGNING_KEY_FINGERPRINT}" \
            "${NGINX_THRESH_SIGNING_KEY_FINGERPRINT}" \
            > /tmp/nginx_expected_fingerprints && \
    sort -u /tmp/nginx_expected_fingerprints \
            > /tmp/nginx_expected_primary_fingerprints && \
    awk -F: '\
        $1 == "pub" { primary = 1; next } \
        primary && $1 == "fpr" { print $10; primary = 0 } \
    ' /tmp/nginx_signing_key_details > /tmp/nginx_actual_fingerprints && \
    sort -u /tmp/nginx_actual_fingerprints \
            > /tmp/nginx_actual_primary_fingerprints && \
    cmp -s /tmp/nginx_actual_primary_fingerprints \
            /tmp/nginx_expected_primary_fingerprints && \
    GNUPGHOME=/tmp/gnupg gpg --batch --import /tmp/nginx_signing_keys/*.key && \
    wget -q "https://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz" \
            -O "/tmp/nginx-${NGINX_VERSION}.tar.gz" && \
    wget -q "https://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz.asc" \
            -O "/tmp/nginx-${NGINX_VERSION}.tar.gz.asc" && \
    GNUPGHOME=/tmp/gnupg gpg --batch --verify \
            "/tmp/nginx-${NGINX_VERSION}.tar.gz.asc" \
            "/tmp/nginx-${NGINX_VERSION}.tar.gz" && \
    tar xzf "/tmp/nginx-${NGINX_VERSION}.tar.gz" -C /tmp && \
    cd "/tmp/nginx-${NGINX_VERSION}" && \
    ./configure \
            --with-compat \
            --with-cc-opt='-Wno-error=unterminated-string-initialization -Wno-error=vla-parameter' \
            --add-dynamic-module=/tmp/ngx_brotli && \
    make modules && \
    cp objs/ngx_http_brotli_static_module.so \
            /tmp/ngx_http_brotli_static_module.so

# PLEASE KEEP THIS LITERAL OR DEPENDABOT WILL NOT BE ABLE TO UPDATE IT.
FROM nginx:1.31.4-alpine

RUN mkdir -p /etc/nginx/modules

COPY --from=brotli-builder \
    /tmp/ngx_http_brotli_static_module.so \
    /etc/nginx/modules/ngx_http_brotli_static_module.so

# hadolint ignore=DL3018
RUN apk add --update --no-cache \
            brotli-libs \
            py3-pip \
            certbot \
            certbot-nginx \
            openssl && \
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
    NGINX_HTTP2=http2 \
    NGINX_CLIENT_BODY_SIZE=30 \
    NGINX_ADMIN_ALLOW_NETWORK=all \
    NGINX_HTTPS_ALLOWED_IPS=all \
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
    NGINX_BROTLI_SWITCH=on \
    NGINX_CUSTOM_FILE=False \
    NGINX_WORKER_PROCESSES=1 \
    NGINX_WORKER_CONNECTIONS=1024 \
    NGINX_WORKER_RLIMIT_NOFILE=__UNSET__ \
    NGINX_EVENTS_BLOCK='' \
    NINGX_REAL_REMOTE_ADDR='$real_ip' \
    NGINX_SSL_PORT=443 \
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
