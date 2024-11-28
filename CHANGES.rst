Changelog
=========

Version 24.11.1 [2024-11-27]
----------------------------

Bugfixes
~~~~~~~~

- Updated ``__openwisp_version__`` to ``24.11.1``.

Version 24.11.0 [2024-11-27]
----------------------------

Features
~~~~~~~~

- Added a default topology for the default VPN.
- Added default credentials and SSH key template.
- Added support for specifying custom Django settings.
- Added dedicated queues for Celery workers.
- Added functionality to tune Celery workers.
- Introduced ``INFLUXDB_DEFAULT_RETENTION_POLICY`` variable to configure
  the default retention policy for InfluxDB.
- Added ``REDIS_PORT`` and ``REDIS_PASS`` variables to configure Redis
  port and password.
- Added ``UWSGI_PROCESSES``, ``UWSGI_THREADS``, and ``UWSGI_LISTEN``
  variables for configuring uWSGI processes, threads, and listen queue
  size.
- Implemented static file minification.
- Introduced a consent mechanism for the `collection of usage metrics
  <https://openwisp.io/docs/stable/utils/user/metric-collection.html>`_.

Changes
~~~~~~~

Dependencies
++++++++++++

- Upgraded to OpenWISP Users 1.1.x (see `changelog
  <https://github.com/openwisp/openwisp-users/releases/tag/1.1.0>`__).
- Upgraded to OpenWISP Controller 1.1.x (see `changelog
  <https://github.com/openwisp/openwisp-controller/releases/tag/1.1.0>`__).
- Upgraded to OpenWISP Monitoring 1.1.x (see `changelog
  <https://github.com/openwisp/openwisp-monitoring/releases/tag/1.1.0>`__).
- Upgraded to OpenWISP Network Topology 1.1.x (see `changelog
  <https://github.com/openwisp/openwisp-network-topology/releases/tag/1.1.0>`__).
- Upgraded to OpenWISP Firmware Upgrader 1.1.x (see `changelog
  <https://github.com/openwisp/openwisp-firmware-upgrader/releases/tag/1.1.0>`__).
- Updated auto-install script to support Debian 12.
- Updated auto-install script to support Ubuntu 22.04.
- Updated base image of ``openwisp/openwisp-nginx`` to
  ``nginx:1.27.2-alpine``.
- Updated base image of ``openwisp/openwisp-freeradius`` to
  ``freeradius/freeradius-server:3.2.6-alpine``.
- Updated base image of ``openwisp/openwisp-postfix`` to ``alpine:3.20``.
- Updated base image of ``openwisp/openwisp-openvpn`` to
  ``kylemanna/openvpn:2.4``.
- Updated base image of ``openwisp/openwisp-dashboard``,
  ``openwisp/openwisp-api``, and ``openwisp/openwisp-websocket`` to
  ``python:3.10.0-slim-buster``.

Backward Incompatible Changes
+++++++++++++++++++++++++++++

- Merged the OpenWISP RADIUS container into the dashboard and API.
- The ``CRON_DELETE_OLD_RADIUSBATCH_USERS`` variable now expects the
  number of days instead of months.
- Removed ``DJANGO_FREERADIUS_ALLOWED_HOSTS``; use
  ``OPENWISP_RADIUS_ALLOWED_HOSTS`` instead.
- Renamed ``CRON_DELETE_OLD_USERS`` to
  ``CRON_DELETE_OLD_RADIUSBATCH_USERS``.

Other Changes
+++++++++++++

- Changed cron to update OpenVPN revoke list daily at midnight.
- Added admin URLs to the API container.
- Migrated to Docker Compose v2.
- Geocoding checks are now performed only in the dashboard container.
- Removed ``sudo`` capabilities for containers.
- Main processes no longer run as ``root``.
- Switched the default email backend to ``django-celery-email``.
- Enabled ``django.contrib.humanize`` in installed apps.
- Enabled gzip compression for HTTP responses.
- Disabled nginx ``server_tokens`` for improved security.

Bugfixes
~~~~~~~~

- Fixed OpenVPN cron script to download configuration at the correct path.
- Fixed project configuration issues in the OpenWISP RADIUS module.
- Fixed monitoring charts not loading on the device's change page.
- Fixed network topology graph stuck at loading.
- Fixed bugs in the auto-install script.
- Fixed missing directory for firmware private storage.
- Fixed duplicate MIME types in nginx gzip configuration.
- Resolved ``OSerror`` in uWSGI.
