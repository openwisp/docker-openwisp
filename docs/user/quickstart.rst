Quick Start Guide
=================

This page explains how to deploy OpenWISP using the docker images provided
by Docker OpenWISP.

.. contents:: **Table of Contents**:
    :depth: 1
    :local:

Available Images
----------------

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

.. include:: ../partials/updating-host-file.rst

Auto Install
------------

The ``auto-install.sh`` script can be used to quickly install a simple
instance of OpenWISP on your server. It will install the required system
dependencies and starts docker containers.

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

This script prompts the user for basic configuration parameters required
to set up OpenWISP. Below are the prompts and their descriptions:

- **OpenWISP Version:** Version of OpenWISP you want to install. If you
  leave this blank, the latest released version will be installed.
- **.env File Path:** Path to an existing :doc:`".env" file <settings>`
  file if you have one. If you leave this blank, the script will continue
  prompting for additional configuration.
- **Domains:** The fully qualified domain names for the :ref:`Dashboard
  <dashboard_domain>`, :ref:`API <api_domain>`, and :ref:`OpenVPN
  <vpn_domain>` services.
- **Site Manager Email:** Email address of the site manager. This email
  address will serve as the default sender address for all email
  communications from OpenWISP.
- **Let's Encrypt Email:** Email address for Let's Encrypt to use for
  certificate generation. If you leave this blank, a self-signed
  certificate will be generated.

Run the following commands to download the auto-install script and execute
it:

.. code-block:: bash

    curl https://raw.githubusercontent.com/openwisp/docker-openwisp/master/deploy/auto-install.sh -o auto-install.sh
    sudo bash auto-install.sh

The auto-install script maintains a log, which is useful for debugging or
checking the real-time output of the script. You can view the log by
running the following command:

.. code-block:: bash

    tail -n 50 -f /opt/openwisp/autoinstall.log

The auto-install script can be used to upgrade installations that were
originally deployed using this script. You can upgrade your installation
by using the following command

.. code-block:: bash

    sudo bash auto-install.sh --upgrade

.. note::

    - If you're having any installation issues with the ``latest``
      version, you can try auto-installation with the ``edge`` version,
      which has images built on the current master branch.
    - Still facing errors while installation? Please :doc:`read the FAQ
      <faq>`.

Using Docker Compose
--------------------

This setup is suitable for single-server setup requirements. It is quicker
and requires less prior knowledge about OpenWISP & networking.

1. Install requirements:

   .. code-block:: bash

       sudo apt -y update
       sudo apt -y install git docker.io make
       # Please ensure docker is installed properly and the following
       # command show system information. In most machines, you'll need to
       # add your user to the `docker` group and re-login to the shell.
       docker info

2. Setup repository:

   .. code-block:: bash

       git clone https://github.com/openwisp/docker-openwisp.git
       cd docker-openwisp

3. Configure:

   Please refer to the :doc:`settings` and :doc:`customization` pages to
   configure any aspect of your OpenWISP instance.

   Make sure to change the values for :ref:`essential
   <docker_essential_env>` and :ref:`security <docker_security_env>`
   variables.

4. Deploy:

   Use the ``make start`` command to pull images and start the containers.

   .. note::

       If you want to shutdown services for maintenance or any other
       purposes, please use ``make stop``.

If you are facing errors during the installation process, :doc:`read the
FAQ <faq>` for known issues.
