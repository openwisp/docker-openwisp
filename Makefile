# Find documentation in README.md under
# the heading "Makefile Options".

SHELL := /bin/bash
.SILENT: clean pull start stop

default: compose-build

# Pull
USER = registry.gitlab.com/openwisp/docker-openwisp
TAG  = latest
pull:
	printf '\e[1;34m%-6s\e[m\n' "Downloading OpenWISP images..."
	for image in 'openwisp-base' 'openwisp-nfs' 'openwisp-api' 'openwisp-dashboard' \
				 'openwisp-freeradius' 'openwisp-nginx' 'openwisp-openvpn' 'openwisp-postfix' \
				 'openwisp-websocket' ; do \
		docker pull --quiet $(USER)/$${image}:$(TAG) &> /dev/null; \
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
	docker-compose build --parallel

# Test
runtests: develop-runtests
	docker-compose stop

develop-runtests:
	docker-compose up -d
	python3 tests/runtests.py

# Development
develop: compose-build
	docker-compose up -d
	docker-compose logs -f

# Clean
clean:
	printf '\e[1;34m%-6s\e[m\n' "Removing docker-openwisp..."
	docker-compose stop &> /dev/null
	docker-compose down --remove-orphans --volumes --rmi all &> /dev/null
	docker-compose rm -svf &> /dev/null
	docker rmi --force openwisp/openwisp-base:latest \
				openwisp/openwisp-base:intermedia-system \
				openwisp/openwisp-base:intermedia-python \
				openwisp/openwisp-nfs:latest \
				`docker images -f "dangling=true" -q` \
				`docker images | grep openwisp/docker-openwisp | tr -s ' ' | cut -d ' ' -f 3` &> /dev/null

# Production
USER = registry.gitlab.com/openwisp/docker-openwisp
TAG  = latest
start: pull
	printf '\e[1;34m%-6s\e[m\n' "Starting Services..."
	docker-compose --log-level WARNING up -d
	printf '\e[1;32m%-6s\e[m\n' "Success: OpenWISP should be available at your dashboard domain in 2 minutes."

stop:
	printf '\e[1;31m%-6s\e[m\n' "Stopping OpenWISP services..."
	docker-compose --log-level ERROR stop
	docker-compose --log-level ERROR down --remove-orphans
	docker-compose down --remove-orphans &> /dev/null

# Publish
USER = registry.gitlab.com/openwisp/docker-openwisp
TAG  = latest
publish: compose-build runtests nfs-build
	for image in 'openwisp-base' 'openwisp-nfs' 'openwisp-api' 'openwisp-dashboard' \
				 'openwisp-freeradius' 'openwisp-nginx' 'openwisp-openvpn' 'openwisp-postfix' \
				 'openwisp-websocket' ; do \
		docker tag openwisp/$${image}:latest $(USER)/$${image}:$(TAG); \
		docker push $(USER)/$${image}:$(TAG); \
		docker rmi $(USER)/$${image}:$(TAG); \
		if [[ "$(TAG)" != "edge" ]] && [[ "$(TAG)" != "latest" ]]; then \
			docker tag openwisp/$${image}:latest $(USER)/$${image}:latest; \
			docker push $(USER)/$${image}:latest; \
			docker rmi $(USER)/$${image}:latest; \
		fi \
	done
