# Docker-OpenWISP

[![Automation Tests](https://github.com/openwisp/docker-openwisp/workflows/Automation%20Tests/badge.svg)](https://github.com/openwisp/docker-openwisp/actions?query=workflow%3A%22Automation+Tests%22)
[![GitLab Container Registery](https://img.shields.io/badge/registry-openwisp-blue.svg)](https://gitlab.com/openwisp/docker-openwisp/container_registry)
[![Gitter](https://badges.gitter.im/openwisp/dockerize-openwisp.svg)](https://gitter.im/openwisp/dockerize-openwisp?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)
[![Support](https://img.shields.io/badge/support-orange.svg)](http://openwisp.org/support.html)
[![GitHub license](https://img.shields.io/github/license/openwisp/docker-openwisp.svg)](https://github.com/openwisp/docker-openwisp/blob/master/LICENSE)

This repository contains official docker images of OpenWISP. Designed with horizontal scaling, easily replicable deployments and user customization in mind.

![kubernetes](https://i.ibb.co/rGpLq4y/ss1.png)
The sample files for deployment on kubernetes are available in the `deploy/examples/kubernetes/` directory.

## Table of contents

- [Docker-OpenWISP](#docker-openwisp)
  - [Table of contents](#table-of-contents)
  - [Images Available](#images-available)
    - [Image Tags](#image-tags)
  - [Architecture](#architecture)
  - [Deployment](#deployment)
    - [Quick Setup](#quick-setup)
    - [Compose](#compose)
    - [Kubernetes](#kubernetes)
  - [Customization](/docs/CUSTOMIZATION.md)
  - [Development](/docs/DEVELOPMENT.md)
  - [Usage](#usage)
    - [Makefile Options](#makefile-options)

## Images Available

The images are hosted on [GitLab Container Registry](https://gitlab.com/openwisp/docker-openwisp/container_registry).

### Image Tags

All images are tagged using the following convention:

|  Tag   | Software Version                              |
| ------ |---------------------------------------------- |
| latest | Images built on the **latest git tag**        |
| edge   | Images built on the **current master branch** |

## Architecture

A typical OpenWISP installation is made of multiple components
(e.g. application servers, background workers, web servers,
database, messaging queue, VPN server, etc. ) that have different
scaling requirements.

The aim of Docker OpenWISP is to allow deploying
OpenWISP in cloud based environments which
allow potentially infinite horizontal scaling.
That is the reason for which there are different
docker images shipped in this repository.

![Architecture](docs/images/architecture.jpg)

- **openwisp-dashboard**: Your OpenWISP device administration dashboard.
- **openwisp-api**: HTTP API from various openwisp modules which can be scaled simply by having multiple
  API containers as per requirement.
- **openwisp-websocket**: Dedicated container for handling websocket requests, eg. for updating location of
  mobile network devices.
- **openwisp-celery**: Runs all the background tasks for OpenWISP, eg. updating configurations of your device.
- **openwisp-celery-monitoring**: Runs background tasks that perform active monitoring checks,
  eg. ping checks and configuration checks. It also executes task for writing monitoring data
  to the timeseries DB.
- **openwisp-celerybeat**: Runs periodic background tasks. eg. revoking all the expired certificates.
- **openwisp-nginx**: Internet facing container that facilitates all the HTTP and Websocket communication
  between the outside world and the service containers.
- **openwisp-freeradius**: Freeradius container for OpenWISP.
- **openwisp-openvpn**: OpenVPN container for out-of-the-box management VPN.
- **openwisp-postfix**: Mail server for sending mails to MTA.
- **openwisp-nfs**: NFS server that allows shared storage between different machines. It does not run
  in single server machines but provided for K8s setup.
- **openwisp-base**: It is the base image which does not run on your server, but openwisp-api & openwisp-dashboard use it as a base.
- **Redis**: data caching service (required for actions like login).
- **PostgreSQL**: SQL database container for OpenWISP.

## Deployment

### Quick Setup

The `auto-install.sh` script can be used to quickly install a simple instance of openwisp on your server.

[![Quick Install](docs/images/auto-install.png)](https://www.youtube.com/watch?v=LLbsKP79MzE "Install tutorial")

If you have created a [`.env` file](docs/ENV.md) to configure your instance, then you can use it with the script otherwise.

**It asks 5 questions for application configuration, 3 of them are domain names.** The dashboard, api & openvpn can be setup on different domain, **please ensure the domains you enter point to your server**. The remaining **2 questions are email id** for site manager email (used by django to send application emails) and letsencrypt (used by [certbot](https://certbot.eff.org/) to issue https certs on this address.)

To get started, run the following command:

```bash
   curl https://raw.githubusercontent.com/openwisp/docker-openwisp/master/deploy/auto-install.sh -o setup.sh
   sudo bash setup.sh
   # If you are upgrading from an older version setup by this script use
   # sudo bash setup.sh --upgrade
   # For more information
   # sudo bash setup.sh --help
```

To get a real-time streaming output of autoinstall logs, run the following command:

```bash
tail -n 50 -f /opt/openwisp/autoinstall.log
```

**Notes:**

- If you're having any installation issues with the `latest` version, you can try auto-installation
  with the `edge` version, which has images built on the current master branch.

- Still facing errors while installation? Please [read the FAQ](docs/FAQ.md).

### Compose

[Setup on docker-compose](docs/QUICK_SETUP.md) is suitable for single-server setup requirements. It is quicker and requires less prior knowledge about openwisp & networking.

### Kubernetes

Setup on kubernetes is complex and requires prior knowledge about linux systems, kubernetes, docker & openwisp. However, it provides scalability for very large networks.

- [Bare Metal](docs/kubernetes/BARE_METAL.md)
- [Google Cloud](docs/kubernetes/GOOGLE_CLOUD.md)

Useful commands for startup and readiness probes which are provided
by the images:

- startup probe example: `test $(ps aux | grep -c uwsgi) -ge 2`
- readiness probe example: `python services.py uwsgi_status "127.0.0.1:8001"`

## Usage

### Makefile Options

Most commonly used:

- `start`<USER=docker-username> <TAG=image-tag>: Start OpenWISP containers on your server.
- `pull`<USER=docker-username> <TAG=image-tag>: Pull Images from registry.
- `stop`: Stop make containers on your server.
- `develop`: Bundles all the commands required to build the images and run containers.
- `runtests`: Run testcases to ensure all the services are working.
- `clean`: Aggressively purge all the containers, images, volumes & networks related to `docker-openwisp`.

Other options:

- `publish` <USER=docker-username> <TAG=image-tag>: Build, test and publish images.
- `python-build`: Generate a random django secret and set it in the `.env` file.
- `nfs-build`: Build openwisp-nfs server image.
- `base-build`: Build openwisp-base image. The base image is used in other OpenWISP images.
- `compose-build`: (default) Build OpenWISP images for development.
- `develop-runtests`: Similar to `runtests`, it runs the testcases except doesn't stop the containers after running the tests which maybe desired for debugging & analyzing failing container's logs.
