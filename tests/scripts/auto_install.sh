#!/bin/bash
# Run installer paths with external operations disabled for testing.

source <(sed '/^## Init script$/,$d' "$AUTO_INSTALL_SCRIPT")

INSTALL_PATH="$TEST_INSTALL_PATH"
ENV_BACKUP="$TEST_ENV_BACKUP"
ENV_USER="$TEST_INSTALL_PATH/config.env"
LOG_FILE="$TEST_LOG_FILE"

get_version_from_user() { openwisp_version="${TEST_OPENWISP_VERSION:-edge}"; }
docker() {
	if [[ "$*" == "compose version --short" ]]; then
		printf '%s\n' "${TEST_COMPOSE_VERSION-2.33.1}"
		return "${TEST_COMPOSE_STATUS:-0}"
	fi
	printf 'docker %s\n' "$*" >>"$INSTALL_PATH/commands.log"
	[[ "${TEST_FAIL_COMMAND-}" != "compose-$2" ]]
}
download_docker_openwisp() { touch "$INSTALL_PATH/downloaded"; }
start_step() { :; }
report_ok() { :; }
make() {
	printf 'make %s\n' "$*" >>"$INSTALL_PATH/commands.log"
	if [[ "$1" == "start" ]]; then
		cp "$INSTALL_PATH/.env" "$INSTALL_PATH/started.env"
	fi
	[[ "${TEST_FAIL_COMMAND-}" != "$1" ]]
}

if [[ "${TEST_ACTION:-upgrade}" == "install" ]]; then
	setup_docker_openwisp
else
	upgrade_docker_openwisp
fi
