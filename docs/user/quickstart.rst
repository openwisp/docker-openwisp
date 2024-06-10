Deploying OpenWISP Using Docker
===============================

Images Available
----------------

======= =============================
Version Corresponding Ansible Version
======= =============================
0.1.0a2 0.9.0
0.1.0a3 0.12.0
0.1.0a4 0.12.0+
0.1.0a5 0.13.1
0.1.0a6 0.13.2+
======= =============================

\* Roughly the same features would be available but it's not an exact
one-to-one mapping.

The images are hosted on `Docker Hub
<https://hub.docker.com/u/openwisp>`__ and `GitLab Container Registry
<https://gitlab.com/openwisp/docker-openwisp/container_registry>`__.

Image Tags
~~~~~~~~~~

All images are tagged using the following convention:

====== =============================================
Tag    Software Version
====== =============================================
latest Images built on the **latest git tag**
edge   Images built on the **current master branch**
====== =============================================

Quick Setup
-----------

The ``auto-install.sh`` script can be used to quickly install a simple
instance of OpenWISP on your server.

.. raw:: html

    <p>
        <iframe width="560" height="315"
            src="https://www.youtube.com/embed/LLbsKP79MzE?si=XzJ3YX_ueutr9--f"
            frameborder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
            referrerpolicy="strict-origin-when-cross-origin"
            allowfullscreen
        ></iframe>
    </p>

If you have created a :doc:`".env" file <settings>` to configure your
instance, then you can use it with the script otherwise.

**It asks 5 questions for application configuration, 3 of them are domain
names.** The dashboard, api & openvpn can be setup on different domain,
**please ensure the domains you enter point to your server**. The
remaining **2 questions are email id** for site manager email (used by
django to send application emails) and letsencrypt (used by `certbot
<https://certbot.eff.org/>`__ to issue https certs on this address.)

To get started, run the following command:

.. code-block:: bash

    curl https://raw.githubusercontent.com/openwisp/docker-openwisp/master/deploy/auto-install.sh -o setup.sh
    sudo bash setup.sh
    # If you are upgrading from an older version setup by this script use
    # sudo bash setup.sh --upgrade
    # For more information
    # sudo bash setup.sh --help

To get a real-time streaming output of autoinstall logs, run the following
command:

.. code-block:: bash

    tail -n 50 -f /opt/openwisp/autoinstall.log

**Notes:**

- If you're having any installation issues with the ``latest`` version,
  you can try auto-installation with the ``edge`` version, which has
  images built on the current master branch.
- Still facing errors while installation? Please :doc:`read the FAQ
  <faq>`.

Using ``docker-compose``
------------------------

This setup is suitable for single-server setup requirements. It is quicker
and requires less prior knowledge about OpenWISP & networking.

1. Install requirements:

       .. code-block:: bash

           sudo apt -y update
           sudo apt -y install git docker.io docker-compose make
           # Please ensure docker is installed properly and the following
           # command show system information. In most machines, you'll need to
           # add your user to the `docker` group and re-login to the shell.
           docker info

2. Setup repository:

       .. code-block:: bash

           git clone https://github.com/openwisp/docker-openwisp.git
           cd docker-openwisp

3. Configure:

Please follow the :doc:`environment variable documentation <settings>` and
customize your deployment of OpenWISP. Remember to change the values for
:ref:`essential <docker_essential_env>` and :ref:`security
<docker_security_env>` variables.

4. Deploy: ``make start``

.. note::

    If you want to shutdown services for maintenance or any other
    purposes, please use ``make stop``.

If you are facing errors while installation, then :doc:`read the FAQ
<faq>` for known issues.
