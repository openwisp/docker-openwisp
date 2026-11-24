#!/bin/bash
# Install CI host tools and Python dependencies without starting containers.
set -e
if [ "${CI_SYSTEM_DEPS_READY:-0}" != 1 ]; then
	sudo curl -sL -o /bin/hadolint "https://github.com/hadolint/hadolint/releases/download/v2.12.0/hadolint-Linux-x86_64"
	sudo chmod +x /bin/hadolint
	sudo curl -sL -o /usr/local/bin/shfmt "https://github.com/mvdan/sh/releases/download/v3.13.1/shfmt_v3.13.1_linux_amd64"
	sudo chmod +x /usr/local/bin/shfmt
	sudo apt-get update
	sudo apt-get install -y python3-venv
	sudo npm install -g prettier
fi
if [ "${CI_SYSTEM_DEPS_ONLY:-0}" = 1 ]; then
	exit 0
fi
if [ -n "${GITHUB_PATH:-}" ]; then
	python -m venv "$RUNNER_TEMP/openwisp-venv"
	"$RUNNER_TEMP/openwisp-venv/bin/python" -m pip install -r requirements-test.txt
	echo "$RUNNER_TEMP/openwisp-venv/bin" >>"$GITHUB_PATH"
else
	python -m pip install -r requirements-test.txt
fi
