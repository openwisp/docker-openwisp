# Docker-OpenWISP

[![Build Status](https://travis-ci.org/openwisp/docker-openwisp.svg?branch=master)](https://travis-ci.org/openwisp/docker-openwisp)
[![Docker Hub](https://img.shields.io/badge/docker--hub-openwisp-blue.svg)](https://hub.docker.com/u/openwisp)
[![Gitter](https://badges.gitter.im/openwisp/dockerize-openwisp.svg)](https://gitter.im/openwisp/dockerize-openwisp?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)
[![Support](https://img.shields.io/badge/support-orange.svg)](http://openwisp.org/support.html)
[![GitHub license](https://img.shields.io/github/license/atb00ker/docker-openwisp.svg)](https://github.com/openwisp/docker-openwisp/blob/master/LICENSE)

This repository contains official docker images of OpenWISP. Designed with horizontal scaling, easily replicable deployments and user customization in mind.

![kubernetes](https://i.ibb.co/rGpLq4y/ss1.png)
The sample files for deployment on kubernetes are available in the `deployment-examples/kubernetes/` directory.

## TL;DR

Images are available on docker hub and can be pulled from the following links:
- OpenWISP Base - `openwisp/openwisp-base:latest`
- OpenWISP Dashboard - `openwisp/openwisp-dashboard:latest`
- OpenWISP Radius - `openwisp/openwisp-radius:latest`
- OpenWISP Controller - `openwisp/openwisp-controller:latest`
- OpenWISP Network Topology - `openwisp/openwisp-topology:latest`
- OpenWISP Nginx - `openwisp/openwisp-nginx:latest`
- OpenWISP Postfix - `openwisp/openwisp-postfix:latest`
- OpenWISP Websocket - `openwisp/openwisp-websocket:latest`

The configuration for openwisp images using environment variables is available [here](docs/ENV.md). Additionally, you can further customize your setup by mounting custom configuration files for which instructions are available [here](docs/FILES.md).

## Index

1. [Deployment](#Deployment): Steps for a sample deployment of these images in production.
2. [Disabling Services](#disabling-services): Instructions to disable services you don't want to use, like when using database-as-a-service, you don't need postgresql container.
3. [Build (Development)](#build-development): Instructions for building your custom images.
4. [Makefile Options](#makefile-options): Instructions for using the makefile.

## Deployment

1. [Docker Compose](#docker-compose)
2. Kubernetes
   2.1 [Bare Metal](docs/kubernetes/BARE_METAL.md)
   2.2 [Google Cloud](docs/kubernetes/GOOGLE_CLOUD.md)

### Docker Compose

Installing on docker-compose is relatively less resource and time consuming.

**Notes:**

- If you want to build images, please read [here](#build-development).
- If you want to preform actions like building images or cleaning `docker-openwisp`, please use the [makefile options](#makefile-options).
- If you are installing for trying out `docker-openwisp`, please read the [notes](#notes) below.


1. Install docker & docker-compose.

2. Change the following options in `.env` file according to your system: `DJANGO_SECRET_KEY`, `DB_USER`, `DB_PASS`, `EMAIL_DJANGO_DEFAULT`, `DASHBOARD_DOMAIN`, `CONTROLLER_DOMAIN`, `RADIUS_DOMAIN`, `TOPOLOGY_DOMAIN`. Optionally, you may change any other setting as well. A detailed document of the available variables can be found [here](docs/ENV.md).

3. Pull all the required images to avoid building them. (Building images is a time consuming task.)

```bash
docker pull openwisp/openwisp-base:latest
docker pull openwisp/openwisp-dashboard:latest
docker pull openwisp/openwisp-radius:latest
docker pull openwisp/openwisp-controller:latest
docker pull openwisp/openwisp-topology:latest
docker pull openwisp/openwisp-nginx:latest
docker pull openwisp/openwisp-postfix:latest
docker pull openwisp/openwisp-websocket:latest
```

4. Run containers: Inside root of the repository, run `docker-compose up`. It will take a while for the containers to start up. (~1 minute)

5. When the containers are ready, you can test them out by going to the domain name that you've set for the modules.

## Disabling Services

To disable an openwisp service container and plug your own service like database, SMTP or nginx:

- You cannot disable the openwisp-dashboard container. It is the heart of OpenWISP and performs core functionalities.
- Disabling the openwisp-daphne & openwisp-websocket containers will cause some functions to fail.
- You can remove the openwisp-openvpn incase you do not want an OpenVPN server.
- To disable openwisp-topology set the `SET_TOPOLOGY_TASKS` variable to `False`. Then, remove any instance of openwisp-topology in the same docker network.
- To disable openwisp-radius set the `SET_RADIUS_TASKS` variable to `False`. Then, remove any instance of openwisp-radius in the same docker network.
- If you do not need openwisp-controller, remove any instance of openwisp-controller in the same docker network.
- Disabling openwisp-postgres:
   - Ensure your database instance reachable by the OpenWISP containers.
   - Ensure your database server supports GeoDjango.
   - Change the [database configuration variables](docs/ENV.md) to point to your instances.
- Disabling openwisp-postfix:
   - Ensure your SMTP instance reachable by the OpenWISP containers.
   - Change the [email configuration variables](docs/ENV.md) to point to your instances.
- Disabling openwisp-nginx:
   - Configurations in `build/openwisp_nginx/` are helpful to replicate in your own instance.
- Disabling openwisp-freeradius:
   - Ensure your freeradius service is reachable on port `1812/udp` and `1813/udp` otherwise openwisp-radius services will fail to work properly.

## Build (Development)

Guide to build images again with modification or with different environment variables.

1. Install docker-compose.
2. In the root of the repository, run `make develop`, when the containers are ready, you can test them out by going to the domain name of the modules.

Now you'll need to do steps (2) everytime you make a changes and want to build the images again.

#### Notes:

   - Default username & password are `admin`.
   - Default domains are: `dashboard.openwisp.org`, `controller.openwisp.org`, `radius.openwisp.org` and `topology.openwisp.org`.
   - To reach the dashboard you should add the openwisp domains set in your `.env` to your hosts file, example:

   ```bash
   bash -c 'echo "127.0.0.1 <your-dashboard-domain> <your-controller-domain> <your-radius-domain> <your-topology-domain>" >> /etc/hosts'
   ```

# Makefile Options

**Right now, this is only tentative guide. Errata may exist. Please report errors on the [gitter channel](https://gitter.im/openwisp/dockerize-openwisp).**

The Makefile has following options, that are useful for developers & users. Default action is `compose-build`.

- `build-base`: Build openwisp-base image. It is the base image used in other images. It takes the most time to build.
- `compose-build`: Build the openwisp images. This option must be used in most usecases, example when a user is building custom images.
- `publish-build`: Similar to `compose-build` except the produced can be used for manually testing before publishing official images and publishing the official images using the `publish` option.
- `runtests`: Run testcases to ensure all the services are working.
- `develop-runtests`: Similar to `runtests`, it runs the testcases except doesn't stop the containers after running the tests which maybe desired for debugging & analyzing failing container's logs.
- `travis-runtests`: Similar to `runtests`, it runs the testcases except used in travis builds because it doesn't clean up after running the tests and prints all the container's logs when an error occurs in the tests.
- `clean`: Purge everything produced during building the images.
- `develop`: Useful for development. Bundles all the commands required to build the images and run containers during development. With this option, you can interact with the interface and APIs and the logs will be printed on the terminal for debugging on the debugging level you select from the `.env` file.
- `publish`: Build, test and publish the latest Official images.
