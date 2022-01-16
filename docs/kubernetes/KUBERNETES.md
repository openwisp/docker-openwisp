# Common Kubernetes Setup

[![Gitter](https://img.shields.io/gitter/room/openwisp/general.svg)](https://gitter.im/openwisp/dockerize-openwisp)
[![Support](https://img.shields.io/badge/support-orange.svg)](http://openwisp.org/support.html)

1. Configure your domain with following A records, point your static IP to:

```
  dashboard.<your.domain>    --Public-IP--
  api.<your.domain>          --Public-IP--
  radius.<your.domain>       --Public-IP--
```

2. (Optional) Postfix mail relay server (Example: Mailjet, Pepipost, Sendgrid, Mandrill)

3. Customization:

   - In `ConfigMap.yml`: You need to change the values according to your cluster. You can set any of the variables from the [list here](docs/ENV.md) to trailor setup to your requirements.

4. Apply to Kubernetes Cluster:

```bash
kubectl apply -f ConfigMap.yml
kubectl apply -f Storage.yml
kubectl apply -f Service.yml
kubectl apply -f Deployment.yml
```

5. Each Loadbalancer creates/assigns an IP address, add it to your DNS:

```
freeradius.<your.domain>    -LoadBalancer-IP-
openvpn.<your.domain>       -LoadBalancer-IP-
```

**NOTE: Containers will take a little while to start working. You can see the status on the Web UI or on CLI by `kubectl get all` command.**
