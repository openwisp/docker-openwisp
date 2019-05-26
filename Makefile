# Makefile to create all the docker-images

SHELL := /bin/bash
.PHONY: build-base

# Building
compose-build: build-base
	docker-compose build

build-base: python-build-script
	docker build -t openwisp/openwisp-base:latest -f ./build/openwisp_base/Dockerfile ./build/

python-build-script: build.py
	python build.py change-secret-key

# Testing
runtests:
	python build.py default-secret-key
	docker-compose up -d
	source ./tests/tests.sh && init_dashoard_tests
	docker-compose stop
