# Docker-OpenWISP 

[![Build Status](https://travis-ci.org/openwisp/docker-openwisp.svg?branch=master)](https://travis-ci.org/openwisp/docker-openwisp)

Easily running OpenWISP on your kubernetes cluster.

![kubernetes](https://i.ibb.co/rGpLq4y/ss1.png)
The sample files for deployment on kubernetes are available in the `kubernetes/` directory.

Images are available on docker hub and can be pulled from the following links:
- OpenWISP Base - `openwisp/openwisp-base:latest`
- OpenWISP Dashboard - `openwisp/openwisp-dashboard:latest`
- OpenWISP Radius - `openwisp/openwisp-radius:latest`
- OpenWISP Controller - `openwisp/openwisp-controller:latest`
- OpenWISP Network Topology - `openwisp/openwisp-topology:latest`
- OpenWISP Nginx - `openwisp/openwisp-nginx:latest`

**Test using:**
1. [Kubernetes](https://github.com/atb00ker/dockerize-openwisp#kubernetes)
2. [Docker Compose](https://github.com/atb00ker/dockerize-openwisp#docker-compose)

### Kubernetes

1. (optional) Setup a Kubernetes Cluster: A guide for setting up the cluster on bare-metal machines is available [here](https://blog.alexellis.io/kubernetes-in-10-minutes/) and the guide to get started with kubernetes-dashboard (Web UI) is available [here](https://github.com/kubernetes/dashboard).

2. Set external IP: You need to set the external IP for all the services. This is the IP on which you will access your openwisp applications. All the services are in [this file](https://github.com/atb00ker/dockerize-openwisp/blob/master/kubernetes/Service.yml). Please do `ctrl+f` to find `172.16.6.2*` and replace with your server's external IP in this file. 

3. (optional) Customization: You can change the settings in the container by changing the environment variables. You can pass the environment variables by changing [this file](https://github.com/atb00ker/dockerize-openwisp/blob/master/kubernetes/ConfigMap.yml). You can add any of the variables from the [list here](https://github.com/atb00ker/dockerize-openwisp/blob/master/.env). 
- The ConfigMap with name `postgres-config` will pass the environment variables only to the postgresql container. 
- The ConfigMap with name `common-config` will pass the environment variables to all the openwisp containers.

4. If you are doing bare-metal setup, follow the steps below to setup nfs-provisioner:

4.1. Install NFS requirements: `sudo apt install nfs-kernel-server nfs-common`

4.2. Setup storage directory:
```
sudo mkdir -p /mnt/kubes
sudo chown nobody: /mnt/kubes
```

4.3. Export the directory file system - inside the `/etc/exports` file add line: `/mnt/kubes    *(rw,sync,no_root_squash,no_subtree_check,no_all_squash,insecure)` and then export `sudo exportfs -rav`

5. `helm install --set storageClass.name=nfs-provisioner --set nfs.server=<ip-address> --set nfs.path=/mnt/kubes stable/nfs-client-provisioner`

6. `helm install --name cert-manager --namespace kube-system stable/cert-manager`

7. Apply to Kubernetes Cluster: You need to apply all the files in the `kubernetes/` directory to your cluster. You can use the Web UI to create new components or you can use `kubectl apply -f <filename>` to apply from CLI. Some `ReplicationControllers` are dependant on other components, so it'll be useful to apply them at last. I recommend to follow this order:
```
$ kubectl apply -f ConfigMap.yml
$ kubectl apply -f ClusterIssuer.yml
$ kubectl apply -f PresistentVolumeClaim.yml
$ kubectl apply -f Service.yml
$ kubectl apply -f Ingress.yml
$ kubectl apply -f ReplicationController.yml
```

NOTE: Wait for a while after every file. Containers will take a little while to boot up. You can see the status on the Web UI or on CLI by `kubectl get all --namespace=default` command. These files have some variables inside them as well.
Read the content of the files before deploying and change according to your needs.

### Docker Compose

Testing on docker-compose is relatively less resource and time consuming.

1. Install docker-compose: `pip install docker-compose`
2. (optional) Congfigure: Manipulate all the values in the .env file as you desire.
3. Pull all the required images to avoid building them. (building images is a time consuming task.)

```bash
docker pull openwisp/openwisp-base:latest
docker pull openwisp/openwisp-dashboard:latest
docker pull openwisp/openwisp-radius:latest
docker pull openwisp/openwisp-controller:latest
docker pull openwisp/openwisp-topology:latest
docker pull openwisp/openwisp-nginx:latest
```

4. Run containers: Inside root of the repository, run `docker-compose up`. It will take a while for the containers to start up. (~1 minute)

5. When the containers are ready, you can test them out by going to the domain name that you've set for the modules. (if the domains used are not registered domains, you'll need to add them to the /etc/hosts)

Note:
   - Default username & password are `admin`.
   - Default domains are: dashboard.openwisp.org, controller.openwisp.org, radius.openwisp.org and topology.openwisp.org.
   - You may want to add the domains in your hosts file, command: `echo "127.0.0.1 dashboard.openwisp.org controller.openwisp.org radius.openwisp.org topology.openwisp.org" >> /etc/hosts/`

**Note(`pipenv`):** Remember changing the values in `.env` file does nothing because `.env` is also a special file in `pipenv`, you need to change the values in `.env` file then re-activate environment to ensure that the changes reflect.

## Build (Developers)

Guide to build images again with modification or with different environment variables.

##### Steps:

1. Install docker-compose
2. (optional) Congfigure: Manipulate all the values in the .env file as you desire.
3. Make desired changes in the Dockerfiles.
4. In the root of the repository, run `make`.
5. After that do `docker-compose up`, when the containers are ready, you can test them out by going to the domain name of the modules.

Note:
   - Default username & password are `admin`.
   - Default domains are: dashboard.openwisp.org, controller.openwisp.org, radius.openwisp.org and topology.openwisp.org.
   - You may want to add the domains in your hosts file, command: `echo "127.0.0.1 dashboard.openwisp.org controller.openwisp.org radius.openwisp.org topology.openwisp.org" >> /etc/hosts/`
