# Docker-OpenWISP

[![Automation Tests](https://github.com/openwisp/docker-openwisp/workflows/Automation%20Tests/badge.svg)](https://github.com/openwisp/docker-openwisp/actions?query=workflow%3A%22Automation+Tests%22)
[![GitLab Container Registery](https://img.shields.io/badge/registry-openwisp-blue.svg)](https://gitlab.com/openwisp/docker-openwisp/container_registry)
[![Gitter](https://badges.gitter.im/openwisp/dockerize-openwisp.svg)](https://gitter.im/openwisp/dockerize-openwisp?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)
[![Support](https://img.shields.io/badge/support-orange.svg)](http://openwisp.org/support.html)
[![GitHub license](https://img.shields.io/github/license/openwisp/docker-openwisp.svg)](https://github.com/openwisp/docker-openwisp/blob/master/LICENSE)

This repository contains official docker images of OpenWISP. Designed with horizontal scaling, easily replicable deployments and user customization in mind.

![kubernetes](https://i.ibb.co/rGpLq4y/ss1.png)
The sample files for deployment on kubernetes are available in the `deploy/examples/kubernetes/` directory.

## Available Images

| Version | Corresponding Ansible Version |
| ------- | :---------------------------: |
| 0.1.0a2 |             0.9.0             |
| 0.1.0a3 |            0.12.0             |
| 0.1.0a4 |            0.12.0+            |
| 0.1.0a5 |            0.13.1             |
| 0.1.0a6 |            0.13.2+            |

\* Roughly the same features would be available but it's not an exact one-to-one mapping.

## Architecture

![Architecture](docs/images/architecture.jpg)

- **openwisp-dashboard**: Your OpenWISP device administration dashboard.
- **openwisp-api**: HTTP API from various openwisp modules which can be scaled simply by having multiple
  API containers as per requirement.
- **openwisp-radius**: HTTP API for interacting with openwisp-radius. Separated from the rest of APIs as it
  can have different scalability requirements in large deployments.
- **openwisp-websocket**: Dedicated container for handling websocket requests, eg. for updating location of
  mobile network devices.
- **openwisp-celery**: Runs all the background tasks for OpenWISP, eg. updating configurations of your device.
- **openwisp-celerybeat**: Runs periodic background tasks. eg. revoking all the expired certificates.
- **openwisp-nginx**: Internet facing container that facilitates all the HTTP and Websocket communication
  between the outside world and the service containers.
- **openwisp-freeradius**: Freeradius container for OpenWISP.
- **openwisp-openvpn**: OpenVPN container for out-of-the-box management VPN.
- **openwisp-postfix**: Mail server for sending mails to MTA.
- **openwisp-nfs**: NFS server that allows shared storage between different machines. It does not run
  in single server machines but provided for K8s setup.
- **openwisp-base**: It is the base image which does not run on your server, but openwisp-radius,
  openwisp-api & openwisp-dashboard use it as a base.
- **Redis**: data caching service (required for actions like login).
- **PostgreSQL**: SQL database container for OpenWISP.

## Deployment

### Quick Setup

The `auto-install.sh` script can be used to quickly install a simple instance of openwisp on your server.

[![Quick Install](docs/images/auto-install.png)](https://www.youtube.com/watch?v=LLbsKP79MzE "Install tutorial")

If you have created a [`.env` file](docs/ENV.md) to configure your instance, then you can use it with the script otherwise.

**It asks 6 questions for application configuration, 4 of them are domain names.** The dashboard, api, radius & openvpn can be setup on different domain, **please ensure the domains you enter point to your server**. The remaining **2 questions are email id** for site manager email (used by django to send application emails) and letsencrypt (used by [certbot](https://certbot.eff.org/) to issue https certs on this address.)

To get started, run the following command:

```bash
   curl -L https://bit.do/auto-install -o setup.sh
   sudo bash setup.sh
   # If you are upgrading from an older version setup by this script use
   # sudo bash setup.sh --upgrade
   # For more information
   # sudo bash setup.sh --help
```

**Note:** Facing errors while installation? Please [read the FAQ](docs/FAQ.md).

### Compose

[Setup on docker-compose](docs/QUICK_SETUP.md) is suitable for single-server setup requirements. It is quicker and requires less prior knowledge about openwisp & networking.

### Kubernetes

Setup on kubernetes is complex and requires prior knowledge about linux systems, kubernetes, docker & openwisp. However, it provides scalability for very large networks.

- [Bare Metal](docs/kubernetes/BARE_METAL.md)
- [Google Cloud](docs/kubernetes/GOOGLE_CLOUD.md)

## Customization

### Workbench setup

1. Install docker & docker-compose.
2. In the root of the repository, run `make develop`, when the containers are ready, you can test them out by going to the domain name of the modules.

#### Notes:

- Default username & password are `admin`.
- Default domains are: `dashboard.openwisp.org`, `api.openwisp.org` and `radius.openwisp.org`.
- To reach the dashboard you may need to add the openwisp domains set in your `.env` to your `hosts` file,
  example: `bash -c 'echo "127.0.0.1 dashboard.openwisp.org api.openwisp.org radius.openwisp.org" >> /etc/hosts'`
- Now you'll need to do steps (2) everytime you make a changes and want to build the images again.
- If you want to perform actions like cleaning everything produced by `docker-openwisp`,
  please use the [makefile options](#makefile-options).

### Changing Python Packages

You can build with your own python package by creating a file named `.build.env` in the root of the repository, then set the variables inside `.build.env` file in `<variable>=<value>` format. Multiple variable should be separated in newline. These are the variables that can be changed:

- `OPENWISP_MONITORING_SOURCE`
- `OPENWISP_FIRMWARE_SOURCE`
- `OPENWISP_CONTROLLER_SOURCE`
- `OPENWISP_NOTIFICATION_SOURCE`
- `OPENWISP_TOPOLOGY_SOURCE`
- `OPENWISP_RADIUS_SOURCE`
- `OPENWISP_USERS_SOURCE`
- `OPENWISP_UTILS_SOURCE`
- `OPENWISP_IPAM_SOURCE`
- `DJANGO_SOURCE`
- `DJANGO_NETJSONCONFIG_SOURCE`
- `DJANGO_X509_SOURCE`

For example, if you want to supply your own django and openwisp-controller source, your `.build.env` should be written like this:

```
DJANGO_SOURCE=django==3.2
OPENWISP_CONTROLLER_SOURCE=https://github.com/<username>/openwisp-api/tarball/master
```

### Disabling Services

**Right now, this is only tentative guide. Errata may exist. Please report errors on the [gitter channel](https://gitter.im/openwisp/dockerize-openwisp).**

- `openwisp-dashboard`: You cannot disable the openwisp-dashboard. It is the heart of OpenWISP and performs core functionalities.
- `openwisp-api`: You cannot disable the openwisp-api. It is required for interacting with your devices.
- `openwisp-websocket`: Removing this container will cause the system to not able to update real-time location for mobile devices.

If you want to disable a service, you can simply remove the container for that service, however, there are additional steps for some images:

- `openwisp-network-topology`: Set the `USE_OPENWISP_TOPOLOGY` variable to `False`.
- `openwisp-firmware-upgrader` : Set the `USE_OPENWISP_FIRMWARE` variable to `False`.
- `openwisp-monitoring` : Set the `USE_OPENWISP_MONITORING` variable to `False`.
- `openwisp-radius` : Set the `USE_OPENWISP_RADIUS` variable to `False`.
- `openwisp-postgres`: If you are using a seperate database instance,
  - Ensure your database instance is reachable by the following OpenWISP containers: `openvpn`, `freeradius`, `celerybeat`, `celery`, `websocket`, `radius`, `api`, `dashboard`.
  - Ensure your database server supports GeoDjango. (Install PostGIS for PostgreSQL)
  - Change the [database configuration variables](docs/ENV.md) to point to your instances, if you are using SSL, remember to set `DB_SSLMODE`, `DB_SSLKEY`, `DB_SSLCERT`, `DB_SSLROOTCERT`.
  - If you are using SSL, remember to mount volume containing the certificates and key in all the containers which contact the database server and make sure that the private key permission is `600` and owned by `root:root`.
  - In your database, create database with name `<DB_NAME>`.
- `openwisp-postfix`:
  - Ensure your SMTP instance reachable by the OpenWISP containers.
  - Change the [email configuration variables](docs/ENV.md) to point to your instances.

### Runtests

You can run tests either with `geckodriver` (firefox) or `chromedriver` (chromium). Chromium is preferred as it checks for console log errors as well.

1. Setup driver for selenium:

   - Setup chromedriver

     1. Install: `sudo apt --yes install chromium`
     2. Check version: `chromium --version`
     3. Install Driver for your version: `https://chromedriver.chromium.org/downloads`
     4. Extract chromedriver to one of directories from your `$PATH`. (example: `/usr/bin/`)

   - Setup geckodriver

     1. Install: `sudo apt --yes install firefox`
     2. Check version: `firefox --version`
     3. Install Driver for your version: `https://github.com/mozilla/geckodriver/releases`
     4. Extract geckodriver to one of directories from your `$PATH`. (example: `/usr/bin/`)

2. Install selenium: `python3 -m pip install selenium`

3. (Optional) Configure: open `tests/config.json` and configure variables as per your requirement, options are:

   ```yaml
   driver: Name of driver to use for tests, "chromium" or "firefox"
   logs: print container's logs if an error occurs.
   logs_file: Location of the log file for saving logs generated for tests.
   headless: Run selenium chrome driver in headless mode
   load_init_data: Flag for running tests/data.py, only needs to be done once after database creation
   app_url: URL to reach the admin dashboard
   username: username for logging in admin dashboard
   password: password for logging in admin dashboard
   services_max_retries: Maximum number of retries to check if services are running
   services_delay_retries: Delay time (in seconds) to each retries for checking if services are running
   ```

4. Run tests: `make runtests`

**Note:** To run a single test use the following command

```bash
python3 tests/runtests.py <TestSuite>.<TestCase>
# python3 tests/runtests.py TestServices.test_celery
```

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
