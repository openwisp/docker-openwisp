#!/bin/sh
# Nginx init script
set -e


if [ "$NGINX_IP6" = 'True' ]; then
    NGINX_IP6_STRING="listen [::]:443 ssl $NGINX_HTTP2;"
    NGINX_IP6_80_STRING="listen [::]:80;"
fi

if [ "$ORCHESTRATION_CERT_MODE" = 'True' ] || [ "$ORCHESTRATION_CERT_MODE" = 'Devel' ]; then
    # Get nginx site configurations ready
    envsubst < /etc/nginx/openwisp.ssl.template.conf > /etc/nginx/conf.d/default.conf
    # Check if all the certificates exist
    echo "Waiting for all SSL certificates to be created..."
    dhparams="/etc/letsencrypt/openwisp-dhparams.pem"
    dashboard_path="/etc/letsencrypt/live/${DASHBOARD_DOMAIN}/privkey.pem"
    controller_path="/etc/letsencrypt/live/${CONTROLLER_DOMAIN}/privkey.pem"
    radius_path="/etc/letsencrypt/live/${RADIUS_DOMAIN}/privkey.pem"
    topology_path="/etc/letsencrypt/live/${TOPOLOGY_DOMAIN}/privkey.pem"
    while [ ! -f $dhparams ]; do sleep 3; done
    while [ ! -f $dashboard_path ]; do sleep 3; done
    while [ ! -f $controller_path ]; do sleep 3; done
    while [ ! -f $radius_path ]; do sleep 3; done
    while [ ! -f $topology_path ]; do sleep 3; done
    echo "All SSL certificates found."
    # Set cronjob to ensure updated certs reflect
    echo "30 3 * * 7 nginx -s reload &>> /etc/nginx/crontab.log" | crontab -
else
    envsubst < /etc/nginx/openwisp.template.conf > /etc/nginx/conf.d/default.conf
fi

mkdir -p /etc/nginx/log/
touch /etc/nginx/log/nginx.access.log /etc/nginx/log/nginx.error.log

nginx -g 'daemon off;'
