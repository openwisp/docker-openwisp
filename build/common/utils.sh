#!/bin/sh

function start_uwsgi {
    envsubst < uwsgi.conf.ini > uwsgi.ini
    uwsgi --ini uwsgi.ini
}

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

function ssl_http_behaviour {
    if [ "$NGINX_HTTP_ALLOW" == "True" ]; then
        envsubst_create_config /etc/nginx/openwisp.template.conf http
    else
        envsubst < /etc/nginx/openwisp.ssl.80.template.conf > /etc/nginx/conf.d/openwisp.http.conf
    fi
}

function envsubst_create_config {
    # Creates nginx configurations files for dashboard,
    # controller, radius and network-topology instances.
    for application in DASHBOARD CONTROLLER RADIUS TOPOLOGY; do
        eval export APP_SERVICE=\$$application\_APP_SERVICE
        eval export APP_PORT=\$$application\_APP_PORT
        eval export DOMAIN=\$$application\_DOMAIN
        application=$(echo "$application" | tr "[:upper:]" "[:lower:]")
        envsubst < ${1} > /etc/nginx/conf.d/${application}.${2}.conf
    done
}

function postfix_config {
    # This function is used to configure the
    # postfix instance.

    mkdir  -p /var/spool/postfix/ /var/spool/postfix/pid /var/lib/postfix/
    chmod 755 /var/spool/postfix/ /var/spool/postfix/pid /var/lib/postfix/
    rm -rf /etc/aliases /etc/postfix/generic /etc/allowed_senders /etc/postfix/main.cf /var/run/rsyslogd.pid
    touch  /etc/aliases /etc/postfix/generic /etc/allowed_senders /etc/postfix/main.cf
    # Create ssl-certs
    if [ ! -f /etc/ssl/mail/openwisp.mail.key ]; then
        openssl req -new -nodes -x509 -subj '/CN=openwisp-postfix' -days 3650 -keyout /etc/ssl/mail/openwisp.mail.key -out /etc/ssl/mail/openwisp.mail.crt -extensions v3_ca
    fi

    # Disable SMTPUTF8, because libraries (ICU) are missing in alpine
    postconf -e smtputf8_enable=no

    # Configure posfix
    postconf -e biff=no
    postconf -e append_dot_mydomain=no
    postconf -e readme_directory=no

    postconf -e smtpd_use_tls=yes
    postconf -e smtpd_tls_cert_file=/etc/ssl/mail/openwisp.mail.crt
    postconf -e smtpd_tls_key_file=/etc/ssl/mail/openwisp.mail.key
    postconf -e smtpd_tls_session_cache_database=btree:/var/lib/postfix/smtpd_scache
    postconf -e smtp_tls_session_cache_database=btree:/var/lib/postfix/smtp_scache

    postconf -e myhostname="$POSTFIX_MYHOSTNAME"
    postconf -e myorigin='$myhostname'
    postconf -e alias_maps=hash:/etc/aliases
    postconf -e smtp_generic_maps=hash:/etc/postfix/generic
    postconf -e alias_database=hash:/etc/aliases
    postconf -e mydestination="$POSTFIX_DESTINATION"

    postconf -e mynetworks="$POSTFIX_MYNETWORKS"
    postconf -e message_size_limit="$POSTFIX_MESSAGE_SIZE_LIMIT"
    postconf -e recipient_delimiter=+
    postconf -e inet_protocols=all

    postconf -e bounce_queue_lifetime=1h
    postconf -e maximal_queue_lifetime=1h
    postconf -e maximal_backoff_time=15m
    postconf -e minimal_backoff_time=5m
    postconf -e queue_run_delay=5m

    if [ "$POSTFIX_ALLOWED_SENDER_DOMAINS" != 'False' ]; then
        for i in $POSTFIX_ALLOWED_SENDER_DOMAINS; do
            echo -e "$i\tOK" >> /etc/allowed_senders
        done
        postmap /etc/allowed_senders
        postconf -e "smtpd_restriction_classes=allowed_domains_only"
        postconf -e "allowed_domains_only=permit_mynetworks, reject_non_fqdn_sender reject"
        postconf -e "smtpd_recipient_restrictions=reject_non_fqdn_recipient, check_sender_access hash:/etc/allowed_senders, reject"
        postconf -e "smtpd_relay_restrictions=permit"
    fi

    if [ "$POSTFIX_RELAYHOST" != 'False' ]; then
        postconf -e "relayhost=$POSTFIX_RELAYHOST"
        postconf -e smtp_tls_CAfile=/etc/ssl/mail/openwisp.mail.crt
        if [ -n "$POSTFIX_RELAYHOST_USERNAME" ] && [ -n "$POSTFIX_RELAYHOST_PASSWORD" ]; then
            echo "$POSTFIX_RELAYHOST $POSTFIX_RELAYHOST_USERNAME:$POSTFIX_RELAYHOST_PASSWORD" >> /etc/postfix/sasl_passwd
            postmap hash:/etc/postfix/sasl_passwd
            postconf -e "smtp_sasl_auth_enable=yes"
            postconf -e "smtp_sasl_password_maps=hash:/etc/postfix/sasl_passwd"
            postconf -e "smtp_sasl_security_options=noanonymous"
            postconf -e "smtp_sasl_tls_security_options=noanonymous"
        fi
        postconf -e smtp_tls_security_level="$POSTFIX_RELAYHOST_TLS_LEVEL"
    fi

    if [ "$POSTFIX_DEBUG_MYNETWORKS" != 'False' ]; then
        postconf -e debug_peer_level=10
        postconf -e debug_peer_list="$POSTFIX_DEBUG_MYNETWORKS"
    fi

    postmap /etc/postfix/generic
    postmap /etc/aliases
    newaliases
}
