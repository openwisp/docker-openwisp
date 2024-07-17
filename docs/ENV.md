# Environment Variables

[![Gitter](https://badges.gitter.im/openwisp/dockerize-openwisp.svg)](https://gitter.im/openwisp/dockerize-openwisp?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)
[![Support](https://img.shields.io/badge/support-orange.svg)](http://openwisp.org/support.html)

**Right now, this is only tentative guide. Errata may exist. Please report errors on the [gitter channel](https://gitter.im/openwisp/dockerize-openwisp?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge).**

The OpenWISP docker images are created with customization in mind. You can simply change the environment variables to change the containers and trailer them to your needs.

- `docker compose`: You can simply change the values in `.env` file.
- `kubernetes`: You need to create `ConfigMap` to change the environment variables. An example is present in `deploy/examples/kubernetes/` directory.

Following are the options that can be changed. The list is divided in following sections:

- [Essential](#Essential): You need to change these values to get the containers working for your system.
- [Security](#Security): You should change these values for security reasons.
- [Enable Modules](#Enable-Modules): Enable / Disable optional openwisp modules.
- [Additional](#Additional): You might want to look into these options before using images in production.
- [OpenWISP](#OpenWISP): OpenWISP Module Configuration.
- [Database](#Database): Database settings.
- [InfluxDB](#InfluxDB): InfluxDB settings. (Used in OpenWISP-monitoring)
- [Django](#Django): Additional django settings.
- [Email](#Email): Email & postfix configurations.
- [Cron](#Cron): Settings of the periodic tasks.
- [uWSGI](#uWSGI): uWSGI configurations.
- [Nginx](#Nginx): Nginx configurations.
- [VPN](#VPN): Default VPN and VPN template related configurations.
- [X509](#X509): Default certificate & certicate Authority configuration options.
- [Host](#Hosts): Want to change the host of a particular service? Like pointing all the containers to a different database service.
- [Developer](#Developer): DON'T change these values unless you know what you are doing.
- [Export](#Export): Changing options for NFS container.

Additionally, you can search for the following:

- `OPENWISP_`: All the custom openwisp module's settings.
- `DB_`: All the database settings.
- `INFLUXDB_`: All the InfluxDB related settings specific settings.
- `DJANGO_`: All the django settings.
- `EMAIL__`: All the email settings. (Also see `POSTFIX_`)
- `POSTFIX_`: All the postfix settings. (Also see `EMAIL_`)
- `NGINX_`: All the nginx settings.
- `DASHBOARD_`: All the OpenWISP dashboard specific settings.
- `API_`: All the OpenWISP api specific settings.
- `RADIUS_`: All the OpenWISP radius specific settings.
- `TOPOLOGY_`: All the OpenWISP network topology specific settings.
- `X509_`: All the configurations related to x509 CA and certificates.
- `VPN_`: Default VPN and VPN template related configurations.
- `CRON_`: Periodic tasks configurations
- `EXPORT_`: NFS Server related configurations

## Essential

### `DASHBOARD_DOMAIN`

- **Explanation:** Domain on which you want to access OpenWISP dashboard.
- **Valid Values:** Domain
- **Default:** dashboard.example.com

### `API_DOMAIN`

- **Explanation:** Domain on which you want to access OpenWISP controller & topology API.
- **Valid Values:** Domain
- **Default:** api.example.com

### `VPN_DOMAIN`

- **Explanation:** Valid domain / IP address to reach the OpenVPN server.
- **Valid Values:** Domain | IP address
- **Default:** openvpn.example.com

### `EMAIL_DJANGO_DEFAULT`

- **Explanation:** It is the email address to use for various automated correspondence from the site manager(s).
- **Valid Values:** Email address
- **Default:** example@example.com

### `DB_USER`

- **Explanation:** The name of the database to use.
- **Valid Values:** STRING
- **Default:** admin

### `DB_PASS`

- **Explanation:** The password to use when connecting to the database.
- **Valid Values:** STRING
- **Default:** admin

## Security

### `DJANGO_SECRET_KEY`

- **Explanation:** A random unique string that must be kept secret for security reasons. You can generate it with the command: `python build.py get-secret-key` at the root of the repository to get a key or make a random key yourself.
- **Valid Values:** STRING
- **Default:** default_secret_key

### `DJANGO_ALLOWED_HOSTS`

- **Explanation:** Used validate a request's HTTP Host header. The default value `*` means all domains. It can be `.mydomain.com`. For security allow only trusted domains, when left blank, it defaults to your dashboard's root domain.
- **Valid Values:** List(Valid domain) | List(IP adress) | \* | --BLANK--
- **Default:** <your-dashboard-domains>
- **Example:** .openwisp.org,.example.org,www.example.com

### `OPENWISP_RADIUS_FREERADIUS_ALLOWED_HOSTS`

- **Explanation:** Default IP address or subnet of your freeradius instance.
- **Valid Values:** List(IP adress) | Subnet
- **Default:** 172.18.0.0/16
- **Example:** 127.0.0.1,192.0.2.20,172.18.0.0/16

## Enable Modules

### `USE_OPENWISP_TOPOLOGY`

- **Explanation:** Use the openwisp-network-topology module.
- **Valid Values:** True | False
- **Default:** True

### `USE_OPENWISP_RADIUS`

- **Explanation:** Use the openwisp-radius module.
- **Valid Values:** True | False
- **Default:** True

### `USE_OPENWISP_FIRMWARE`

- **Explanation:** Use the openwisp-firmware-upgrader module.
- **Valid Values:** True | False
- **Default:** True

### `USE_OPENWISP_MONITORING`

- **Explanation:** Use the openwisp-monitoring module.
- **Valid Values:** True | False
- **Default:** True

## Additional

### `TZ`

- **Explanation:** Sets the timezone for the OpenWISP containers.
- **Valid Values:** Find list of timezone database [here](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).
- **Default:** UTC

### `CERT_ADMIN_EMAIL`

- **Explanation:** Required by certbot. Email used for registration and recovery contact. Use comma to register multiple emails.
- **Valid Values:** Email address(s)
- **Default:** example@example.com

### `SSL_CERT_MODE`

- **Explanation:** Flag to enable or disable HTTPs. If it is set to `Yes`, letsencrypt certificates are automatically fetched with the help of certbot and a cronjob to ensure they stay updated is added. If it is set to `SelfSigned`, self-signed certificates are used and cronjob for the certificates is set. If set to `No`, site is accessiable via HTTP, if set if `EXTERNAL`, it tells HTTPs is used but managed by external tool like loadbalancer / provider. Setting this option as `No` is not recommended and might break some features, only do it when you know what you are doing.
- **Valid Values:** External | Yes | SelfSigned | No
- **Default:** Yes

## OpenWISP

Any OpenWISP Configuration of type `string`. `int`, `bool` or `json` is supported and can be used as per the documentation in the module. If you want support for a setting that has a more complex datatype, please discuss in the support channel.

### `OPENWISP_CUSTOM_OPENWRT_IMAGES`

- **Explanation:** [JSON of OpenWRT Images as documented in openwisp-firmware-image repository](https://github.com/openwisp/openwisp-firmware-upgrader/#openwisp_custom_openwrt_images).
- **Valid Values:** JSON
- **Default:** None
- **Example:** [{"name": "Name1","label": "Label1","boards": ["TestA", "TestB"]}, {"name": "Name2","label": "Label2","boards": ["TestC", "TestD"]}]

### `METRIC_COLLECTION`

- **Explanation:** Whether the usage metric collection feature of openwisp-utils is enabled or not.
- **Valid Values:** True | False
- **Default:** True

## Database

### `DB_NAME`

- **Explanation:** The name of the database to use.
- **Valid Values:** STRING
- **Default:** openwisp_db

### `DB_ENGINE`

- **Explanation:** Django database engine compatible with GeoDjango, read more [here](https://docs.djangoproject.com/en/2.2/ref/settings/#engine).
- **Valid Values:** Valid name from list [here](https://docs.djangoproject.com/en/2.2/ref/settings/#engine).
- **Default:** django.contrib.gis.db.backends.postgis

### `DB_HOST`

- **Explanation:** Host to be used when connecting to the database. `localhost` or empty string are not allowed.
- **Valid Values:** STRING | IP adress
- **Default:** postgres

### `DB_PORT`

- **Explanation:** The port to use when connecting to the database. Only valid port allowed.
- **Valid Values:** INTEGER
- **Default:** 5432

### `DB_SSLMODE`

- **Explanation:** [Postgresql SSLMode option](https://www.postgresql.org/docs/9.1/libpq-ssl.html).
- **Valid Values:** STRING
- **Default:** disable

### `DB_SSLCERT`

- **Explanation:** Path inside container to valid client certificate.
- **Valid Values:** STRING
- **Default:** None

### `DB_SSLKEY`

- **Explanation:** Path inside container to valid client private key.
- **Valid Values:** STRING
- **Default:** None

### `DB_SSLROOTCERT`

- **Explanation:** Path inside container to database server certificate.
- **Valid Values:** STRING
- **Default:** None

### `DB_OPTIONS`

- **Explanation:** Additional database options to connect to the database. These options must be supported by your `DB_ENGINE`.
- **Valid Values:** JSON
- **Default:** {}

## InfluxDB

### `INFLUXDB_USER`

- **Explanation:** Username of InfluxDB user.
- **Valid Values:** STRING
- **Default:** admin

### `INFLUXDB_PASS`

- **Explanation:** Password for InfluxDB user.
- **Valid Values:** STRING
- **Default:** admin

### `INFLUXDB_NAME`

- **Explanation:** Name of InfluxDB database.
- **Valid Values:** STRING
- **Default:** openwisp

### `INFLUXDB_HOST`

- **Explanation:** Host to be used when connecting to the influxDB. `localhost` or empty string are not allowed.
- **Valid Values:** STRING | IP adress
- **Default:** influxdb

### `INFLUXDB_PORT`

- **Explanation:** Port on which InfluxDB is listening.
- **Valid Values:** INT
- **Default:** 8086

### `INFLUXDB_DEFAULT_RETENTION_POLICY`

- **Explanation:** The default retention policy that applies to the timeseries data.
- **Valid Values:** STRING
- **Default:** 26280h0m0s (3 years)

## Django

### `DJANGO_X509_DEFAULT_CERT_VALIDITY`

- **Explanation:** Validity of your x509 cert in days.
- **Valid Values:** INT
- **Default:** 1825

### `DJANGO_X509_DEFAULT_CA_VALIDITY`

- **Explanation:** Validity of your x509 CA in days.
- **Valid Values:** INT
- **Default:** 3650

### `DJANGO_CORS_HOSTS`

- **Explanation:** Hosts for which CORS is whitelisted. [See here](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS).
- **Valid Values:** List(Valid domain)
- **Default:** http://localhost
- **Example:** https://www.openwisp.org,openwisp.example.org

### `DJANGO_LANGUAGE_CODE`

- **Explanation:** Language for your OpenWISP application.
- **Valid Values:** List of available options can be found [here](https://github.com/django/django/blob/fcbc502af93f0ee75522c45ae6ec2925da9f2145/django/conf/global_settings.py#L51-L145)
- **Default:** en-gb

### `DJANGO_SENTRY_DSN`

- **Explanation:** Sentry DSN. [See here](https://sentry.io/for/django/).
- **Valid Values:** Your DSN value provided by sentry.
- **Example:** https://example@sentry.io/example
- **Default:** --BLANK--

### `DJANGO_LEAFET_CENTER_X_AXIS`

- **Explanation:** x-axis co-ordinate of the leaflet default center property. [See here](https://django-leaflet.readthedocs.io/en/latest/templates.html#configuration).
- **Valid Values:** FLOAT
- **Example:** 26.357896
- **Default:** 0

### `DJANGO_LEAFET_CENTER_Y_AXIS`

- **Explanation:** y-axis co-ordinate of the leaflet default center property. [See here](https://django-leaflet.readthedocs.io/en/latest/templates.html#configuration).
- **Valid Values:** FLOAT
- **Example:** 127.783809
- **Default:** 0

### `DJANGO_LEAFET_ZOOM`

- **Explanation:** Default zoom for leaflet. [See here](https://django-leaflet.readthedocs.io/en/latest/templates.html#configuration).
- **Valid Values:** INT (1-16)
- **Default:** 1

### `DJANGO_WEBSOCKET_HOST`

- **Explanation:** Host on which daphne should listen for websocket connections.
- **Valid Values:** Domain | IP Address
- **Default:** 0.0.0.0

### `OPENWISP_GEOCODING_CHECK`

- **Explanation:** Use to check if geocoding is working as expected or not.
- **Valid Values:** True | False
- **Default:** True

### `USE_OPENWISP_CELERY_TASK_ROUTES_DEFAULTS`

- **Explanation:** Whether the default celery task routes should be
  used by celery. Turn this off if you're defining custom task routing rules.
- **Valid Values:** True | False
- **Default:** True

### `OPENWISP_CELERY_COMMAND_FLAGS`

- **Explanation:** Additional flags passed to the command that
  starts the celery worker for the "default" queue. It can be used to configure
  different attributes of the celery worker (e.g. autoscaling, concurrency, etc.).
  Refer to the [celery worker documentation](https://docs.celeryq.dev/en/stable/userguide/workers.html#workers-guide)
  for more information on configurable properties.
- **Valid Values:** STRING
- **Default:** `--concurrency=1`

### `USE_OPENWISP_CELERY_NETWORK`

- **Explanation:** Whether the dedicated worker for the celery
  "network" queue is enabled. Must be turned on unless there's another
  server running a worker for this queue.
- **Valid Values:** True | False
- **Default:** True

### `OPENWISP_CELERY_NETWORK_COMMAND_FLAGS`

- **Explanation:** Additional flags passed to the command that
  starts the celery worker for the "network" queue. It can be used to configure
  different attributes of the celery worker (e.g. autoscaling, concurrency, etc.).
  Refer to the [celery worker documentation](https://docs.celeryq.dev/en/stable/userguide/workers.html#workers-guide)
  for more information on configurable properties.
- **Valid Values:** STRING
- **Default:** `--concurrency=1`

### `USE_OPENWISP_CELERY_FIRMWARE`

- **Explanation:** Whether the dedicated worker for the celery
    "firmware_upgrader" queue is enabled. Must be turned on unless
    there's another server running a worker for this queue.
- **Valid Values:** True | False
- **Default:** True

### `OPENWISP_CELERY_FIRMWARE_COMMAND_FLAGS`

- **Explanation:** Additional flags passed to the command that
  starts the celery worker for the "firmware_upgrader" queue. It can be used to configure
  different attributes of the celery worker (e.g. autoscaling, concurrency, etc.).
  Refer to the [celery worker documentation](https://docs.celeryq.dev/en/stable/userguide/workers.html#workers-guide)
  for more information on configurable properties.
- **Valid Values:** STRING
- **Default:** `--concurrency=1`

### `USE_OPENWISP_CELERY_MONITORING`

- **Explanation:** Whether the dedicated worker for the celery
    "monitoring" and "monitoring_checks" queue is enabled.
    Must be turned on unless there's another server running
    a worker for this queue.
- **Valid Values:** True | False
- **Default:** True

### `OPENWISP_CELERY_MONITORING_COMMAND_FLAGS`

- **Explanation:** Additional flags passed to the command that
  starts the celery worker for the "monitoring" queue.
  It can be used to configure different attributes of the
  celery worker (e.g. autoscaling, concurrency, etc.).
  Refer to the [celery worker documentation](https://docs.celeryq.dev/en/stable/userguide/workers.html#workers-guide)
  for more information on configurable properties.
- **Valid Values:** STRING
- **Default:** `--concurrency=1`

### `OPENWISP_CELERY_MONITORING_CHECKS_COMMAND_FLAGS`

- **Explanation:** Additional flags passed to the command that
  starts the celery worker for the "monitoring_checks" queue.
  It can be used to configure different attributes of the
  celery worker (e.g. autoscaling, concurrency, etc.).
  Refer to the [celery worker documentation](https://docs.celeryq.dev/en/stable/userguide/workers.html#workers-guide)
  for more information on configurable properties.
- **Valid Values:** STRING
- **Default:** `--concurrency=1`

## Email

### `EMAIL_BACKEND`

- **Explanation:** Email will be sent using this backend.
- **Valid Values:** [See list](https://docs.djangoproject.com/en/2.2/topics/email/#obtaining-an-instance-of-an-email-backend)
- **Default:** djcelery_email.backends.CeleryEmailBackend

### `EMAIL_HOST_PORT`

- **Explanation:** Port to use for the SMTP server defined in `EMAIL_HOST`.
- **Valid Values:** INTEGER
- **Default:** 25

### `EMAIL_HOST_USER`

- **Explanation:** Username to use for the SMTP server defined in EMAIL_HOST. If empty, Django won’t attempt authentication.
- **Valid Values:** STRING
- **Default:** --BLANK--
- **Example:** example@example.com

### `EMAIL_HOST_PASSWORD`

- **Explanation:** Username to use for the SMTP server defined in EMAIL_HOST. If empty, Django won’t attempt authentication.
- **Valid Values:** STRING
- **Default:** --BLANK--

### `EMAIL_HOST_TLS`

- **Explanation:** Whether to use a TLS (secure) connection when talking to the SMTP server. This is used for explicit TLS connections, generally on port 587.
- **Valid Values:** True | False
- **Default:** False

### `EMAIL_TIMEOUT`

- **Explanation:** Specifies a timeout in seconds used by Django for blocking operations like the connection attempt.
- **Valid Values:** INTEGER
- **Default:** 10

### `POSTFIX_ALLOWED_SENDER_DOMAINS`

- **Explanation:** Due to in-built spam protection in Postfix you will need to specify sender domains.
- **Valid Values:** Domain
- **Default:** example.org

### `POSTFIX_MYHOSTNAME`

- **Explanation:** You may configure a specific hostname that the SMTP server will use to identify itself.
- **Valid Values:** STRING
- **Default:** example.org

### `POSTFIX_DESTINATION`

- **Explanation:** Destinations of the postfix service.
- **Valid Values:** Domain
- **Default:** $myhostname

### `POSTFIX_MESSAGE_SIZE_LIMIT`

- **Explanation:** By default, this limit is set to 0 (zero), which means unlimited. Why would you want to set this? Well, this is especially useful in relation with RELAYHOST setting.
- **Valid Values:**
- **Default:** 0
- **Example:** 26214400

### `POSTFIX_MYNETWORKS`

- **Explanation:** Postfix is exposed only in mynetworks to prevent any issues with this postfix being inadvertently exposed on the internet.
- **Valid Values:** IP Addresses
- **Default:** 127.0.0.0/8 [::ffff:127.0.0.0]/104 [::1]/128

### `POSTFIX_RELAYHOST_TLS_LEVEL`

- **Explanation:** Define relay host TLS connection level.
- **Valid Values:** [See list](http://www.postfix.org/postconf.5.html#smtp_tls_security_level).
- **Default:** may

### `POSTFIX_RELAYHOST`

- **Explanation:** Host that relays your mails.
- **Valid Values:** IP address | Domain
- **Default:** null
- **Example:** [smtp.gmail.com]:587

### `POSTFIX_RELAYHOST_USERNAME`

- **Explanation:** Username for the relay server.
- **Valid Values:** STRING
- **Default:** null
- **Example:** example@example.com

### `POSTFIX_RELAYHOST_PASSWORD`

- **Explanation:** Login password for the relay server.
- **Valid Values:** STRING
- **Default:** null
- **Example:** example

## Cron

### `CRON_DELETE_OLD_RADACCT`

- **Explanation:** (Value in days) Deletes RADIUS accounting sessions older than given number of days.
- **Valid Values:** INT
- **Default:** 365

### `CRON_DELETE_OLD_POSTAUTH`

- **Explanation:** (Value in days) Deletes RADIUS post-auth logs older than given number of days.
- **Valid Values:** INT
- **Default:** 365

### `CRON_CLEANUP_STALE_RADACCT`

- **Explanation:** (Value in days) Closes stale RADIUS sessions that have remained open for the number of specified days.
- **Valid Values:** INT
- **Default:** 365

### `CRON_DELETE_OLD_RADIUSBATCH_USERS`

- **Explanation:** (Value in months) Deactivates expired user accounts which were created temporarily and have an expiration date set.
- **Valid Values:** INT
- **Default:** 12

## uWSGI

### `UWSGI_PROCESSES`

- **Explanation:** Number of uWSGI process to spawn.
- **Valid Values:** INT
- **Default:** 2

### `UWSGI_THREADS`

- **Explanation:** Number of threads each uWSGI process will have.
- **Valid Values:** INT
- **Default:** 2

### `UWSGI_LISTEN`

- **Explanation:** Value of the listen queue of uWSGI
- **Valid Values:** INT
- **Default:** 100

## Nginx

### `NGINX_HTTP2`

- **Explanation:** Options: or http2. Used by nginx to enable http2. [See here](https://www.nginx.com/blog/http2-module-nginx/#overview)
- **Valid Values:** --BLANK-- | http2
- **Default:** http2

### `NGINX_CLIENT_BODY_SIZE`

- **Explanation:** Client body size. [See here](http://nginx.org/en/docs/http/ngx_http_core_module.html#client_max_body_size)
- **Valid Values:** INT
- **Default:** 30

### `NGINX_IP6_STRING`

- **Explanation:** Nginx listen on IPv6 for SSL connection. You can either enter a valid nginx statement or leave this value empty.
- **Valid Values:** --BLANK-- | listen [::]:443 ssl http2;
- **Default:** --BLANK--

### `NGINX_IP6_80_STRING`

- **Explanation:** Nginx listen on IPv6 connection. You can either enter a valid nginx statement or leave this value empty.
- **Valid Values:** --BLANK-- | listen [::]:80;
- **Default:** --BLANK--

### `NGINX_ADMIN_ALLOW_NETWORK`

- **Explanation:** IP address allowed to access OpenWISP services.
- **Valid Values:** all | IP address
- **Example:** `12.213.43.54/16`
- **Default:** all

### `NGINX_SERVER_NAME_HASH_BUCKET`

- **Explanation:** Define domain hash bucket size. [See here](http://nginx.org/en/docs/hash.html). Value should be only in powers of 2.
- **Valid Values:** INT
- **Default:** 32

### `NGINX_SSL_CONFIG`

- **Explanation:** Additional nginx configurations. You can add any valid server block element here. As an example `index` option is configured. You may add options to this string or leave this variable blank. This variable is only applicable when `SSL_CERT_MODE` is `Yes` or `SelfSigned`.
- **Example:** `index index.html index.htm;`
- **Default:** --BLANK--

### `NGINX_80_CONFIG`

- **Explanation:** Additional nginx configurations. You can add any valid server block element here. As an example `index` option is configured. You may add options to this string or leave this variable blank. This variable is only applicable when `SSL_CERT_MODE` is `False`.
- **Example:** `index index.html index.htm;`
- **Default:** --BLANK--

### `NGINX_GZIP_SWITCH`

- **Explanation:** Turn on/off Nginx GZIP.
- **Valid Values:** `on` | `off`
- **Default:** `off`

### `NGINX_GZIP_LEVEL`

- **Explanation:** Sets a gzip compression level of a response. Acceptable values are in the range from 1 to 9.
- **Valid Values:** INT
- **Default:** 6

### `NGINX_GZIP_PROXIED`

- **Explanation:** Enables or disables gzipping of responses for proxied requests depending on the request and response.
- **Valid Values:** `off` | `expired` | `no-cache` | `no-store` | `private` | `no_last_modified` | `no_etag` | `auth` | `any`
- **Default:** `any`

### `NGINX_GZIP_MIN_LENGTH`

- **Explanation:** Sets the minimum length of a response that will be gzipped. The length is determined only from the “Content-Length” response header field.
- **Valid Values:** INT
- **Default:** 1000

### `NGINX_GZIP_TYPES`

- **Explanation:** Enables gzipping of responses for the specified MIME types in addition to “text/html”. The special value “\*” matches any MIME type. Responses with the “text/html” type are always compressed.
- **Valid Values:** MIME type
- **Example:** `text/plain image/svg+xml application/json application/javascript text/xml text/css application/xml application/x-font-ttf font/opentype`
- **Default:** \*

### `NGINX_HTTPS_ALLOWED_IPS`

- **Explanation:** Allow these IP addresses to access the website over http when `SSL_CERT_MODE` is set to `Yes` .
- **Valid Values:** all | IP address
- **Example:** `12.213.43.54/16`
- **Default:** all

### `NGINX_HTTP_ALLOW`

- **Explanation:** Allow http access with https access. Valid only when `SSL_CERT_MODE` is set to `Yes` or `SelfSigned`.
- **Valid Values:** True | False
- **Default:** True

### `NGINX_CUSTOM_FILE`

- **Explanation:** If you have a custom configuration file mounted, set this to `True`.
- **Valid Values:** True | False
- **Default:** False

### `NINGX_REAL_REMOTE_ADDR`

- **Explanation:** The nginx header to get the value of the real IP address of Access points. Example if a reverse proxy is used in your cluster (Example if you are using an Ingress), then the real IP of the AP is most likely the `$http_x_forwarded_for`. If `$http_x_forwarded_for` returns a list, you can use `$real_ip` for getting first element of the list.
- **Valid Values:** `$remote_addr` | `$http_x_forwarded_for` | `$realip_remote_addr` | `$real_ip`
- **Default:** `$real_ip`

## VPN

### `VPN_NAME`

- **Explanation:** Name of the VPN Server that will be visible on the OpenWISP dashboard.
- **Valid Values:** STRING
- **Default:** default

### `VPN_CLIENT_NAME`

- **Explanation:** Name of the VPN client template that will be visible on the OpenWISP dashboard.
- **Valid Values:** STRING
- **Default:** default-management-vpn

## X509

### `X509_NAME_CA`

- **Explanation:** Name of the default certificate authority visible on the OpenWISP dashboard.
- **Valid Values:** STRING
- **Default:** default

### `X509_NAME_CERT`

- **Explanation:** Name of the default certificate visible on the OpenWISP dashboard.
- **Valid Values:** STRING
- **Default:** default

### `X509_COUNTRY_CODE`

- **Explanation:** ISO code of the country of issuance of the certificate.
- **Valid Values:** Country code, see list [here](https://countrycode.org/)
- **Default:** IN

### `X509_STATE`

- **Explanation:** Name of the state / province of issuance of the certificate.
- **Valid Values:** STRING
- **Default:** Delhi

### `X509_CITY`

- **Explanation:** Name of the city of issuance of the certificate.
- **Valid Values:** STRING
- **Default:** New Delhi

### `X509_ORGANIZATION_NAME`

- **Explanation:** Name of the organization issuing the certificate.
- **Valid Values:** STRING
- **Default:** OpenWISP

### `X509_ORGANIZATION_UNIT_NAME`

- **Explanation:** Name of the unit of the organization issuing the certificate.
- **Valid Values:** STRING
- **Default:** OpenWISP

### `X509_EMAIL`

- **Explanation:** Organzation email adddress that'll be available to view in the certificate.
- **Valid Values:** STRING
- **Default:** certificate@example.com

### `X509_COMMON_NAME`

- **Explanation:** Common name for the CA and certificate.
- **Valid Values:** STRING
- **Default:** OpenWISP

## Hosts

### `EMAIL_HOST`

- **Explanation:** Host to be used when connecting to the STMP. `localhost` or empty string are not allowed.
- **Valid Values:** STRING | IP adress
- **Example:** smtp.gmail.com
- **Default:** postfix

### `REDIS_HOST`

- **Explanation:** Host to establish redis connection.
- **Valid Values:** Domain | IP address
- **Default:** redis

### `REDIS_PORT`

- **Explanation:** Port to establish redis connection.
- **Valid Values:** INT
- **Default:** `6379`

### `REDIS_PASS`

- **Explanation:** Redis password, optional.
- **Valid Values:** STRING
- **Default:** `None`

### `DASHBOARD_APP_SERVICE`

- **Explanation:** Host to establish OpenWISP dashboard connection.
- **Valid Values:** Domain | IP address
- **Default:** dashboard

### `API_APP_SERVICE`

- **Explanation:** Host to establish OpenWISP api connection.
- **Valid Values:** Domain | IP address
- **Default:** api

## Developer

### `DEBUG_MODE`

- **Explanation:** Enable Django Debugging. [See here](https://docs.djangoproject.com/en/2.2/ref/settings/#debug).
- **Valid Values:** True | False
- **Default:** False

### `DASHBOARD_APP_PORT`

- **Explanation:** Change the port on which nginx tries to get the OpenWISP dashboard container. DON'T Change unless you know what you are doing.
- **Valid Values:** INTEGER
- **Default:** 8000

### `API_APP_PORT`

- **Explanation:** Change the port on which nginx tries to get the OpenWISP api container. DON'T Change unless you know what you are doing.
- **Valid Values:** INTEGER
- **Default:** 8001

### `DASHBOARD_INTERNAL`

- **Explanation:** Internal dashboard domain to reach dashboard from other containers.
- **Valid Values:** STRING
- **Default:** dashboard.internal

### `API_INTERNAL`

- **Explanation:** Internal api domain to reach api from other containers.
- **Valid Values:** STRING
- **Default:** api.internal

### `POSTFIX_DEBUG_MYNETWORKS`

- **Explanation:** Set debug_peer_list for given list of networks.
- **Valid Values:** STRING
- **Default:** null
- **Example:** 127.0.0.0/8

## Export

### `EXPORT_DIR`

- **Explanation:** Directory to be exported by the NFS server. Don't change this unless you know what you are doing.
- **Valid Values:** STRING
- **Default:** /exports

### `EXPORT_OPTS`

- **Explanation:** NFS export options for the directory in `EXPORT_DIR` variable.
- **Valid Values:** STRING
- **Default:** 10.0.0.0/8(rw,fsid=0,insecure,no_root_squash,no_subtree_check,sync)
