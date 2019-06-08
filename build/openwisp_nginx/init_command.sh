#!/bin/sh
# Nginx init script
set -e

# Set timezone
ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
# Init
rm -rf /etc/nginx/conf.d/default.conf
envsubst < /etc/nginx/nginx.template.conf > /etc/nginx/nginx.conf
source /etc/nginx/utils.sh

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
