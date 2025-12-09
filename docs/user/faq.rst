######################
 Docker OpenWISP FAQs
######################

.. contents:: **Table of Contents**:
    :depth: 1
    :local:

***********************************************************
 1. Setup fails, it couldn't find the images on DockerHub?
***********************************************************

Answer: The setup requires following ports and destinations to be
unblocked, if you are using a firewall or any external control to block
traffic, please whitelist:

= ====== ======== ========== ====================== =====================================
\ UserId Protocol DstPort    Destination            Process
= ====== ======== ========== ====================== =====================================
1 0      tcp,udp  443,53     gitlab.com             ``/usr/bin/dockerd``
2 0      tcp,udp  443,53     registry.gitlab.com    ``/usr/bin/dockerd``
3 0      tcp,udp  443,53     storage.googleapis.com ``/usr/bin/dockerd``
4 0      udp      53         registry.gitlab.com    ``/usr/bin/docker``
5 0      tcp,udp  443,53     github.com             ``/usr/lib/git-core/git-remote-http``
6 0      tcp      443,80     172.18.0.0/16          ``/usr/bin/docker-proxy``
7 0      udp      1812, 1813 172.18.0.0/16          ``/usr/bin/docker-proxy``
8 0      tcp      25         172.18.0.0/16          ``/usr/bin/docker-proxy``
= ====== ======== ========== ====================== =====================================

***********************************************************
 2. Makefile failed without any information, what's wrong?
***********************************************************

Answer: You are using an old version of a requirement, please consider
upgrading:

.. code-block:: bash

    $ git --version
    git version 2.25.1
    $ docker --version
    Docker version 27.0.2, build 912c1dd
    $ docker compose version
    Docker Compose version v2.28.1
    $ make --version
    GNU Make 4.2.1
    $ bash --version
    GNU bash, version 5.0.3(1)-release (x86_64-pc-linux-gnu)
    $ uname -v # kernel-version
    #1 SMP Debian 4.19.181-1 (2021-03-19)

***********************************************************
 3. Can I run the containers as the ``root`` or ``docker``
***********************************************************

No, please do not run the Docker containers as these users.

Ensure you use a less privileged user and tools like ``sudo`` or ``su`` to
escalate privileges during the installation phase.
