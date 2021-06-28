# Quick Setup: docker-compose

[![Gitter](https://img.shields.io/gitter/room/openwisp/general.svg)](https://gitter.im/openwisp/dockerize-openwisp)
[![Support](https://img.shields.io/badge/support-orange.svg)](http://openwisp.org/support.html)

1. Install requirements (Debian):

```bash
sudo apt -y update
sudo apt -y install git docker.io docker-compose make
# Please ensure docker is installed properly and the following
# command show system information. In most machines, you'll need to
# add your user to the `docker` group and re-login to the shell.
docker info
```

2. Setup repository:

```bash
git clone https://github.com/openwisp/docker-openwisp.git
cd docker-openwisp
```

3. Configure:

Please follow the [environment variable documentation](ENV.md) and customize your deployment of OpenWISP.
Remember to change the values for [essential](ENV.md#Essential) and [security](ENV.md#Security) variables.

4. Deploy: `make start`

**Note: If you want to shutdown services for maintenance or any other purposes, please use `make stop`.**

**Note:** Facing errors while installation? Please [read the FAQ](FAQ.md).
