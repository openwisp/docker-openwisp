#!/bin/sh
# OpenWISP common module init script
set -e
source utils.sh

init_conf

# Start services
if [ "$MODULE_NAME" = 'dashboard' ]; then
	if [ "$OPENWISP_GEOCODING_CHECK" = 'True' ]; then
		python manage.py check --deploy --tag geocoding
	fi
	python services.py database redis
	python manage.py migrate --noinput
	test -f "$SSH_PRIVATE_KEY_PATH" || ssh-keygen -t ed25519 -f "$SSH_PRIVATE_KEY_PATH" -N ""
	python load_init_data.py
	python collectstatic.py
	start_uwsgi
elif [ "$MODULE_NAME" = 'postfix' ]; then
	postfix_config
	postfix set-permissions
	postfix start
	rsyslogd -n
elif [ "$MODULE_NAME" = 'freeradius' ]; then
	wait_nginx_services
	if [ "$FREERADIUS_DEBUG_MODE" = 'True' ]; then
		source docker-entrypoint.sh -X
	else
		source docker-entrypoint.sh
	fi
elif [ "$MODULE_NAME" = 'openvpn' ]; then
	if [ -z "$VPN_DOMAIN" ]; then exit; fi
	. ./openvpn_utils.sh
	wait_nginx_services
	openvpn_preconfig
	openvpn_config
	openvpn_config_download
	crl_download
	crontab /openvpn.crontab
	crond
	# Schedule send topology script only when
	# network topology module is enabled.
	if [ "$USE_OPENWISP_TOPOLOGY" == "True" ]; then
		init_send_network_topology
	fi
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
	# Expand escape sequences in the optional events block so it can be injected
	# correctly into the nginx configuration template.
	NGINX_EVENTS_BLOCK=$(printf "%b" "${NGINX_EVENTS_BLOCK:-}")
	export NGINX_EVENTS_BLOCK
	# Use a sentinel value when the variable is unset. Since envsubst cannot
	# conditionally omit directives, we later remove any line containing this
	# sentinel from the generated nginx.conf.
	export NGINX_WORKER_RLIMIT_NOFILE="${NGINX_WORKER_RLIMIT_NOFILE:-__UNSET__}"
	envsubst </etc/nginx/nginx.template.conf >/etc/nginx/nginx.conf
	# Remove incomplete worker_rlimit_nofile directives if env var is unset or empty
	sed -i '/__UNSET__/d; /^worker_rlimit_nofile *$/d; /^[[:space:]]*$/d' /etc/nginx/nginx.conf
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
	source celery_supervisor.sh
	generate_celery_supervisor_config /opt/openwisp/supervisor/conf.d/workers.conf
	# Keep Supervisor as PID 1 so it receives Docker stop signals.
	exec supervisord --nodaemon
elif [ "$MODULE_NAME" = 'celery_monitoring' ]; then
	python services.py database redis dashboard
	if [[ "$USE_OPENWISP_MONITORING" == "True" && "$USE_OPENWISP_CELERY_MONITORING" == 'True' ]]; then
		source celery_supervisor.sh
		generate_celery_supervisor_config /opt/openwisp/supervisor/conf.d/workers.conf
		# Keep Supervisor as PID 1 so it receives Docker stop signals.
		exec supervisord --nodaemon
	else
		echo "Monitoring queues are not activated, exiting."
	fi
elif [ "$MODULE_NAME" = 'celerybeat' ]; then
	rm -rf celerybeat.pid
	python services.py database redis dashboard
	exec celery -A openwisp beat -l ${DJANGO_LOG_LEVEL}
else
	python services.py database redis dashboard
	start_uwsgi
fi
