# Google Kubernetes Engine

[![Gitter](https://img.shields.io/gitter/room/openwisp/general.svg)](https://gitter.im/openwisp/dockerize-openwisp)
[![Support](https://img.shields.io/badge/support-orange.svg)](http://openwisp.org/support.html)

The following are steps of a sample deployment on a kubernetes cluster on Google Kubernetes Engine. All the files are present in `deploy/examples/kubernetes/` directory of this repository.
The following assumes the reader knows basics of kubernetes, docker & Google Cloud Platform.
The steps are tested on master version-1.14.9

1. Setup External IP: Create a global static IP adress named `openwisp-http-loadbalancer-ip`.

2. Create a compute disk named `openwisp-disk`. This will be your storage disk which will store all the persistent files like user uploaded files and user database.

3. Create your cluster (Minimum 4 instances of g1-small are required for the deployment)

4. You will need "Compute Engine API - Backend services" to be atleast 7 for this deployment, please request more quota if required. (By default backend quota is 5)

5. Create GoogleCloud OpenWISP kubernetes requirements: `kubectl create -f GoogleCloud.yml`

6. Your system is ready, now you can move to the installation of OpenWISP on kubernetes [here](KUBERNETES.md).

7. [Setup Certificate manager](https://cert-manager.io/docs/installation/kubernetes/#installing-with-regular-manifests) for SSL certificates:

```bash
kubectl create namespace cert-manager
kubectl apply --validate=false -f https://github.com/jetstack/cert-manager/releases/download/v0.12.0/cert-manager.yaml
```

8. In `CertManager.yml`: Change the email address & the domain name and create `kubectl create -f CertManager.yml`.

9. When the certificate is ready(check: `kubectl get certificate`), patch the Ingress with tls information:

```bash
kubectl patch ingress/openwisp-http-ingress \
    --patch '{
        "spec": {
            "tls": [
                {
                "hosts": [
                    "dasboard.openwisp.org",
                    "api.openwisp.org",
                    "radius.openwisp.org"
                ],
                "secretName": "openwisp-tls-secret"
                }
            ]
        }
    }'
```
