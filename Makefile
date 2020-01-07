# Find documentation in README.md under
# the heading "Makefile Options".
-include .makerc

SHELL := /bin/bash

default: compose-build

# Build
python-build: build.py
	python build.py change-secret-key

build-base:
	# Build Intermedia Image with System Packages
	docker build --tag openwisp/openwisp-base:intermedia-system \
	             --file ./build/openwisp_base/Dockerfile \
	             --target SYSTEM ./build/
	# Build Intermedia Image with Python Packages
	docker build --tag openwisp/openwisp-base:intermedia-python \
	             --file ./build/openwisp_base/Dockerfile \
	             --target PYTHON ./build/ \
	             --build-arg OPENWISP_CONTROLLER_SOURCE=${OPENWISP_CONTROLLER_SOURCE} \
	             --build-arg OPENWISP_TOPOLOGY_SOURCE=${OPENWISP_TOPOLOGY_SOURCE} \
	             --build-arg DJANGO_FREERADIUS_SOURCE=${DJANGO_FREERADIUS_SOURCE} \
	             --build-arg OPENWISP_RADIUS_SOURCE=${OPENWISP_RADIUS_SOURCE} \
	             --build-arg OPENWISP_USERS_SOURCE=${OPENWISP_USERS_SOURCE} \
	             --build-arg DJANGO_NETJSONCONFIG_SOURCE=${DJANGO_NETJSONCONFIG_SOURCE} \
	             --build-arg DJANGO_NETJSONGRAPH_SOURCE=${DJANGO_NETJSONGRAPH_SOURCE} \
	             --build-arg DJANGO_X509_SOURCE=${DJANGO_X509_SOURCE} \
	             --build-arg OPENWISP_UTILS_SOURCE=${OPENWISP_UTILS_SOURCE}
	# Build Final Image
	docker build --tag openwisp/openwisp-base:latest \
	             --file ./build/openwisp_base/Dockerfile ./build/

compose-build: python-build build-base
	docker-compose build --parallel
	python build.py default-secret-key

publish-build: build-base
	docker-compose build --parallel

# Test
runtests: develop-runtests
	docker-compose stop

develop-runtests: publish-build
	docker-compose up -d
	source ./tests/tests.sh && init_tests

travis-runtests: publish-build
	docker-compose up -d
	echo "127.0.0.1 dashboard.openwisp.org controller.openwisp.org" \
	     "radius.openwisp.org topology.openwisp.org" | sudo tee -a /etc/hosts
	source ./tests/tests.sh && init_tests logs

# Development
develop: publish-build
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
				`docker images -f "dangling=true" -q` || true

# Publish
publish: publish-build develop-runtests
	docker push openwisp/openwisp-base:latest
	docker-compose push
