# Google Kubernetes Engine

[![Gitter](https://img.shields.io/gitter/room/openwisp/general.svg)](https://gitter.im/openwisp/dockerize-openwisp)
[![Support](https://img.shields.io/badge/support-orange.svg)](http://openwisp.org/support.html)

The following are steps of a sample deployment on a kubernetes cluster on Google Kubernetes Engine. All the files are present in `deployment-examples/kubernetes/` directory of this repository.
The following assumes the reader knows basics of kubernetes, docker & Google Cloud Platform.
The steps where performed on master version-1.13.

1. Setup External IP: Create a global static IP adress named `openwisp-http-loadbalancer-ip` and two IP addresses in the region where you want to create your kubernetes cluster.

2. Create your cluster (Minimum 4 instances of g1-small are required for the deployment)

3. Create a compute disk named `openwisp-disk`. This will be your storage disk which will store all the persistent files like user uploaded files and user database.

4. You will need "Compute Engine API - Backend services" to be atleast 7 for this deployment, please request more quota if required. (By default backend quota is 5)

5. In `GooglePersistentVolume.yml`: Change storage size according to your needs and create Persistent Volumes for OpenWISP:

```bash
kubeapply --create GooglePersistentVolume.yml
```

6. Exec into the nfs-server container and execute the following command:

```bash
mkdir /exports/postfix /exports/html /exports/media /exports/static /exports/postgres
```

7. Your system is ready, now you can move to the installation of OpenWISP on kubernetes [here](KUBERNETES.md).
