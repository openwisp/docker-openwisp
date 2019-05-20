#!/bin/sh
# Orchestration init script
set -e

# Nginx Related Certificates
if [ "$ORCHESTRATION_CERT_MODE" = 'True' ]; then
    source /opt/openwisp/utils.sh
    createProdCerts
    # TODO: Think about future implementation / future updates about crontab
    echo "0 3 * * 7 certbot renew &>> /etc/nginx/crontab.log" | crontab -
    trap : TERM INT; (while true; do sleep 1000; done) & wait
fi
if [ "$ORCHESTRATION_CERT_MODE" = 'Devel' ]; then
    source /opt/openwisp/utils.sh
    createDevCerts
fi