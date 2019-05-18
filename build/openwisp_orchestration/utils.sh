#!/bin/sh
# Helping functions for init_command.sh

function createProdCerts {
    certbot certonly --standalone --noninteractive --agree-tos \
    --rsa-key-size 4096 \
    --domain ${DASHBOARD_DOMAIN} \
    --domain ${CONTROLLER_DOMAIN} \
    --domain ${RADIUS_DOMAIN} \
    --domain ${TOPOLOGY_DOMAIN} \
    --email ${CERT_ADMIN_EMAIL}
    if [ ! -f /etc/letsencrypt/openwisp-dhparams.pem ]; then
        openssl dhparam -out /etc/letsencrypt/openwisp-dhparams.pem 4096
    fi
}

function createDevCerts {
    # Ensure required directories exist
    mkdir -p /etc/letsencrypt/live/${DASHBOARD_DOMAIN}/
    mkdir -p /etc/letsencrypt/live/${CONTROLLER_DOMAIN}/
    mkdir -p /etc/letsencrypt/live/${RADIUS_DOMAIN}/
    mkdir -p /etc/letsencrypt/live/${TOPOLOGY_DOMAIN}/
    # Create self-signed certificates
    if [ ! -f /etc/letsencrypt/live/${DASHBOARD_DOMAIN}/privkey.pem ]; then    
        openssl req -x509 -newkey rsa:1024 \
            -keyout /etc/letsencrypt/live/${DASHBOARD_DOMAIN}/privkey.pem \
            -out /etc/letsencrypt/live/${DASHBOARD_DOMAIN}/fullchain.pem \
            -days 365 -nodes -subj '/CN=openwisp-orchestration'
    fi
    if [ ! -f /etc/letsencrypt/live/${CONTROLLER_DOMAIN}/privkey.pem ]; then
        openssl req -x509 -newkey rsa:1024 \
            -keyout /etc/letsencrypt/live/${CONTROLLER_DOMAIN}/privkey.pem \
            -out /etc/letsencrypt/live/${CONTROLLER_DOMAIN}/fullchain.pem \
            -days 365 -nodes -subj '/CN=openwisp-orchestration'
    fi
    if [ ! -f /etc/letsencrypt/live/${RADIUS_DOMAIN}/privkey.pem ]; then
        openssl req -x509 -newkey rsa:1024 \
            -keyout /etc/letsencrypt/live/${RADIUS_DOMAIN}/privkey.pem \
            -out /etc/letsencrypt/live/${RADIUS_DOMAIN}/fullchain.pem \
            -days 365 -nodes -subj '/CN=openwisp-orchestration'
    fi
    if [ ! -f /etc/letsencrypt/live/${TOPOLOGY_DOMAIN}/privkey.pem ]; then
        openssl req -x509 -newkey rsa:1024 \
            -keyout /etc/letsencrypt/live/${TOPOLOGY_DOMAIN}/privkey.pem  \
            -out /etc/letsencrypt/live/${TOPOLOGY_DOMAIN}/fullchain.pem \
            -days 365 -nodes -subj '/CN=openwisp-orchestration'
    fi
    if [ ! -f /etc/letsencrypt/openwisp-dhparams.pem ]; then
        openssl dhparam -out /etc/letsencrypt/openwisp-dhparams.pem 512
    fi
}
