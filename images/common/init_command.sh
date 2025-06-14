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
	(
		crontab -l
		echo "0 0 * * * sh /revokelist.sh"
	) | crontab -
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
	envsubst </etc/nginx/nginx.template.conf >/etc/nginx/nginx.conf
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
	echo "Starting the 'default' celery worker"
	celery -A openwisp worker -l ${DJANGO_LOG_LEVEL} --queues celery \
		-n celery@%h --logfile /opt/openwisp/logs/celery.log \
		--pidfile /opt/openwisp/celery.pid --detach \
		${OPENWISP_CELERY_COMMAND_FLAGS}

	if [ "$USE_OPENWISP_CELERY_NETWORK" = "True" ]; then
		echo "Starting the 'network' celery worker"
		celery -A openwisp worker -l ${DJANGO_LOG_LEVEL} --queues network \
			-n network@%h --logfile /opt/openwisp/logs/celery_network.log \
			--pidfile /opt/openwisp/celery_network.pid --detach \
			${OPENWISP_CELERY_NETWORK_COMMAND_FLAGS}
	fi

	if [[ "$USE_OPENWISP_FIRMWARE" == "True" && "$USE_OPENWISP_CELERY_FIRMWARE" == "True" ]]; then
		echo "Starting the 'firmware_upgrader' celery worker"
		celery -A openwisp worker -l ${DJANGO_LOG_LEVEL} --queues firmware_upgrader \
			-n firmware_upgrader@%h --logfile /opt/openwisp/logs/celery_firmware_upgrader.log \
			--pidfile /opt/openwisp/celery_firmware_upgrader.pid --detach \
			${OPENWISP_CELERY_FIRMWARE_COMMAND_FLAGS}
	fi
	sleep 1s
	tail -f /opt/openwisp/logs/*
elif [ "$MODULE_NAME" = 'celery_monitoring' ]; then
	python services.py database redis dashboard
	if [[ "$USE_OPENWISP_MONITORING" == "True" && "$USE_OPENWISP_CELERY_MONITORING" == 'True' ]]; then
		echo "Starting the 'monitoring' celery worker"
		celery -A openwisp worker -l ${DJANGO_LOG_LEVEL} --queues monitoring \
			-n monitoring@%h --logfile /opt/openwisp/logs/celery_monitoring.log \
			--pidfile /opt/openwisp/celery_monitoring.pid --detach \
			${OPENWISP_CELERY_MONITORING_COMMAND_FLAGS}
		echo "Starting the 'monitoring_checks' celery worker"
		celery -A openwisp worker -l ${DJANGO_LOG_LEVEL} --queues monitoring_checks \
			-n monitoring_checks@%h --logfile /opt/openwisp/logs/celery_monitoring_checks.log \
			--pidfile /opt/openwisp/celery_monitoring_checks.pid --detach \
			${OPENWISP_CELERY_MONITORING_CHECKS_COMMAND_FLAGS}
		sleep 1s
		tail -f /opt/openwisp/logs/*
	else
		echo "Monitoring queues are not activated, exiting."
	fi
elif [ "$MODULE_NAME" = 'celerybeat' ]; then
	rm -rf celerybeat.pid
	python services.py database redis dashboard
	celery -A openwisp beat -l ${DJANGO_LOG_LEVEL}
else
	python services.py database redis dashboard
	start_uwsgi
fi
