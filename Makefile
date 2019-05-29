# Find documentation in README.md under
# the heading "Makefile Options".

SHELL := /bin/bash

default: compose-build

# Build
python-build: build.py
	python build.py change-secret-key

build-base:
	docker build --tag openwisp/openwisp-base:intermedia-system \
	             --file ./build/openwisp_base/Dockerfile \
	             --target SYSTEM ./build/
	docker build --tag openwisp/openwisp-base:intermedia-python \
	             --file ./build/openwisp_base/Dockerfile \
	             --target PYTHON ./build/
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
	source ./tests/tests.sh && init_dashoard_tests

travis-runtests: publish-build
	docker-compose up -d
	echo "127.0.0.1 dashboard.openwisp.org controller.openwisp.org" \
	     "radius.openwisp.org topology.openwisp.org" | sudo tee -a /etc/hosts
	source ./tests/tests.sh && init_dashoard_tests logs

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
	docker push openwisp/openwisp-nginx:latest
	docker push openwisp/openwisp-dashboard:latest
	docker push openwisp/openwisp-radius:latest
	docker push openwisp/openwisp-controller:latest
	docker push openwisp/openwisp-topology:latest
	docker push openwisp/openwisp-websocket:latest
	docker push openwisp/openwisp-postfix:latest
