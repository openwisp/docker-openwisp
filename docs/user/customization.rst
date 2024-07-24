Advanced Customization
======================

This page describes advanced customization options for the OpenWISP Docker
images.

The table of contents below provides a quick overview of the specific
areas that can be customized.

.. contents::
    :depth: 1
    :local:

Creating the ``customization`` Directory
----------------------------------------

The following commands will create the directory structure required for
adding customizations. Execute these commands in the same location as the
``docker-compose.yml`` file.

.. code-block:: shell

    mkdir -p customization/configuration/django
    touch customization/configuration/django/__init__.py
    touch customization/configuration/django/custom_django_settings.py
    mkdir -p customization/theme

You can also refer to the `directory structure of Docker OpenWISP
repository
<https://github.com/openwisp/docker-openwisp/tree/master/customization>`__
for an example.

.. _docker_custom_django_settings:

Supplying Custom Django Settings
--------------------------------

The ``customization/configuration/django`` directory created in the
previous section is mounted at ``/opt/openwisp/openwisp/configuration`` in
the ``dashboard``, ``api``, ``celery``, ``celery_monitoring`` and
``celerybeat`` containers.

You can specify additional Django settings (e.g. SMTP configuration) in
the ``customization/configuration/django/custom_django_settings.py`` file.
OpenWISP will include these settings during the startup phase.

You can also put additional files in
``customization/configuration/django`` that need to be mounted at
``/opt/openwisp/openwisp/configuration`` in the containers.

Supplying Custom CSS and JavaScript Files
-----------------------------------------

If you want to use your custom styles, add custom JavaScript you can
follow the following guide.

1. Read about the option :ref:`openwisp_admin_theme_links`. Please make
   `ensure the value you have enter is a valid JSON
   <https://jsonlint.com/>`__ and add the desired JSON in ``.env`` file.
   example:

.. code-block:: shell

    # OPENWISP_ADMIN_THEME_LINKS = [
    #     {
    #         "type": "text/css",
    #         "href": "/static/custom/css/custom-theme.css",
    #         "rel": "stylesheet",
    #         "media": "all",
    #     },
    #     {
    #         "type": "image/x-icon",
    #         "href": "/static/custom/bootload.png",
    #         "rel": "icon",
    #     },
    #     {
    #         "type": "image/svg+xml",
    #         "href": "/static/ui/openwisp/images/openwisp-logo-small.svg",
    #         "rel": "icons",
    #     },
    # ]
    # JSON string of the above configuration:
    OPENWISP_ADMIN_THEME_LINKS='[{"type": "text/css", "href": "/static/custom/css/custom-theme.css", "rel": "stylesheet", "media": "all"}, {"type": "image/x-icon", "href": "/static/custom/bootload.png", "rel": "icon"}, {"type": "image/svg+xml", "href": "/static/ui/openwisp/images/openwisp-logo-small.svg", "rel": "icons"}]'

2. Create your custom CSS / Javascript file in ``customization/theme``
   directory created in the above section. E.g.
   ``customization/theme/static/custom/css/custom-theme.css``.
3. Start the nginx containers.

.. note::

    1. You can edit the styles / JavaScript files now without restarting
       the container, as long as file is in the correct place, it will be
       picked.
    2. You can create a ``maintenance.html`` file inside the ``customize``
       directory to have a custom maintenance page for scheduled downtime.

Supplying Custom uWSGI configuration
------------------------------------

By default, you can only configure :ref:`"processes", "threads" and
"listen" settings of uWSGI using environment variables
<docker_uwsgi_env>`. If you want to configure more uWSGI settings, you can
supply your uWSGI configuration by following these steps:

1. Create the uWSGI configuration file in the
   ``customization/configuration`` directory. For the sake of this
   example, let's assume the filename is ``custom_uwsgi.ini``.
2. In ``dashboard`` and ``api`` services of ``docker-compose.yml``, add
   volumes as following

.. code-block:: yaml

    services:
      dashboard:
        ... # other configuration
        volumes:
          ... # other volumes
          - ${PWD}/customization/configuration/custom_uwsgi.ini:/opt/openwisp/uwsgi.ini:ro
      api:
        ... # other configuration
        volumes:
          ... # other volumes
          - ${PWD}/customization/configuration/custom_uwsgi.ini:/opt/openwisp/uwsgi.ini:ro

.. _docker_nginx:

Supplying Custom Nginx Configurations
-------------------------------------

Docker
~~~~~~

1. Create nginx your configuration file.
2. Set ``NGINX_CUSTOM_FILE`` to ``True`` in ``.env`` file.
3. Mount your file in ``docker-compose.yml`` as following:

.. code-block:: yaml

    nginx:
      ...
      volumes:
          ...
          PATH/TO/YOUR/FILE:/etc/nginx/nginx.conf
      ...

Kubernetes
~~~~~~~~~~

1. Create nginx your configuration file. Files in
   ``build/openwisp-nginx/`` may by helpful.
2. Set ``NGINX_CUSTOM_FILE`` to ``True``.
3. Create configmap from file: ``kubectl create configmap
   nginx-file-config --from-file PATH/TO/YOUR/FILE``
4. Add your config to ``openwisp-nginx`` object:

.. code-block:: yaml

    ...
    metadata:
      name: openwisp-nginx
    spec:
      ...
      spec:
        containers:
          ...
          volumeMounts:
            ...
            - name: "nginx-file-config"
              mountPath: "/etc/nginx/nginx.conf"
              subPath: "nginx.conf"
        volumes:
            ...
            - name: "nginx-file-config"
              configMap:
                name: "nginx-file-config"

.. _docker_freeradius:

Supplying Custom Freeradius Configurations
------------------------------------------

Note: ``/etc/raddb/clients.conf``, ``/etc/raddb/radiusd.conf``,
``/etc/raddb/sites-enabled/default``, ``/etc/raddb/mods-enabled/``,
``/etc/raddb/mods-available/`` are the default files you may want to
overwrite and you can find all of default files in
``build/openwisp_freeradius/raddb``. The following are examples for
including custom ``radiusd.conf`` and ``sites-enabled/default`` files.

.. _docker-1:

Docker
~~~~~~

1. Create file configuration files that you want to edit / add to your
   container.
2. Mount your file in ``docker-compose.yml`` as following:

.. code-block:: yaml

    nginx:
      ...
      volumes:
          ...
          PATH/TO/YOUR/RADIUSD:/etc/raddb/radiusd.conf
          PATH/TO/YOUR/DEFAULT:/etc/raddb/sites-enabled/default
      ...

Kubernetes
~~~~~~~~~~

1. Create configmap from file: ``kubectl create configmap
   freeradius-dir-files --from-file PATH/TO/YOUR/RADIUSD --from-file
   PATH/TO/YOUR/DEFAULT``
2. Add your config to ``openwisp-freeradius`` object:

.. code-block:: yaml

    ...
    metadata:
      name: openwisp-freeradius
    spec:
      ...
      spec:
        containers:
          ...
          volumeMounts:
            ...
            - name: "freeradius-dir-files"
              mountPath: "/etc/raddb/radiusd.conf"
              subPath: "radiusd.conf"
            - name: "freeradius-dir-files"
              mountPath: "/etc/raddb/sites-enabled/default"
              subPath: "default"
        volumes:
            ...
            - name: "freeradius-dir-files"
              configMap:
                name: "freeradius-dir-files"

Supplying Custom Python Source Code
-----------------------------------

You can build the images and supply custom python source code by creating
a file named ``.build.env`` in the root of the repository, then set the
variables inside ``.build.env`` file in ``<variable>=<value>`` format.
Multiple variable should be separated in newline.

These are the variables that can be changed:

- ``OPENWISP_MONITORING_SOURCE``
- ``OPENWISP_FIRMWARE_SOURCE``
- ``OPENWISP_CONTROLLER_SOURCE``
- ``OPENWISP_NOTIFICATION_SOURCE``
- ``OPENWISP_TOPOLOGY_SOURCE``
- ``OPENWISP_RADIUS_SOURCE``
- ``OPENWISP_IPAM_SOURCE``
- ``OPENWISP_USERS_SOURCE``
- ``OPENWISP_UTILS_SOURCE``
- ``DJANGO_X509_SOURCE``
- ``DJANGO_SOURCE``

For example, if you want to supply your own Django and :doc:`OpenWISP
Controller </controller/index>` source, your ``.build.env`` should be
written like this:

.. code-block:: shell

    DJANGO_SOURCE=https://github.com/<username>/Django/tarball/master
    OPENWISP_CONTROLLER_SOURCE=https://github.com/<username>/openwisp-controller/tarball/master

Disabling Services
------------------

- ``openwisp-dashboard``: You cannot disable the openwisp-dashboard. It is
  the heart of OpenWISP and performs core functionalities.
- ``openwisp-api``: You cannot disable the openwisp-api. It is required
  for interacting with your devices.
- ``openwisp-websocket``: Removing this container will cause the system to
  not able to update real-time location for mobile devices.

If you want to disable a service, you can simply remove the container for
that service, however, there are additional steps for some images:

- ``openwisp-network-topology``: Set the ``USE_OPENWISP_TOPOLOGY``
  variable to ``False``.
- ``openwisp-firmware-upgrader`` : Set the ``USE_OPENWISP_FIRMWARE``
  variable to ``False``.
- ``openwisp-monitoring`` : Set the ``USE_OPENWISP_MONITORING`` variable
  to ``False``.
- ``openwisp-radius`` : Set the ``USE_OPENWISP_RADIUS`` variable to
  ``False``.
- ``openwisp-postgres``: If you are using a separate database instance,

  - Ensure your database instance is reachable by the following OpenWISP
    containers: ``openvpn``, ``freeradius``, ``celerybeat``, ``celery``,
    ``celery_monitoring``, ``websocket``, ``api``, ``dashboard``.
  - Ensure your database server supports GeoDjango. (Install PostGIS for
    PostgreSQL)
  - Change the :ref:`PostgreSQL Database Setting
    <docker_postgresql_db_settings>` to point to your instances, if you
    are using SSL, remember to set ``DB_SSLMODE``, ``DB_SSLKEY``,
    ``DB_SSLCERT``, ``DB_SSLROOTCERT``.
  - If you are using SSL, remember to mount volume containing the
    certificates and key in all the containers which contact the database
    server and make sure that the private key permission is ``600`` and
    owned by ``root:root``.
  - In your database, create database with name ``<DB_NAME>``.

- ``openwisp-postfix``:

  - Ensure your SMTP instance reachable by the OpenWISP containers.
  - Change the :ref:`email configuration variables <email_host>` to point
    to your instances.
