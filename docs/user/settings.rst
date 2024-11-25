Settings
========

The OpenWISP Docker images are designed for customization. You can easily
modify environment variables to tailor the containers to your needs.

- **Docker Compose:** Simply change the values in the ``.env`` file.

Below are listed the available configuration options divided by section:

.. contents::
    :depth: 1
    :local:

Additionally, you can search for the following prefixes:

- ``OPENWISP_``: OpenWISP application settings.
- ``DB_``: PostgreSQL Database settings.
- ``INFLUXDB_``: InfluxDB settings.
- ``DJANGO_``: Django settings.
- ``EMAIL_``: Email settings (see also ``POSTFIX_``).
- ``POSTFIX_``: Postfix settings (see also ``EMAIL_``).
- ``NGINX_``: Nginx web server settings.
- ``UWSGI_``: uWSGI application server settings.
- ``DASHBOARD_``: Settings specific to the OpenWISP dashboard.
- ``API_``: Settings specific to the OpenWISP API.
- ``X509_``: Configurations related to x509 CA and certificates.
- ``VPN_``: Default VPN and VPN template configurations.
- ``CRON_``: Periodic task configurations.
- ``EXPORT_``: NFS server configurations.

.. _docker_essential_env:

Essential
---------

You will need to adapt these values to get the docker images working
properly on your system.

.. _dashboard_domain:

``DASHBOARD_DOMAIN``
~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Domain on which you want to access OpenWISP dashboard.
- **Valid Values:** Any valid domain.
- **Default:** ``dashboard.example.com``.

.. _api_domain:

``API_DOMAIN``
~~~~~~~~~~~~~~

- **Explanation:** Domain on which you want to access OpenWISP APIs.
- **Valid Values:** Any valid domain.
- **Default:** ``api.example.com``.

.. _vpn_domain:

``VPN_DOMAIN``
~~~~~~~~~~~~~~

- **Explanation:** Valid domain / IP address to reach the OpenVPN server.
- **Valid Values:** Any valid domain or IP address.
- **Default:** ``openvpn.example.com``.

``TZ``
~~~~~~

- **Explanation:** Sets the timezone for the OpenWISP containers.
- **Valid Values:** Find list of timezone database `here
  <https://en.wikipedia.org/wiki/List_of_tz_database_time_zones>`__.
- **Default:** ``UTC``.

``CERT_ADMIN_EMAIL``
~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Required by certbot. Email used for registration and
  recovery contact.
- **Valid Values:** A comma separated list of valid email addresses.
- **Default:** ``example@example.com``.

``SSL_CERT_MODE``
~~~~~~~~~~~~~~~~~

- **Explanation:** Flag to enable or disable HTTPs. If it is set to
  ``Yes``, letsencrypt certificates are automatically fetched with the
  help of certbot and a cronjob to ensure they stay updated is added. If
  it is set to ``SelfSigned``, self-signed certificates are used and
  cronjob for the certificates is set. If set to ``No``, site is
  accessible via HTTP, if set if ``EXTERNAL``, it tells HTTPs is used but
  managed by external tool like loadbalancer / provider. Setting this
  option as ``No`` is not recommended and might break some features, only
  do it when you know what you are doing.
- **Valid Values:** ``External``, ``Yes``, ``SelfSigned``, ``No``.
- **Default:** ``Yes``.

.. _docker_security_env:

Security
--------

Tune these options to strengthen the security of your instance.

``DJANGO_SECRET_KEY``
~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** A random unique string that must be kept secret for
  security reasons. You can generate it with the command: ``python
  build.py get-secret-key`` at the root of the repository to get a key or
  make a random key yourself.
- **Valid Values:** STRING.
- **Default:** ``default_secret_key``

``DJANGO_ALLOWED_HOSTS``
~~~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Used to validate a request's HTTP Host header. The
  default value ``*`` allows all domains. For security, it is recommended
  to specify only trusted domains, such as ``.mydomain.com``. If left
  blank, it defaults to your dashboard's root domain.
- **Valid Values:** Refer to the `Django documentation for ALLOWED_HOSTS
  <https://docs.djangoproject.com/en/4.2/ref/settings/#std-setting-ALLOWED_HOSTS>`_.
- **Default:** Root domain extracted from :ref:`DASHBOARD_DOMAIN`.
- **Example:** ``.openwisp.org,.example.org,www.example.com``.

``OPENWISP_RADIUS_FREERADIUS_ALLOWED_HOSTS``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Default IP address or subnet of your freeradius
  instance.
- **Valid Values:** A comma separated string of valid IP address or IP
  Networks.
- **Default:** ``172.18.0.0/16``.
- **Example:** ``127.0.0.1,192.0.2.20,172.18.0.0/16``.

OpenWISP
--------

Settings for the OpenWISP application and the underlying Django web
framework.

.. note::

    Any OpenWISP Configuration of type ``string``. ``int``, ``bool`` or
    ``json`` is supported and can be used as per the documentation in the
    module.

    If you need to change a Django setting that has a more complex
    datatype, please refer to :ref:`docker_custom_django_settings`.

.. _email_host:

``EMAIL_HOST``
~~~~~~~~~~~~~~

- **Explanation:** Host to be used when connecting to the STMP.
  ``localhost`` or empty string are not allowed.
- **Valid Values:** A valid hostname or IP address.
- **Example:** ``smtp.gmail.com``.
- **Default:** ``postfix``.

``EMAIL_DJANGO_DEFAULT``
~~~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** It is the email address to use for various automated
  correspondence from the site manager(s).
- **Valid Values:** Any valid email address.
- **Default:** ``example@example.com``.

``EMAIL_HOST_PORT``
~~~~~~~~~~~~~~~~~~~

- **Explanation:** Port to use for the SMTP server defined in
  :ref:`EMAIL_HOST`.
- **Valid Values:** INTEGER.
- **Default:** ``25``.

``EMAIL_HOST_USER``
~~~~~~~~~~~~~~~~~~~

- **Explanation:** Username to use for the SMTP server defined in
  :ref:`EMAIL_HOST`. If empty, Django won't attempt authentication.
- **Valid Values:** STRING.
- **Default:** ``""`` (empty string).
- **Example:** ``example@example.com``

``EMAIL_HOST_PASSWORD``
~~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Password to use for the SMTP server defined in
  :ref:`EMAIL_HOST`.. If empty, Django won't attempt authentication.
- **Valid Values:** STRING.
- **Default:** ``""`` (empty string)

``EMAIL_HOST_TLS``
~~~~~~~~~~~~~~~~~~

- **Explanation:** Whether to use a TLS (secure) connection when talking
  to the SMTP server. This is used for explicit TLS connections, generally
  on port 587.
- **Valid Values:** ``True``, ``False``.
- **Default:** ``False``.

``EMAIL_TIMEOUT``
~~~~~~~~~~~~~~~~~

- **Explanation:** Specifies a timeout in seconds used by Django for
  blocking operations like the connection attempt.
- **Valid Values:** INTEGER.
- **Default:** ``10``.

``EMAIL_BACKEND``
~~~~~~~~~~~~~~~~~

- **Explanation:** Email will be sent using this backend.
- **Valid Values:** `Refer to the "Email backends" section on the Django
  documentation
  <https://docs.djangoproject.com/en/4.2/topics/email/#email-backends>`__.
- **Default:** ``djcelery_email.backends.CeleryEmailBackend``.

``DJANGO_X509_DEFAULT_CERT_VALIDITY``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Validity of your x509 cert in days.
- **Valid Values:** INTEGER.
- **Default:** ``1825``

``DJANGO_X509_DEFAULT_CA_VALIDITY``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Validity of your x509 CA in days.
- **Valid Values:** INTEGER.
- **Default:** ``3650``.

``DJANGO_CORS_HOSTS``
~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Hosts for which `CORS
  <https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS>`__. is
  whitelisted.
- **Valid Values:** Comma separated list of CORS domains.
- **Default:** ``http://localhost``
- **Example:** ``https://www.openwisp.org,openwisp.example.org``

``DJANGO_LANGUAGE_CODE``
~~~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Language for your OpenWISP application.
- **Valid Values:** Refer to the `related Django documentation section
  <https://docs.djangoproject.com/en/4.2/ref/settings/#language-code>`__.
- **Default:** ``en-gb``.

``DJANGO_SENTRY_DSN``
~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** `Sentry DSN <https://sentry.io/for/django/>`__.
- **Valid Values:** Your DSN value provided by sentry.
- **Example:** ``https://example@sentry.io/example``.
- **Default:** ``""`` (empty string).

``DJANGO_LEAFET_CENTER_X_AXIS``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** X-axis coordinate of the leaflet default center
  property. `Refer to the django-leaflet docs for more information
  <https://django-leaflet.readthedocs.io/en/latest/templates.html#configuration>`__.
- **Valid Values:** FLOAT.
- **Example:** ``26.357896``.
- **Default:** ``0``.

``DJANGO_LEAFET_CENTER_Y_AXIS``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Y-axis coordinate of the leaflet default center
  property. `Refer to the django-leaflet docs for more information
  <https://django-leaflet.readthedocs.io/en/latest/templates.html#configuration>`__.
- **Valid Values:** FLOAT.
- **Example:** ``127.783809``.
- **Default:** ``0``.

``DJANGO_LEAFET_ZOOM``
~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Default zoom for leaflet. `Refer to the django-leaflet
  docs for more information
  <https://django-leaflet.readthedocs.io/en/latest/templates.html#configuration>`__.
- **Valid Values:** INT (1-16).
- **Default:** ``1``.

``DJANGO_WEBSOCKET_HOST``
~~~~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Host on which Daphne should listen for websocket
  connections.
- **Valid Values:** Any valid domain or IP Address.
- **Default:** ``0.0.0.0``.

``OPENWISP_GEOCODING_CHECK``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Used to check if geocoding is working as expected or
  not.
- **Valid Values:** ``True``, ``False``.
- **Default:** ``True``.

``USE_OPENWISP_CELERY_TASK_ROUTES_DEFAULTS``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Whether the default celery task routes should be used
  by celery. Turn this off if you're defining custom task routing rules.
- **Valid Values:** ``True``, ``False``.
- **Default:** ``True``.

``OPENWISP_CELERY_COMMAND_FLAGS``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Additional flags passed to the command that starts the
  celery worker for the ``default`` queue. It can be used to configure
  different attributes of the celery worker (e.g. auto-scaling,
  concurrency, etc.). Refer to the `celery worker documentation
  <https://docs.celeryq.dev/en/stable/userguide/workers.html#workers-guide>`__
  for more information on configurable properties.
- **Valid Values:** STRING.
- **Default:** ``--concurrency=1``.

``USE_OPENWISP_CELERY_NETWORK``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Whether the dedicated worker for the celery "network"
  queue is enabled. Must be turned on unless there's another server
  running a worker for this queue.
- **Valid Values:** ``True``, ``False``.
- **Default:** ``True``.

``OPENWISP_CELERY_NETWORK_COMMAND_FLAGS``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Additional flags passed to the command that starts the
  celery worker for the ``network`` queue. It can be used to configure
  different attributes of the celery worker (e.g. auto-scaling,
  concurrency, etc.). Refer to the `celery worker documentation
  <https://docs.celeryq.dev/en/stable/userguide/workers.html#workers-guide>`__
  for more information on configurable properties.
- **Valid Values:** STRING.
- **Default:** ``--concurrency=1``

``USE_OPENWISP_CELERY_FIRMWARE``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Whether the dedicated worker for the celery
  ``firmware_upgrader`` queue is enabled. Must be turned on unless there's
  another server running a worker for this queue.
- **Valid Values:** ``True``, ``False``.
- **Default:** ``True``.

``OPENWISP_CELERY_FIRMWARE_COMMAND_FLAGS``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Additional flags passed to the command that starts the
  celery worker for the ``firmware_upgrader`` queue. It can be used to
  configure different attributes of the celery worker (e.g. auto-scaling,
  concurrency, etc.). Refer to the `celery worker documentation
  <https://docs.celeryq.dev/en/stable/userguide/workers.html#workers-guide>`__
  for more information on configurable properties.
- **Valid Values:** STRING
- **Default:** ``--concurrency=1``

``USE_OPENWISP_CELERY_MONITORING``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Whether the dedicated worker for the celery
  ``monitoring`` queue is enabled. Must be turned on unless there's
  another server running a worker for this queue.
- **Valid Values:** ``True``, ``False``.
- **Default:** ``True``.

``OPENWISP_CELERY_MONITORING_COMMAND_FLAGS``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Additional flags passed to the command that starts the
  celery worker for the ``monitoring`` queue. It can be used to configure
  different attributes of the celery worker (e.g. auto-scaling,
  concurrency, etc.). Refer to the `celery worker documentation
  <https://docs.celeryq.dev/en/stable/userguide/workers.html#workers-guide>`__
  for more information on configurable properties.
- **Valid Values:** STRING.
- **Default:** ``--concurrency=1``.

``OPENWISP_CELERY_MONITORING_CHECKS_COMMAND_FLAGS``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Additional flags passed to the command that starts the
  celery worker for the ``monitoring_checks`` queue. It can be used to
  configure different attributes of the celery worker (e.g. auto-scaling,
  concurrency, etc.). Refer to the `celery worker documentation
  <https://docs.celeryq.dev/en/stable/userguide/workers.html#workers-guide>`__
  for more information on configurable properties.
- **Valid Values:** STRING.
- **Default:** ``--concurrency=1``.

``OPENWISP_CUSTOM_OPENWRT_IMAGES``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** JSON representation of the :ref:`related Firmware
  Upgrader setting <openwisp_custom_openwrt_images>`.
- **Valid Values:** JSON
- **Default:** ``None``
- **Example:** ``[{"name": "Name1","label": "Label1","boards": ["TestA",
  "TestB"]}, {"name": "Name2","label": "Label2","boards": ["TestC",
  "TestD"]}]``

``METRIC_COLLECTION``
~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Whether :doc:`/utils/user/metric-collection` is enabled
  or not.
- **Valid Values:** ``True``, ``False``.
- **Default:** ``True``.

``CRON_DELETE_OLD_RADACCT``
~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** (Value in days) Deletes RADIUS accounting sessions
  older than given number of days.
- **Valid Values:** INTEGER.
- **Default:** ``365``.

``CRON_DELETE_OLD_POSTAUTH``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** (Value in days) Deletes RADIUS *post-auth* logs older
  than given number of days.
- **Valid Values:** INTEGER.
- **Default:** ``365``.

``CRON_CLEANUP_STALE_RADACCT``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** (Value in days) Closes stale RADIUS sessions that have
  remained open for the number of specified days.
- **Valid Values:** INTEGER.
- **Default:** ``365``.

``CRON_DELETE_OLD_RADIUSBATCH_USERS``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** (Value in days) Deactivates expired user accounts which
  were created temporarily and have an expiration date set.
- **Valid Values:** INTEGER.
- **Default:** ``365``.

``DEBUG_MODE``
~~~~~~~~~~~~~~

- **Explanation:** Enable Django Debugging. Refer to the `related Django
  documentation section
  <https://docs.djangoproject.com/en/4.2/ref/settings/#debug>`__ for
  details.
- **Valid Values:** ``True``, ``False``.
- **Default:** ``False``.

DJANGO_LOG_LEVEL
~~~~~~~~~~~~~~~~

- **Explanation:** Logging level for Django. Refer to the `related Django
  documentation section
  <https://docs.djangoproject.com/en/4.2/topics/logging/#topic-logging-parts-loggers>`__
  for details.
- **Valid Values:** STRING.
- **Default:** ``ERROR``.

Enabled OpenWISP Modules
------------------------

These options allow to disable the optional OpenWISP modules.

``USE_OPENWISP_TOPOLOGY``
~~~~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Whether the :doc:`Network Topology
  </network-topology/index>` module is enabled or not.
- **Valid Values:** ``True``, ``False``.
- **Default:** ``True``.

``USE_OPENWISP_RADIUS``
~~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Whether the :doc:`RADIUS </radius/index>` module is
  enabled or not.
- **Valid Values:** ``True``, ``False``.
- **Default:** ``True``.

``USE_OPENWISP_FIRMWARE``
~~~~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Whether the :doc:`Firmware Upgrader
  </firmware-upgrader/index>` module is enabled or not.
- **Valid Values:** ``True``, ``False``.
- **Default:** ``True``.

``USE_OPENWISP_MONITORING``
~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Whether the :doc:`Monitoring </monitoring/index>`
  module is enabled or not.
- **Valid Values:** ``True``, ``False``.
- **Default:** ``True``.

.. _docker_postgresql_db_settings:

PostgreSQL Database
-------------------

``DB_NAME``
~~~~~~~~~~~

- **Explanation:** The name of the database to use.
- **Valid Values:** STRING.
- **Default:** ``openwisp_db``.

``DB_USER``
~~~~~~~~~~~

- **Explanation:** The username to use when connecting to the database.
- **Valid Values:** STRING.
- **Default:** ``admin``.

``DB_PASS``
~~~~~~~~~~~

- **Explanation:** The password to use when connecting to the database.
- **Valid Values:** STRING.
- **Default:** ``admin``.

.. _db_engine:

``DB_HOST``
~~~~~~~~~~~

- **Explanation:** Host to be used when connecting to the database.
  ``localhost`` or empty string are not allowed.
- **Valid Values:** A hostname or an IP address.
- **Default:** ``postgres``.

``DB_PORT``
~~~~~~~~~~~

- **Explanation:** The port to use when connecting to the database.
- **Valid Values:** INTEGER.
- **Default:** ``5432``.

``DB_SSLMODE``
~~~~~~~~~~~~~~

- **Explanation:** Postgresql SSLMode option.
- **Valid Values:** Consult the related `PostgreSQL documentation
  <https://www.postgresql.org/docs/14/libpq-ssl.html#LIBPQ-SSL-SSLMODE-STATEMENTS>`__.
- **Default:** ``disable``.

``DB_SSLCERT``
~~~~~~~~~~~~~~

- **Explanation:** Path inside container to a valid client certificate.
- **Valid Values:** STRING.
- **Default:** ``None``.

``DB_SSLKEY``
~~~~~~~~~~~~~

- **Explanation:** Path inside container to valid client private key.
- **Valid Values:** STRING.
- **Default:** ``None``.

``DB_SSLROOTCERT``
~~~~~~~~~~~~~~~~~~

- **Explanation:** Path inside container to a valid server certificate for
  the database.
- **Valid Values:** STRING.
- **Default:** ``None``.

``DB_OPTIONS``
~~~~~~~~~~~~~~

- **Explanation:** Additional database options to connect to the database.
  These options must be supported by your :ref:`DB_ENGINE`.
- **Valid Values:** JSON.
- **Default:** ``{}``.

``DB_ENGINE``
~~~~~~~~~~~~~

- **Explanation:** `Django spatial database backend
  <https://docs.djangoproject.com/en/4.2/ref/contrib/gis/db-api/#module-django.contrib.gis.db.backends>`_
  to use.
- **Valid Values:** Refer to `Spatial Backends on the Django documentation
  <https://docs.djangoproject.com/en/4.2/ref/contrib/gis/db-api/#module-django.contrib.gis.db.backends>`__.
- **Default:** ``django.contrib.gis.db.backends.postgis``

InfluxDB
--------

InfluxDB is the default time series database used by the :doc:`Monitoring
module </monitoring/index>`.

``INFLUXDB_USER``
~~~~~~~~~~~~~~~~~

- **Explanation:** Username of InfluxDB user.
- **Valid Values:** STRING.
- **Default:** ``admin``.

``INFLUXDB_PASS``
~~~~~~~~~~~~~~~~~

- **Explanation:** Password for InfluxDB user.
- **Valid Values:** STRING.
- **Default:** ``admin``.

``INFLUXDB_NAME``
~~~~~~~~~~~~~~~~~

- **Explanation:** Name of InfluxDB database.
- **Valid Values:** STRING.
- **Default:** ``openwisp``.

``INFLUXDB_HOST``
~~~~~~~~~~~~~~~~~

- **Explanation:** Host to be used when connecting to influxDB. Values as
  ``localhost`` or empty string are not allowed.
- **Valid Values:** any valid hostname or IP address.
- **Default:** ``influxdb``.

``INFLUXDB_PORT``
~~~~~~~~~~~~~~~~~

- **Explanation:** Port on which InfluxDB is listening to.
- **Valid Values:** INTEGER.
- **Default:** ``8086``.

``INFLUXDB_DEFAULT_RETENTION_POLICY``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** The default retention policy that applies to the time
  series data.
- **Valid Values:** STRING.
- **Default:** ``26280h0m0s`` (3 years).

Postfix
-------

.. note::

    Keep in mind that Postfix is optional. You can avoid running the
    Postfix container if you already have an external SMTP server
    available.

``POSTFIX_ALLOWED_SENDER_DOMAINS``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Due to in-built spam protection in Postfix you will
  need to specify sender domains.
- **Valid Values:** Any valid domain name.
- **Default:** ``example.org``.

``POSTFIX_MYHOSTNAME``
~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** You may configure a specific hostname that the SMTP
  server will use to identify itself.
- **Valid Values:** STRING.
- **Default:** ``example.org``.

``POSTFIX_DESTINATION``
~~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Destinations of the postfix service.
- **Valid Values:** Any valid domain name.
- **Default:** ``$mydomain, $myhostname``.

``POSTFIX_MESSAGE_SIZE_LIMIT``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** By default, this limit is set to 0 (zero), which means
  unlimited. Why would you want to set this? Well, this is especially
  useful in relation with ``RELAYHOST`` setting.
- **Valid Values:** INTEGER.
- **Default:** ``0``
- **Example:** ``26214400``

``POSTFIX_MYNETWORKS``
~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Postfix is exposed only in ``mynetworks`` to prevent
  any issues with this postfix being inadvertently exposed on the
  internet.
- **Valid Values:** space separated IP Networks.
- **Default:** ``127.0.0.0/8 [::ffff:127.0.0.0]/104 [::1]/128``.

``POSTFIX_RELAYHOST_TLS_LEVEL``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Define relay host TLS connection level.
- **Valid Values:** `See list
  <http://www.postfix.org/postconf.5.html#smtp_tls_security_level>`__.
- **Default:** ``may``.

``POSTFIX_RELAYHOST``
~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Host that relays your mails.
- **Valid Values:** any valid IP address or domain name.
- **Default:** ``null``.
- **Example:** ``[smtp.gmail.com]:587``.

``POSTFIX_RELAYHOST_USERNAME``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Username for the relay server.
- **Valid Values:** STRING.
- **Default:** ``null``.
- **Example:** ``example@example.com``.

``POSTFIX_RELAYHOST_PASSWORD``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Login password for the relay server.
- **Valid Values:** STRING.
- **Default:** ``null``.
- **Example:** ``example``.

``POSTFIX_DEBUG_MYNETWORKS``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Set debug_peer_list for given list of networks.
- **Valid Values:** STRING.
- **Default:** ``null``.
- **Example:** ``127.0.0.0/8``.

.. _docker_uwsgi_env:

uWSGI
-----

``UWSGI_PROCESSES``
~~~~~~~~~~~~~~~~~~~

- **Explanation:** Number of uWSGI process to spawn.
- **Valid Values:** INTEGER.
- **Default:** ``2``.

``UWSGI_THREADS``
~~~~~~~~~~~~~~~~~

- **Explanation:** Number of threads each uWSGI process will have.
- **Valid Values:** INTEGER.
- **Default:** ``2``.

``UWSGI_LISTEN``
~~~~~~~~~~~~~~~~

- **Explanation:** Value of the listen queue of uWSGI.
- **Valid Values:** INTEGER.
- **Default:** ``100``.

Nginx
-----

``NGINX_HTTP2``
~~~~~~~~~~~~~~~

- **Explanation:** Used by nginx to enable http2. Refer to the `related
  Nginx documentation section
  <https://www.nginx.com/blog/http2-module-nginx/#overview>`__ for
  details.
- **Valid Values:** ``http2`` or empty string.
- **Default:** ``http2``.

``NGINX_CLIENT_BODY_SIZE``
~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Client body size. Refer to the `related Nginx
  documentation section
  <http://nginx.org/en/docs/http/ngx_http_core_module.html#client_max_body_size>`__
  for details.
- **Valid Values:** INTEGER.
- **Default:** ``30``.

``NGINX_IP6_STRING``
~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Nginx listen on IPv6 for SSL connection. You can either
  enter a valid nginx statement or leave this value empty.
- **Valid Values:** ``listen [::]:443 ssl http2;`` or empty string.
- **Default:** ``""`` (empty string).

``NGINX_IP6_80_STRING``
~~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Nginx listen on IPv6 connection. You can either enter a
  valid nginx statement or leave this value empty.
- **Valid Values:** ``listen [::]:80;`` or empty string.
- **Default:** ``""`` (empty string).

``NGINX_ADMIN_ALLOW_NETWORK``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** IP address allowed to access OpenWISP services.
- **Valid Values:** ``all``, IP network.
- **Example:** ``12.213.43.54/16``.
- **Default:** ``all``.

``NGINX_SERVER_NAME_HASH_BUCKET``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Define the `Nginx domain hash bucket size
  <http://nginx.org/en/docs/hash.html>`__. Values should be only in powers
  of 2.
- **Valid Values:** INTEGER.
- **Default:** ``32``.

``NGINX_SSL_CONFIG``
~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Additional nginx configurations. You can add any valid
  server block element here. As an example ``index`` option is configured.
  You may add options to this string or leave this variable blank. This
  variable is only applicable when ``SSL_CERT_MODE`` is ``Yes`` or
  ``SelfSigned``.
- **Example:** ``index index.html index.htm;``.
- **Default:** ``""`` (empty string).

``NGINX_80_CONFIG``
~~~~~~~~~~~~~~~~~~~

- **Explanation:** Additional nginx configurations. You can add any valid
  server block element here. As an example ``index`` option is configured.
  You may add options to this string or leave this variable blank. This
  variable is only applicable when ``SSL_CERT_MODE`` is ``False``.
- **Example:** ``index index.html index.htm;``.
- **Default:** ``""`` (empty string).

``NGINX_GZIP_SWITCH``
~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Turn on/off Nginx GZIP.
- **Valid Values:** ``on``, ``off``.
- **Default:** ``on``.

``NGINX_GZIP_LEVEL``
~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Sets a gzip compression level of a response. Acceptable
  values are in the range from 1 to 9.
- **Valid Values:** ``INTEGER``.
- **Default:** ``6``.

``NGINX_GZIP_PROXIED``
~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Enables or disables gzipping of responses for proxied
  requests depending on the request and response.
- **Valid Values:** ``off``, ``expired``, ``no-cache``, ``no-store`` \|
  ``private``, ``no_last_modified``, ``no_etag``, ``auth``, ``any``.
- **Default:** ``any``.

``NGINX_GZIP_MIN_LENGTH``
~~~~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Sets the minimum length of a response that will be
  gzipped. The length is determined only from the "Content-Length"
  response header field.
- **Valid Values:** INTEGER.
- **Default:** ``1000``.

``NGINX_GZIP_TYPES``
~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Enables gzipping of responses for the specified MIME
  types in addition to "text/html". The special value "\*" matches any
  MIME type. Responses with the "text/html" type are always compressed.
- **Valid Values:** MIME type
- **Example:** ``text/plain image/svg+xml application/json
  application/javascript text/xml text/css application/xml
  application/x-font-ttf font/opentype``.
- **Default:** ``\*``.

``NGINX_HTTPS_ALLOWED_IPS``
~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Allow these IP addresses to access the website over
  http when ``SSL_CERT_MODE`` is set to ``Yes`` .
- **Valid Values:** ``all``, any valid IP address.
- **Example:** ``12.213.43.54/16``.
- **Default:** ``all``.

``NGINX_HTTP_ALLOW``
~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Allow http access with https access. Valid only when
  ``SSL_CERT_MODE`` is set to ``Yes`` or ``SelfSigned``.
- **Valid Values:** ``True``, ``False``.
- **Default:** ``True``.

``NGINX_CUSTOM_FILE``
~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** If you have a custom configuration file mounted, set
  this to ``True``.
- **Valid Values:** ``True``, ``False``.
- **Default:** ``False``.

``NINGX_REAL_REMOTE_ADDR``
~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** The nginx header to get the value of the real IP
  address of Access points. Example if a reverse proxy is used in your
  cluster (Example if you are using an Ingress), then the real IP of the
  AP is most likely the ``$http_x_forwarded_for``. If
  ``$http_x_forwarded_for`` returns a list, you can use ``$real_ip`` for
  getting first element of the list.
- **Valid Values:** ``$remote_addr``, ``$http_x_forwarded_for``,
  ``$realip_remote_addr``, ``$real_ip``.
- **Default:** ``$real_ip``.

OpenVPN
-------

``VPN_NAME``
~~~~~~~~~~~~

- **Explanation:** Name of the VPN Server that will be visible on the
  OpenWISP dashboard.
- **Valid Values:** STRING.
- **Default:** ``default``.

``VPN_CLIENT_NAME``
~~~~~~~~~~~~~~~~~~~

- **Explanation:** Name of the VPN client template that will be visible on
  the OpenWISP dashboard.
- **Valid Values:** STRING.
- **Default:** ``default-management-vpn``.

Topology
--------

``TOPOLOGY_UPDATE_INTERVAL``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Interval in minutes to upload the topology data to the
  OpenWISP,
- **Valid Values:** INTEGER.
- **Default:** ``3``.

X509 Certificates
-----------------

``X509_NAME_CA``
~~~~~~~~~~~~~~~~

- **Explanation:** Name of the default certificate authority visible on
  the OpenWISP dashboard.
- **Valid Values:** STRING.
- **Default:** ``default``.

``X509_NAME_CERT``
~~~~~~~~~~~~~~~~~~

- **Explanation:** Name of the default certificate visible on the OpenWISP
  dashboard.
- **Valid Values:** STRING.
- **Default:** ``default``.

``X509_COUNTRY_CODE``
~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** ISO code of the country of issuance of the certificate.
- **Valid Values:** Country code, see list `here
  <https://countrycode.org/>`__.
- **Default:** ``IN``.

``X509_STATE``
~~~~~~~~~~~~~~

- **Explanation:** Name of the state / province of issuance of the
  certificate.
- **Valid Values:** STRING.
- **Default:** ``Delhi``.

``X509_CITY``
~~~~~~~~~~~~~

- **Explanation:** Name of the city of issuance of the certificate.
- **Valid Values:** STRING.
- **Default:** ``New Delhi``.

``X509_ORGANIZATION_NAME``
~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Name of the organization issuing the certificate.
- **Valid Values:** STRING.
- **Default:** ``OpenWISP``.

``X509_ORGANIZATION_UNIT_NAME``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Name of the unit of the organization issuing the
  certificate.
- **Valid Values:** STRING.
- **Default:** ``OpenWISP``.

``X509_EMAIL``
~~~~~~~~~~~~~~

- **Explanation:** Organization email address that'll be available to view
  in the certificate.
- **Valid Values:** STRING.
- **Default:** ``certificate@example.com``.

``X509_COMMON_NAME``
~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Common name for the CA and certificate.
- **Valid Values:** STRING.
- **Default:** ``OpenWISP``.

Misc Services
-------------

``REDIS_HOST``
~~~~~~~~~~~~~~

- **Explanation:** Host to establish redis connection.
- **Valid Values:** A valid hostname or IP address.
- **Default:** ``redis``.

``REDIS_PORT``
~~~~~~~~~~~~~~

- **Explanation:** Port to establish redis connection.
- **Valid Values:** INTEGER.
- **Default:** ``6379``.

``REDIS_PASS``
~~~~~~~~~~~~~~

- **Explanation:** Redis password, optional.
- **Valid Values:** STRING.
- **Default:** ``None``.

``DASHBOARD_APP_SERVICE``
~~~~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Host to establish OpenWISP dashboard connection.
- **Valid Values:** Any hostname or IP address.
- **Default:** ``dashboard``.

``API_APP_SERVICE``
~~~~~~~~~~~~~~~~~~~

- **Explanation:** Host to establish OpenWISP api connection.
- **Valid Values:** Any hostname or IP address.
- **Default:** ``api``.

``DASHBOARD_APP_PORT``
~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** The port on which nginx tries to get the OpenWISP
  dashboard container. Don't Change unless you know what you are doing.
- **Valid Values:** INTEGER.
- **Default:** ``8000``.

``API_APP_PORT``
~~~~~~~~~~~~~~~~

- **Explanation:** The port on which nginx tries to get the OpenWISP api
  container. Don't Change unless you know what you are doing.
- **Valid Values:** INTEGER.
- **Default:** ``8001``.

``WEBSOCKET_APP_PORT``
~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** The port on which nginx tries to get the OpenWISP
  websocket container. Don't Change unless you know what you are doing.
- **Valid Values:** INTEGER.
- **Default:** ``8002``.

``DASHBOARD_INTERNAL``
~~~~~~~~~~~~~~~~~~~~~~

- **Explanation:** Internal dashboard domain to reach dashboard from other
  containers.
- **Valid Values:** STRING.
- **Default:** ``dashboard.internal``.

``API_INTERNAL``
~~~~~~~~~~~~~~~~

- **Explanation:** Internal api domain to reach api from other containers.
- **Valid Values:** STRING.
- **Default:** ``api.internal``.

NFS Server
----------

``EXPORT_DIR``
~~~~~~~~~~~~~~

- **Explanation:** Directory to be exported by the NFS server. Don't
  change this unless you know what you are doing.
- **Valid Values:** STRING.
- **Default:** ``/exports``.

``EXPORT_OPTS``
~~~~~~~~~~~~~~~

- **Explanation:** NFS export options for the directory in ``EXPORT_DIR``
  variable.
- **Valid Values:** STRING.
- **Default:**
  ``10.0.0.0/8(rw,fsid=0,insecure,no_root_squash,no_subtree_check,sync)``.
