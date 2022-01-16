# Bare Metal Kubernetes

[![Gitter](https://img.shields.io/gitter/room/openwisp/general.svg)](https://gitter.im/openwisp/dockerize-openwisp)
[![Support](https://img.shields.io/badge/support-orange.svg)](http://openwisp.org/support.html)

The following are steps of a sample deployment on a kubernetes cluster. All the files are present in `deploy/examples/kubernetes/` directory of this repository.
The following assumes the reader knows basics of kubernetes & docker.
The steps where performed on master version-1.14.

1. [Setup a Kubernetes Cluster](https://blog.alexellis.io/kubernetes-in-10-minutes/).

2. Make sure to install `nfs-common` on all your nodes.

3. Add label to the node where you want to save the data: `kubectl label nodes <node-name> volume=nfs-server`

4. Setup [Metallb](https://metallb.universe.tf/) on your cluster. (Tested with `v0.8.3`)

5. Create BareMetal OpenWISP kubernetes requirements: `kubectl create -f BareMetal.yml`

6. Your system is ready, now you can move to the installation of OpenWISP on kubernetes [here](KUBERNETES.md).
