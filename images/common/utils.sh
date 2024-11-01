#!/bin/sh

function init_conf {
	default_psql_vars
}

function default_psql_vars {
	# Set database variable values in default PG
	# vars to use psql command without passing additional
	# arguments.
	export PGHOST=$DB_HOST
	export PGPORT=$DB_PORT
	export PGUSER=$DB_USER
	export PGPASSWORD=$DB_PASS
	export PGDATABASE=$DB_NAME
	export PGSSLMODE=$DB_SSLMODE
	export PGSSLCERT=$DB_SSLCERT
	export PGSSLKEY=$DB_SSLKEY
	export PGSSLROOTCERT=$DB_SSLROOTCERT
}

function start_uwsgi {
	# If a user supplies custom uWSGI configuration, then
	# due to lack of write permissions this command will fail.
	# Hence, OR (||) operator is used here to continue execution
	# of the script.
	envsubst <uwsgi.conf.ini >uwsgi.ini || true
	uwsgi --ini uwsgi.ini
}

function create_prod_certs {
	if [ ! -f /etc/letsencrypt/live/${DASHBOARD_DOMAIN}/privkey.pem ]; then
		certbot certonly --standalone --noninteractive --agree-tos \
			--rsa-key-size 4096 \
			--domain ${DASHBOARD_DOMAIN} \
			--email ${CERT_ADMIN_EMAIL}
	fi
	if [ ! -f /etc/letsencrypt/live/${API_DOMAIN}/privkey.pem ]; then
		certbot certonly --standalone --noninteractive --agree-tos \
			--rsa-key-size 4096 \
			--domain ${API_DOMAIN} \
			--email ${CERT_ADMIN_EMAIL}
	fi
}

function create_dev_certs {
	# Ensure required directories exist
	mkdir -p /etc/letsencrypt/live/${DASHBOARD_DOMAIN}/
	mkdir -p /etc/letsencrypt/live/${API_DOMAIN}/
	# Create self-signed certificates
	if [ ! -f /etc/letsencrypt/live/${DASHBOARD_DOMAIN}/privkey.pem ]; then
		openssl req -x509 -newkey rsa:4096 \
			-keyout /etc/letsencrypt/live/${DASHBOARD_DOMAIN}/privkey.pem \
			-out /etc/letsencrypt/live/${DASHBOARD_DOMAIN}/fullchain.pem \
			-days 365 -nodes -subj '/CN=OpenWISP'
	fi
	if [ ! -f /etc/letsencrypt/live/${API_DOMAIN}/privkey.pem ]; then
		openssl req -x509 -newkey rsa:4096 \
			-keyout /etc/letsencrypt/live/${API_DOMAIN}/privkey.pem \
			-out /etc/letsencrypt/live/${API_DOMAIN}/fullchain.pem \
			-days 365 -nodes -subj '/CN=OpenWISP'
	fi
}

function nginx_dev {
	envsubst_create_config /etc/nginx/openwisp.ssl.template.conf https DOMAIN
	ssl_http_behaviour
	create_dev_certs
	CMD="source /etc/nginx/utils.sh && create_dev_certs && nginx -s reload"
	echo "0 3 1 1 * $CMD &>> /etc/nginx/log/crontab.log" | crontab -
	nginx -g 'daemon off;'
}

function nginx_prod {
	create_prod_certs
	ssl_http_behaviour
	envsubst_create_config /etc/nginx/openwisp.ssl.template.conf https DOMAIN
	CMD="certbot --nginx renew && nginx -s reload"
	echo "0 3 * * 7 ${CMD} &>> /etc/nginx/log/crontab.log" | crontab -
}

function wait_nginx_services {
	# Wait for nginx to start up and then check
	# if the openwisp-dashboard is reachable.
	echo "Waiting for dashboard to become available..."
	# Make fault tolerant to ensure connection
	# error report by `wget` is received.
	set +e
	while :; do
		wget -qS ${DASHBOARD_INTERNAL}/admin/login/ 2>&1 | grep -q "200 OK"
		if [[ $? = "0" ]]; then
			FAILURE=0
			echo "Connection with dashboard established."
			break
		fi
		sleep 5
	done
	set -e # Restore previous error setting.
}

function ssl_http_behaviour {
	if [ "$NGINX_HTTP_ALLOW" == "True" ]; then
		envsubst_create_config /etc/nginx/openwisp.template.conf http DOMAIN
	else
		envsubst </etc/nginx/openwisp.ssl.80.template.conf >/etc/nginx/conf.d/openwisp.http.conf
	fi
}

function envsubst_create_config {
	# Creates nginx configurations files for dashboard
	# and api instances.
	for application in DASHBOARD API; do
		eval export APP_SERVICE=\$${application}_APP_SERVICE
		eval export APP_PORT=\$${application}_APP_PORT
		eval export DOMAIN=\$${application}_${3}
		eval export ROOT_DOMAIN=$(python3 get_domain.py)
		application=$(echo "$application" | tr "[:upper:]" "[:lower:]")
		envsubst <${1} >/etc/nginx/conf.d/${application}.${2}.conf
	done
}

function postfix_config {
	# This function is used to configure the
	# postfix instance.

	mkdir -p /var/spool/postfix/ /var/spool/postfix/pid /var/lib/postfix/
	chmod 755 /var/spool/postfix/ /var/spool/postfix/pid /var/lib/postfix/
	rm -rf /etc/aliases /etc/postfix/generic /etc/allowed_senders /etc/postfix/main.cf /var/run/rsyslogd.pid
	touch /etc/aliases /etc/postfix/generic /etc/allowed_senders /etc/postfix/main.cf
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
	postconf -e alias_maps=lmdb:/etc/aliases
	postconf -e smtp_generic_maps=lmdb:/etc/postfix/generic
	postconf -e alias_database=lmdb:/etc/aliases
	postconf -e mydestination="$POSTFIX_DESTINATION"

	postconf -e mynetworks="$POSTFIX_MYNETWORKS"
	postconf -e message_size_limit="$POSTFIX_MESSAGE_SIZE_LIMIT"
	postconf -e mailbox_size_limit=0
	postconf -e recipient_delimiter=+
	postconf -e inet_protocols=all

	postconf -e bounce_queue_lifetime=1h
	postconf -e maximal_queue_lifetime=1h
	postconf -e maximal_backoff_time=15m
	postconf -e minimal_backoff_time=5m
	postconf -e queue_run_delay=5m

	if [ "$POSTFIX_ALLOWED_SENDER_DOMAINS" != 'null' ]; then
		for i in $POSTFIX_ALLOWED_SENDER_DOMAINS; do
			echo -e "$i\tOK" >>/etc/allowed_senders
		done
		postmap /etc/allowed_senders
		postconf -e "smtpd_restriction_classes=allowed_domains_only"
		postconf -e "allowed_domains_only=permit_mynetworks, reject_non_fqdn_sender reject"
		postconf -e "smtpd_recipient_restrictions=reject_non_fqdn_recipient, check_sender_access lmdb:/etc/allowed_senders,permit_sasl_authenticated, reject_unauth_destination"
		postconf -e "smtpd_relay_restrictions=permit"
	fi

	if [ "$POSTFIX_RELAYHOST" != 'null' ]; then
		postconf -e "relayhost=$POSTFIX_RELAYHOST"
		postconf -e smtp_tls_CAfile=/etc/ssl/mail/openwisp.mail.crt
		if [ "$POSTFIX_RELAYHOST_USERNAME" != 'null' ] && [ "$POSTFIX_RELAYHOST_PASSWORD" != 'null' ]; then
			echo "$POSTFIX_RELAYHOST $POSTFIX_RELAYHOST_USERNAME:$POSTFIX_RELAYHOST_PASSWORD" >>/etc/postfix/sasl_passwd
			postmap lmdb:/etc/postfix/sasl_passwd
			postconf -e "smtp_sasl_auth_enable=yes"
			postconf -e "smtp_sasl_password_maps=lmdb:/etc/postfix/sasl_passwd"
			postconf -e "smtp_sasl_security_options=noanonymous"
			postconf -e "smtp_sasl_tls_security_options=noanonymous"
		fi
		postconf -e smtp_tls_security_level="$POSTFIX_RELAYHOST_TLS_LEVEL"
	fi

	if [ "$POSTFIX_DEBUG_MYNETWORKS" != 'null' ]; then
		postconf -e debug_peer_level=10
		postconf -e debug_peer_list="$POSTFIX_DEBUG_MYNETWORKS"
	fi

	postmap /etc/postfix/generic
	postmap /etc/aliases
	newaliases
}

get_redis_value() {
	local key="$1"
	echo -en "GET $key\r\n" | nc redis 6379 | awk 'NR==2 {gsub(/\r/, ""); print}'
}

function openvpn_preconfig {
	mkdir -p /dev/net
	if [ ! -c /dev/net/tun ]; then
		mknod /dev/net/tun c 10 200
	fi
	ip -6 route show default 2>/dev/null
	if [ $? = 0 ]; then
		echo "Enabling IPv6 Forwarding"
		sysctl -w net.ipv6.conf.all.disable_ipv6=0 || echo "Failed to enable IPv6 support"
		sysctl -w net.ipv6.conf.default.forwarding=1 || echo "Failed to enable IPv6 Forwarding default"
		sysctl -w net.ipv6.conf.all.forwarding=1 || echo "Failed to enable IPv6 Forwarding"
	fi
}

function openvpn_config {
	# Fectch UUID and Key of the default VPN only if they
	# are not already set. The user may override the UUID and Key
	# by setting them in the environment variables to use deploy
	# a different VPN server.
	if [ -z "$UUID" ]; then
		export UUID=$(get_redis_value "openwisp_default_vpn_uuid")
		export KEY=$(get_redis_value "openwisp_default_vpn_key")
		export CA_UUID=$(get_redis_value "openwisp_default_vpn_ca_uuid")
	fi
}

function openvpn_config_checksum {
	export OFILE=$(curl --silent --insecure \
		${API_INTERNAL}/controller/vpn/checksum/$UUID/?key=$KEY)
	export NFILE=$(cat checksum)
}

function openvpn_config_download {
	curl --silent --retry 10 --retry-delay 5 --retry-max-time 300\
		--insecure --output vpn.tar.gz \
		${API_INTERNAL}/controller/vpn/download-config/$UUID/?key=$KEY
	curl --silent --insecure --output checksum \
		${API_INTERNAL}/controller/vpn/checksum/$UUID/?key=$KEY
	tar xzf vpn.tar.gz
	chmod 600 *.pem
}

function crl_download {
	curl --silent --insecure --output revoked.crl \
	${DASHBOARD_INTERNAL}/admin/pki/ca/x509/ca/${CA_UUID}.crl
}

function init_send_network_topology {
	if [ -z "$TOPOLOGY_UUID" ]; then
		export TOPOLOGY_UUID=$(get_redis_value "default_openvpn_topology_uuid")
		export TOPOLOGY_KEY=$(get_redis_value "default_openvpn_topology_key")
	fi
	(
		crontab -l
		echo "*/$TOPLOGY_UPDATE_INTERVAL * * * * TOPOLOGY_UUID=$TOPOLOGY_UUID TOPOLOGY_KEY=$TOPOLOGY_KEY sh /send-topology.sh"
	) | crontab -
}
