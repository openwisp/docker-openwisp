#!/bin/sh
# Nginx init script
set -e

rm -rf /etc/nginx/conf.d/default.conf
mkdir -p /etc/nginx/log/
touch /etc/nginx/log/nginx.access.log /etc/nginx/log/nginx.error.log
envsubst < /etc/nginx/http.conf > /etc/nginx/conf.d/http.conf
source /etc/nginx/utils.sh

if [ "$NGINX_IP6" = 'True' ]; then
    NGINX_IP6_STRING="listen [::]:443 ssl $NGINX_HTTP2;"
    NGINX_IP6_80_STRING="listen [::]:80;"
fi
if [ "$SSL_CERT_MODE" = 'True' ]; then
    envsubst_create_config /etc/nginx/openwisp.ssl.template.conf https
    sslHttpBehaviour
    nginx -g 'daemon off;'
    create_prod_certs
    echo "0 3 * * 7 certbot renew &>> /etc/nginx/log/crontab.log" | crontab -
elif [ "$SSL_CERT_MODE" = 'Develop' ]; then
    envsubst_create_config /etc/nginx/openwisp.ssl.template.conf https
    sslHttpBehaviour
    create_dev_certs
    CMD="source /etc/nginx/utils.sh && create_dev_certs && nginx -s reload"
    echo "0 3 1 1 * $CMD &>> /etc/nginx/log/crontab.log" | crontab -
    nginx -g 'daemon off;'
else
    envsubst_create_config /etc/nginx/openwisp.template.conf http
    nginx -g 'daemon off;'
fi
