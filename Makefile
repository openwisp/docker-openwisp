# Find documentation in README.md under
# the heading "Makefile Options".

SHELL := /bin/bash
REGISTRY ?= openwisp
TAG := $(shell cat VERSION)
export REGISTRY TAG

default: compose-build

# Build
python-build: build.py
	python build.py change-secret-key

build-base:
	docker build --tag $(REGISTRY)/openwisp-base:intermedia-system \
	             --file ./build/openwisp_base/Dockerfile \
	             --target SYSTEM ./build/
	docker build --tag $(REGISTRY)/openwisp-base:intermedia-python \
	             --file ./build/openwisp_base/Dockerfile \
	             --target PYTHON ./build/
	docker build --tag $(REGISTRY)/openwisp-base:$(TAG) \
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
	docker rmi --force `docker images -f "reference=*/openwisp-*" -q` \
	                   `docker images -f "dangling=true" -q`

# Publish
publish: develop-runtests
	docker push $(REGISTRY)/openwisp-base:$(TAG)
	docker-compose push
	docker tag $(REGISTRY)/openwisp-base:$(TAG) $(REGISTRY)/openwisp-base:latest
	docker push $(REGISTRY)/openwisp-base:latest
	images=$$(docker-compose config | awk '{if($$0 ~ /image: $(REGISTRY)/ && !visited[$$0]++) print $$2}'); \
	for image in $$images; do \
		img_target=`echo $$image | sed "s/:$(TAG)/:latest/g"`; \
		docker tag $$image $$img_target; \
		docker push $$img_target; \
	done

travis-publish: TAG := nightly
travis-publish: travis-runtests
	echo "$(DOCKER_PASSWORD)" | docker login -u "$(DOCKER_USERNAME)" --password-stdin
	docker push $(REGISTRY)/openwisp-base:$(TAG)
	docker-compose push
	echo "$(GITHUB_TOKEN)" | docker login docker.pkg.github.com -u $(GITHUB_USERNAME) --password-stdin
	docker tag $(REGISTRY)/openwisp-base:$(TAG) \
               docker.pkg.github.com/$(GITHUB_USERNAME)/docker-openwisp/openwisp-base:$(TAG)
	docker push docker.pkg.github.com/$(GITHUB_USERNAME)/docker-openwisp/openwisp-base:$(TAG)
	images=$$(docker-compose config | awk '{if($$0 ~ /image: $(REGISTRY)/ && !visited[$$0]++) print $$2}'); \
	for image in $$images; do \
		github_docker_repo=`echo $$image | sed "s/$(REGISTRY)\//docker.pkg.github.com\/$(GITHUB_USERNAME)\/docker-openwisp\//g"`; \
		docker tag $$image $$github_docker_repo; \
		docker push $$github_docker_repo; \
	done
