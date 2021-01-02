#!/bin/sh
# OpenWISP common module init script
set -e
source utils.sh

init_conf

# Start services
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
elif [ "$MODULE_NAME" = 'freeradius' ]; then
    wait_nginx_services
    if [ "$DEBUG_MODE" = 'False' ]; then
        source docker-entrypoint.sh
    else
        source docker-entrypoint.sh -X
    fi
elif [ "$MODULE_NAME" = 'openvpn' ]; then
    if [[ -z "$VPN_DOMAIN" ]]; then exit; fi
    wait_nginx_services
    openvpn_preconfig
    openvpn_config
    openvpn_config_download
    crl_download
    echo "*/1 * * * * sh /openvpn.sh" | crontab -
    (crontab -l ; echo "0 3 * * 7 sh /revokelist.sh")| crontab -
    crond
    # Supervisor is used to start the service because OpenVPN
    # needs to restart after crl list is updated or configurations
    # are changed. If OpenVPN as the service keeping the
    # docker container running, restarting would mean killing
    # the container while supervisor helps only to restart the service!
    supervisord --nodaemon --configuration supervisord.conf
elif [ "$MODULE_NAME" = 'nginx' ]; then
    rm -rf /etc/nginx/conf.d/default.conf
    if [ "$NGINX_CUSTOM_FILE" = 'True' ]; then
        nginx -g 'daemon off;'
    fi
    envsubst < /etc/nginx/nginx.template.conf > /etc/nginx/nginx.conf
    envsubst_create_config /etc/nginx/openwisp.internal.template.conf internal INTERNAL
    if [ "$SSL_CERT_MODE" = 'Yes' ]; then
        nginx_prod
    elif [ "$SSL_CERT_MODE" = 'SelfSigned' ]; then
        nginx_dev
    else
        envsubst_create_config /etc/nginx/openwisp.template.conf http DOMAIN
    fi
    nginx -g 'daemon off;'
elif [ "$MODULE_NAME" = 'celery' ]; then
    python services.py database redis dashboard
    celery -A openwisp worker -l ${DJANGO_LOG_LEVEL}
elif [ "$MODULE_NAME" = 'celerybeat' ]; then
    rm -rf celerybeat.pid
    python services.py database redis dashboard
    celery -A openwisp beat -l ${DJANGO_LOG_LEVEL}
else
    python services.py database redis dashboard
    start_uwsgi
fi
