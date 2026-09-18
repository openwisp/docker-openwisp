#!/bin/sh

add_celery_worker() {
	local name=$1 queue=$2 flags=$3
	local command="/usr/local/bin/celery -A openwisp worker -l ${DJANGO_LOG_LEVEL} --queues ${queue} -n ${name}@%h ${flags}"
	command=$(printf '%s' "$command" | sed 's/%/%%/g')
	CELERY_SUPERVISOR_WORKERS="${CELERY_SUPERVISOR_WORKERS:+${CELERY_SUPERVISOR_WORKERS},}${name}"
	cat >>"$CELERY_SUPERVISOR_WORKERS_CONF" <<EOF
[program:${name}]
command=${command}
directory=/opt/openwisp
autostart=true
autorestart=true
stopsignal=TERM
; Leave time for Supervisor to exit before Docker's 120-second grace period ends.
stopwaitsecs=90
stopasgroup=false
killasgroup=true
redirect_stderr=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
EOF
}

generate_celery_supervisor_config() {
	CELERY_SUPERVISOR_WORKERS_CONF=${1:-celery_supervisord.d/workers.conf}
	mkdir -p "$(dirname "$CELERY_SUPERVISOR_WORKERS_CONF")"
	: >"$CELERY_SUPERVISOR_WORKERS_CONF"
	CELERY_SUPERVISOR_WORKERS=
	if [ "$MODULE_NAME" = 'celery' ]; then
		add_celery_worker celery celery "${OPENWISP_CELERY_COMMAND_FLAGS}"
		if [ "$USE_OPENWISP_CELERY_NETWORK" = 'True' ]; then
			add_celery_worker network network "${OPENWISP_CELERY_NETWORK_COMMAND_FLAGS}"
		fi
		if [[ "$USE_OPENWISP_FIRMWARE" == 'True' && "$USE_OPENWISP_CELERY_FIRMWARE" == 'True' ]]; then
			add_celery_worker firmware_upgrader firmware_upgrader "${OPENWISP_CELERY_FIRMWARE_COMMAND_FLAGS}"
		fi
	else
		add_celery_worker monitoring monitoring "${OPENWISP_CELERY_MONITORING_COMMAND_FLAGS}"
		add_celery_worker monitoring_checks monitoring_checks "${OPENWISP_CELERY_MONITORING_CHECKS_COMMAND_FLAGS}"
	fi
	cat >>"$CELERY_SUPERVISOR_WORKERS_CONF" <<EOF

; Stop workers together so each receives TERM in the same Supervisor shutdown pass.
[group:workers]
programs=${CELERY_SUPERVISOR_WORKERS}
priority=100
EOF
}
