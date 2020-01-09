# Common Kubernetes Setup

[![Gitter](https://img.shields.io/gitter/room/openwisp/general.svg)](https://gitter.im/openwisp/dockerize-openwisp)
[![Support](https://img.shields.io/badge/support-orange.svg)](http://openwisp.org/support.html)

1. Configure your domain with following A records:

```
dashboard.<your.domain>     GLOBAL-IP
controller.<your.domain>    GLOBAL-IP
radius.<your.domain>        GLOBAL-IP
topology.<your.domain>      GLOBAL-IP
freeradius.<your.domain>    REGIONAL-IP-1
openvpn.<your.domain>       REGIONAL-IP-2
```

2. Postfix mail relay server (Example: Mailjet, Pepipost, Sendgrid, Mandrill)

3. [Setup Certificate manager](https://cert-manager.io/docs/installation/kubernetes/#installing-with-regular-manifests) for SSL certificates:

```bash
kubectl create namespace cert-manager
kubectl apply --validate=false -f https://github.com/jetstack/cert-manager/releases/download/v0.12.0/cert-manager.yaml
```

4. Customization:

    4.1 In `deployment-examples/kubernetes/.env`: Change the email address and the domain name to your domain.

    4.2 In `ConfigMap.yml`: You need to change the values according to your cluster. You can set any of the variables from the [list here](docs/ENV.md) to trailor setup to your requirements.

5. Apply to Kubernetes Cluster: You need to apply all the files in the `deployment-examples/kubernetes/` directory to your cluster. Some `Deployments` are dependant on other components, so it'll be helpful to apply them at last. This is the recommended order (let the services in the previous step be ready before applying the next YAML file.):

```bash
kubeapply ConfigMap.yml
kubeapply Service.yml
kubeapply Deployment.yml
kubeapply Ingress.yml
kubeapply CertManager.yml
```

**NOTE: Containers will take a little while to start working. You can see the status on the Web UI or on CLI by `kubectl get all` command.**
