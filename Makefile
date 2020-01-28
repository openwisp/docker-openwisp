# Find documentation in README.md under
# the heading "Makefile Options".

SHELL := /bin/bash

default: compose-build

# Build
python-build: build.py
	python build.py change-secret-key

base-build:
	BUILD_ARGS_FILE=$$(cat .build.env 2>/dev/null); \
	for build_arg in $$BUILD_ARGS_FILE; do \
	    BUILD_ARGS+=" --build-arg $$build_arg"; \
	done; \
	docker build --tag openwisp/openwisp-base:intermedia-system \
	             --file ./build/openwisp_base/Dockerfile \
	             --target SYSTEM ./build/; \
	docker build --tag openwisp/openwisp-base:intermedia-python \
	             --file ./build/openwisp_base/Dockerfile \
	             --target PYTHON ./build/ \
	             $$BUILD_ARGS; \
	docker build --tag openwisp/openwisp-base:latest \
	             --file ./build/openwisp_base/Dockerfile ./build/ \
	             $$BUILD_ARGS

nfs-build:
	docker build --tag openwisp/openwisp-nfs:latest \
	             --file ./build/openwisp_nfs/Dockerfile ./build/

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
	docker-compose stop
	docker-compose down --remove-orphans --volumes --rmi all
	docker-compose rm -svf
	docker rmi --force openwisp/openwisp-base:latest \
				openwisp/openwisp-base:intermedia-system \
				openwisp/openwisp-base:intermedia-python \
				openwisp/openwisp-nfs:latest \
				`docker images -f "dangling=true" -q`

# Publish
USER = openwisp
TAG  = latest
publish: compose-build runtests nfs-build
	for image in 'openwisp-base' 'openwisp-nfs' 'openwisp-controller' 'openwisp-dashboard' \
				 'openwisp-freeradius' 'openwisp-nginx' 'openwisp-openvpn' 'openwisp-postfix' \
				 'openwisp-radius' 'openwisp-topology' 'openwisp-websocket' ; do \
		docker tag openwisp/$${image}:latest  $(USER)/$${image}:$(TAG); \
		docker push $(USER)/$${image}:$(TAG); \
		docker push $(USER)/$${image}:latest; \
	done
