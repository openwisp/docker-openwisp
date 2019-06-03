#!/bin/sh

function create_prod_certs {
    certbot certonly --nginx --noninteractive --agree-tos
                     --rsa-key-size 4096
                     --domain ${DASHBOARD_DOMAIN}
                     --domain ${CONTROLLER_DOMAIN}
                     --domain ${RADIUS_DOMAIN}
                     --domain ${TOPOLOGY_DOMAIN}
                     --email ${CERT_ADMIN_EMAIL}
    nginx -s reload # reload to reflect changes
}

function create_dev_certs {
    # Ensure required directories exist
    mkdir -p /etc/letsencrypt/live/${DASHBOARD_DOMAIN}/
    mkdir -p /etc/letsencrypt/live/${CONTROLLER_DOMAIN}/
    mkdir -p /etc/letsencrypt/live/${RADIUS_DOMAIN}/
    mkdir -p /etc/letsencrypt/live/${TOPOLOGY_DOMAIN}/
    # Create self-signed certificates
    if [ ! -f /etc/letsencrypt/live/${DASHBOARD_DOMAIN}/privkey.pem ]; then
        openssl req -x509 -newkey rsa:4096 \
                    -keyout /etc/letsencrypt/live/${DASHBOARD_DOMAIN}/privkey.pem \
                    -out /etc/letsencrypt/live/${DASHBOARD_DOMAIN}/fullchain.pem \
                    -days 365 -nodes -subj '/CN=OpenWISP'
    fi
    if [ ! -f /etc/letsencrypt/live/${CONTROLLER_DOMAIN}/privkey.pem ]; then
        openssl req -x509 -newkey rsa:4096 \
                    -keyout /etc/letsencrypt/live/${CONTROLLER_DOMAIN}/privkey.pem \
                    -out /etc/letsencrypt/live/${CONTROLLER_DOMAIN}/fullchain.pem \
                    -days 365 -nodes -subj '/CN=OpenWISP'
    fi
    if [ ! -f /etc/letsencrypt/live/${RADIUS_DOMAIN}/privkey.pem ]; then
        openssl req -x509 -newkey rsa:4096 \
                    -keyout /etc/letsencrypt/live/${RADIUS_DOMAIN}/privkey.pem \
                    -out /etc/letsencrypt/live/${RADIUS_DOMAIN}/fullchain.pem \
                    -days 365 -nodes -subj '/CN=OpenWISP'
    fi
    if [ ! -f /etc/letsencrypt/live/${TOPOLOGY_DOMAIN}/privkey.pem  ]; then
        openssl req -x509 -newkey rsa:4096 \
                    -keyout /etc/letsencrypt/live/${TOPOLOGY_DOMAIN}/privkey.pem  \
                    -out /etc/letsencrypt/live/${TOPOLOGY_DOMAIN}/fullchain.pem \
                    -days 365 -nodes -subj '/CN=OpenWISP'
    fi
}

function sslHttpBehaviour {
    if [ "$HTTP_ALLOW" == "TRUE" ]; then
        envsubst_create_config /etc/nginx/openwisp.template.conf http
    else
        envsubst < /etc/nginx/openwisp.ssl.80.template.conf > /etc/nginx/conf.d/openwisp.http.conf
    fi
}

function envsubst_create_config {
    for application in DASHBOARD CONTROLLER RADIUS TOPOLOGY; do
        eval export APP_SERVICE=\$$application\_APP_SERVICE
        eval export APP_PORT=\$$application\_APP_PORT
        eval export DOMAIN=\$$application\_DOMAIN
        application=$(echo "$application" | tr "[:upper:]" "[:lower:]")
        envsubst < ${1} > /etc/nginx/conf.d/${application}.${2}.conf
    done
}
