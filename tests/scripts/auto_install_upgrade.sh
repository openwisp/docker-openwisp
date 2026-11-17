#!/bin/bash
# Run the upgrade path with external operations disabled for testing.

source <(sed '/^## Init script$/,$d' "$AUTO_INSTALL_SCRIPT")

INSTALL_PATH="$TEST_INSTALL_PATH"
ENV_BACKUP="$TEST_ENV_BACKUP"
LOG_FILE="$TEST_LOG_FILE"

get_version_from_user() { openwisp_version=edge; }
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
	[[ "${TEST_FAIL_COMMAND-}" != "$1" ]]
}

upgrade_docker_openwisp
