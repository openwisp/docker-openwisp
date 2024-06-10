Kubernetes
==========

Setup on kubernetes is complex and requires prior knowledge about linux
systems, kubernetes, docker & OpenWISP. However, it provides scalability
for very large networks.

Useful commands for startup and readiness probes which are provided by the
images:

- startup probe example: ``test $(ps aux | grep -c uwsgi) -ge 2``
- readiness probe example: ``python services.py uwsgi_status
  "127.0.0.1:8001"``

Bare Metal Kubernetes
---------------------

The following are steps of a sample deployment on a kubernetes cluster.
All the files are present in ``deploy/examples/kubernetes/`` directory of
this repository. The following assumes the reader knows basics of
kubernetes & docker. The steps where performed on master version-1.14.

1. `Setup a Kubernetes Cluster
   <https://blog.alexellis.io/kubernetes-in-10-minutes/>`__.
2. Make sure to install ``nfs-common`` on all your nodes.
3. Add label to the node where you want to save the data: ``kubectl label
   nodes <node-name> volume=nfs-server``
4. Setup `Metallb <https://metallb.universe.tf/>`__ on your cluster.
   (Tested with ``v0.8.3``)
5. Create BareMetal OpenWISP kubernetes requirements: ``kubectl create -f
   BareMetal.yml``
6. Your system is ready, now you can move to the installation of OpenWISP
   on kubernetes :ref:`here <common_kubernetes_setup>`.

Google Kubernetes Engine
------------------------

The following are steps of a sample deployment on a kubernetes cluster on
Google Kubernetes Engine. All the files are present in
``deploy/examples/kubernetes/`` directory of this repository. The
following assumes the reader knows basics of kubernetes, docker & Google
Cloud Platform. The steps are tested on master version-1.14.9

1. Setup External IP: Create a global static IP address named
   ``openwisp-http-loadbalancer-ip``.
2. Create a compute disk named ``openwisp-disk``. This will be your
   storage disk which will store all the persistent files like user
   uploaded files and user database.
3. Create your cluster (Minimum 4 instances of g1-small are required for
   the deployment)
4. You will need “Compute Engine API - Backend services” to be atleast 7
   for this deployment, please request more quota if required. (By default
   backend quota is 5)
5. Create GoogleCloud OpenWISP kubernetes requirements: ``kubectl create
   -f GoogleCloud.yml``
6. Your system is ready, now you can move to the installation of OpenWISP
   on kubernetes :ref:`here <common_kubernetes_setup>`.
7. `Setup Certificate manager
   <https://cert-manager.io/docs/installation/kubernetes/#installing-with-regular-manifests>`__
   for SSL certificates:

   .. code-block:: bash

       kubectl create namespace cert-manager
       kubectl apply --validate=false -f https://github.com/jetstack/cert-manager/releases/download/v0.12.0/cert-manager.yaml

8. In ``CertManager.yml``: Change the email address & the domain name and
   create ``kubectl create -f CertManager.yml``.
9. When the certificate is ready(check: ``kubectl get certificate``),
   patch the Ingress with tls information:

   .. code-block:: bash

       kubectl patch ingress/openwisp-http-ingress \
          --patch '{
             "spec": {
                   "tls": [
                      {
                      "hosts": [
                         "dasboard.openwisp.org",
                         "api.openwisp.org",
                      ],
                      "secretName": "openwisp-tls-secret"
                      }
                   ]
             }
          }'

.. _common_kubernetes_setup:

Common Kubernetes Setup
-----------------------

1. Configure your domain with following A records, point your static IP
   to:

   .. code-block:: text

       dashboard.<your.domain>    --Public-IP--
       api.<your.domain>          --Public-IP--

2. (Optional) Postfix mail relay server (Example: Mailjet, Pepipost,
   Sendgrid, Mandrill)
3. Customization:
       - In ``ConfigMap.yml``: You need to change the values according to
         your cluster. You can set any of the variables from the
         :doc:`list here <settings>` to trailor setup to your
         requirements.
4. Apply to Kubernetes Cluster:

   .. code-block:: bash

       kubectl apply -f ConfigMap.yml
       kubectl apply -f Storage.yml
       kubectl apply -f Service.yml
       kubectl apply -f Deployment.yml

5. Each Loadbalancer creates/assigns an IP address, add it to your DNS:

   .. code-block:: bash

       freeradius.<your.domain>    -LoadBalancer-IP-
       openvpn.<your.domain>       -LoadBalancer-IP-

.. note::

    Containers will take a little while to start working. You can see the
    status on the Web UI or on CLI by ``kubectl get all`` command.
