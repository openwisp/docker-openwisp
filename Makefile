# Makefile to create all the docker-images

SHELL := /bin/bash

# Build
compose-build: build-base
	docker-compose build

build-base: python-build-script
	docker build --tag openwisp/openwisp-base:intermedia-system \
	             --file ./build/openwisp_base/Dockerfile \
	             --target SYSTEM ./build/
	docker build --tag openwisp/openwisp-base:intermedia-python \
	             --file ./build/openwisp_base/Dockerfile \
	             --target PYTHON ./build/
	docker build --tag openwisp/openwisp-base:latest \
	             --file ./build/openwisp_base/Dockerfile ./build/

python-build-script: build.py
	python build.py change-secret-key

# Test
runtests:
	python build.py default-secret-key
	docker-compose up -d
	source ./tests/tests.sh && init_dashoard_tests logs
	docker-compose stop
