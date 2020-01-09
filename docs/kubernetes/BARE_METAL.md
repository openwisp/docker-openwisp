# Bare Metal Kubernetes

[![Gitter](https://img.shields.io/gitter/room/openwisp/general.svg)](https://gitter.im/openwisp/dockerize-openwisp)
[![Support](https://img.shields.io/badge/support-orange.svg)](http://openwisp.org/support.html)

The following are steps of a sample deployment on a kubernetes cluster. All the files are present in `deployment-examples/kubernetes/` directory of this repository.
The following assumes the reader knows basics of kubernetes & docker.
The steps where performed on master version-1.13.

1. Setup a Kubernetes Cluster

   1.1. A guide for setting up the cluster on bare-metal machines is available [here](https://blog.alexellis.io/kubernetes-in-10-minutes/) and the guide to get started with kubernetes-dashboard (Web UI) is available [here](https://github.com/kubernetes/dashboard).

2. [Setup nfs-server](https://vitux.com/install-nfs-server-and-client-on-ubuntu/):

   2.1 Install NFS requirements on all the nodes: `sudo apt install nfs-kernel-server nfs-common`

   2.2 Setup storage directory:

   ```bash
   sudo mkdir -p /exports
   sudo chown nobody: /exports
   ```

   2.3 To configure export directory, inside `/etc/exports`:

   ```bash
   # Change * to your server IP range for security
   /exports    *(rw,sync,no_root_squash,no_subtree_check,no_all_squash,insecure)
   ```

   2.4 Export the directories `sudo exportfs -rav`

   2.5 On all the nodes, mount the NFS folder: `sudo mount <nfs-server-ip-address>:/exports /exports`.

3. Setup dynamic kubernetes NFS server:

    3.1 You may need to [setup helm](https://helm.sh/docs/using_helm/).

    3.2 Install NFS Server: `helm install nfs-server-provisioner stable/nfs-server-provisioner`

5. In `deployment-examples/kubernetes/.env`: Change storage size according to your needs and create Persistent Volumes for OpenWISP:

```bash
kubeapply --create BarePersistentVolume.yml
```

6. Your system is ready, now you can move to the installation of OpenWISP on kubernetes [here](KUBERNETES.md).
