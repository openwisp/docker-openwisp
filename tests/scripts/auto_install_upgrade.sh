#!/bin/bash

source <(sed '/^## Init script$/,$d' "$AUTO_INSTALL_SCRIPT")

INSTALL_PATH="$TEST_INSTALL_PATH"
ENV_BACKUP="$TEST_ENV_BACKUP"
LOG_FILE="$TEST_LOG_FILE"

get_version_from_user() { openwisp_version=edge; }
download_docker_openwisp() { :; }
check_status() { :; }
start_step() { :; }
report_ok() { :; }
make() { :; }

upgrade_docker_openwisp
