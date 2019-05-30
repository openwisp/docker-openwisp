#!/bin/sh
# OpenWISP common module init script
set -e
source utils.sh

# Set timezone
ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

if [ "$MODULE_NAME" = 'dashboard' ]; then
    python services.py database redis
    python manage.py migrate --noinput
    python load_init_data.py
    python manage.py collectstatic --noinput
    start_uwsgi
elif [ "$MODULE_NAME" = 'postfix' ]; then
    postfix_config
    postfix start
    rsyslogd -n
elif [ "$MODULE_NAME" = 'nginx' ]; then
    rm -rf /etc/nginx/conf.d/default.conf
    envsubst < /etc/nginx/nginx.template.conf > /etc/nginx/nginx.conf
    if [ "$SSL_CERT_MODE" = 'True' ]; then
        envsubst_create_config /etc/nginx/openwisp.ssl.template.conf https
        ssl_http_behaviour
        nginx -g 'daemon off;'
        create_prod_certs
        echo "0 3 * * 7 certbot renew &>> /etc/nginx/log/crontab.log" | crontab -
    elif [ "$SSL_CERT_MODE" = 'Develop' ]; then
        envsubst_create_config /etc/nginx/openwisp.ssl.template.conf https
        ssl_http_behaviour
        create_dev_certs
        CMD="source /etc/nginx/utils.sh && create_dev_certs && nginx -s reload"
        echo "0 3 1 1 * $CMD &>> /etc/nginx/log/crontab.log" | crontab -
        nginx -g 'daemon off;'
    else
        envsubst_create_config /etc/nginx/openwisp.template.conf http
        nginx -g 'daemon off;'
    fi
else
    python services.py database redis dashboard
    start_uwsgi
fi
