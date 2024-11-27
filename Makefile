# Find documentation in README.md under
# the heading "Makefile Options".

OPENWISP_VERSION = 24.11.1
SHELL := /bin/bash
.SILENT: clean pull start stop

default: compose-build

USER = registry.gitlab.com/openwisp/docker-openwisp
TAG = edge
SKIP_PULL ?= false
SKIP_BUILD ?= false
SKIP_TESTS ?= false

# Pull
pull:
	printf '\e[1;34m%-6s\e[m\n' "Downloading OpenWISP images..."
	for image in 'openwisp-base' 'openwisp-nfs' 'openwisp-api' 'openwisp-dashboard' \
				 'openwisp-freeradius' 'openwisp-nginx' 'openwisp-openvpn' 'openwisp-postfix' \
				 'openwisp-websocket' ; do \
		docker pull --quiet $(USER)/$${image}:$(TAG); \
		docker tag  $(USER)/$${image}:$(TAG) openwisp/$${image}:latest; \
	done

# Build
python-build: build.py
	python build.py change-secret-key

base-build:
	BUILD_ARGS_FILE=$$(cat .build.env 2>/dev/null); \
	for build_arg in $$BUILD_ARGS_FILE; do \
	    BUILD_ARGS+=" --build-arg $$build_arg"; \
	done; \
	docker build --tag openwisp/openwisp-base:intermedia-system \
	             --file ./images/openwisp_base/Dockerfile \
	             --target SYSTEM ./images/; \
	docker build --tag openwisp/openwisp-base:intermedia-python \
	             --file ./images/openwisp_base/Dockerfile \
	             --target PYTHON ./images/ \
	             $$BUILD_ARGS; \
	docker build --tag openwisp/openwisp-base:latest \
	             --file ./images/openwisp_base/Dockerfile ./images/ \
	             $$BUILD_ARGS

nfs-build:
	docker build --tag openwisp/openwisp-nfs:latest \
	             --file ./images/openwisp_nfs/Dockerfile ./images/

compose-build: base-build
	docker compose build --parallel

# Test
runtests: develop-runtests
	docker compose stop

develop-runtests:
	docker compose up -d
	make develop-pythontests

develop-pythontests:
	python3 tests/runtests.py

# Development
develop: compose-build
	docker compose up -d
	docker compose logs -f

# Clean
clean:
	printf '\e[1;34m%-6s\e[m\n' "Removing docker-openwisp..."
	docker compose stop &> /dev/null
	docker compose down --remove-orphans --volumes --rmi all &> /dev/null
	docker compose rm -svf &> /dev/null
	docker rmi --force openwisp/openwisp-base:latest \
				openwisp/openwisp-base:intermedia-system \
				openwisp/openwisp-base:intermedia-python \
				openwisp/openwisp-nfs:latest \
				`docker images -f "dangling=true" -q` \
				`docker images | grep openwisp/docker-openwisp | tr -s ' ' | cut -d ' ' -f 3` &> /dev/null

# Production
start:
	if [ "$(SKIP_PULL)" == "false" ]; then \
		make pull; \
	fi
	printf '\e[1;34m%-6s\e[m\n' "Starting Services..."
	docker --log-level WARNING compose up -d
	printf '\e[1;32m%-6s\e[m\n' "Success: OpenWISP should be available at your dashboard domain in 2 minutes."

stop:
	printf '\e[1;31m%-6s\e[m\n' "Stopping OpenWISP services..."
	docker --log-level ERROR compose stop
	docker --log-level ERROR compose down --remove-orphans
	docker compose down --remove-orphans &> /dev/null

# Publish
publish:
	if [[ "$(SKIP_BUILD)" == "false" ]]; then \
		make compose-build nfs-build; \
	fi
	if [[ "$(SKIP_TESTS)" == "false" ]]; then \
		make runtests; \
	fi
	for image in 'openwisp-base' 'openwisp-nfs' 'openwisp-api' 'openwisp-dashboard' \
				 'openwisp-freeradius' 'openwisp-nginx' 'openwisp-openvpn' 'openwisp-postfix' \
				 'openwisp-websocket' ; do \
		# Docker images built locally are tagged "latest" by default. \
		# This script updates the tag of each built image to a user-defined tag \
		# and pushes the newly tagged image to a Docker registry under the user's namespace. \
		docker tag openwisp/$${image}:latest $(USER)/$${image}:$(TAG); \
		docker push $(USER)/$${image}:$(TAG); \
		if [ "$(TAG)" != "latest" ]; then \
			docker rmi $(USER)/$${image}:$(TAG); \
		fi; \
	done

release:
	make publish TAG=latest SKIP_TESTS=true
	make publish TAG=$(OPENWISP_VERSION) SKIP_BUILD=true SKIP_TESTS=true
