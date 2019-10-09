# Environment Variables

[![Gitter](https://badges.gitter.im/openwisp/dockerize-openwisp.svg)](https://gitter.im/openwisp/dockerize-openwisp?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)
[![Support](https://img.shields.io/badge/support-orange.svg)](http://openwisp.org/support.html)

**Right now, this is only tentative guide. Errata may exist. Please report errors on the [gitter channel](https://gitter.im/openwisp/dockerize-openwisp?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge).**

The OpenWISP docker images are created with customization in mind. You can simply change the environment variables to change the containers and trailer them to your needs.

- `docker-compose`: You can simply change the values in `.env` file.
- `kubernetes`: You need to create `ConfigMap` to change the environment variables. An example is present in `deployment-examples/kubernetes/` directory.

Following are the options that can be changed. The list is divided in following sections:

- [Essential](#Essential): You need to change these values to get the containers working for your system.
- [Security](#Security): You should change these values for security reasons.
- [Additional](#Additional): You might want to look into these options before using images in production.
- [Database](#Database): Database settings. Database host setting is in "Host" section.
- [Django](#Django): Additional django settings.
- [Email](#Email): Email & postfix configurations.
- [Freeradius](#Freeradius): Freeradius related settings.
- [Cron](#Cron): Settings of the periodic tasks.
- [Nginx](#Nginx): Nginx configurations.
- [VPN](#VPN): Default VPN and VPN template related configurations.
- [X509](#X509): Default certificate & certicate Authority configuration options.
- [Host](#Hosts): Want to change the host of a particular service? Like pointing all the containers to a different database service.
- [Developer](#Developer): DON'T change these values unless you know what you are doing.

Additionally, you can search for the following:
- `DB_`: All the database settings.
- `DJANGO_`: All the django settings.
- `EMAIL__`: All the email settings. (Also see `POSTFIX_`)
- `POSTFIX_`: All the postfix settings. (Also see `EMAIL_`)
- `NGINX_`: All the nginx settings.
- `DASHBOARD_`: All the OpenWISP dashboard specific settings.
- `CONTROLLER_`: All the OpenWISP controller specific settings.
- `RADIUS_`: All the OpenWISP radius specific settings.
- `TOPOLOGY_`: All the OpenWISP network topology specific settings.
- `FREERADIUS_`: All the freeradius related settings.
- `X509_`: All the configurations related to x509 CA and certificates.
- `VPN_`: Default VPN and VPN template related configurations.
- `CRON_`: Periodic tasks configurations

## Essential

### `DASHBOARD_DOMAIN`

- **Explaination:** Domain on which you want to access OpenWISP dashboard.
- **Valid Values:** Domain
- **Default:** dashboard.openwisp.org

### `CONTROLLER_DOMAIN`

- **Explaination:** Domain on which you want to access OpenWISP controller API.
- **Valid Values:** Domain
- **Default:** controller.openwisp.org

### `RADIUS_DOMAIN`

- **Explaination:** Domain on which you want to access OpenWISP radius API.
- **Valid Values:** Domain
- **Default:** radius.openwisp.org

### `TOPOLOGY_DOMAIN`

- **Explaination:** Domain on which you want to access OpenWISP network topology API.
- **Valid Values:** Domain
- **Default:** topology.openwisp.org

### `EMAIL_DJANGO_DEFAULT`

- **Explaination:** It is the email address to use for various automated correspondence from the site manager(s).
- **Valid Values:** Email address
- **Default:** example@example.com

### `DB_USER`

- **Explaination:** The name of the database to use.
- **Valid Values:** STRING
- **Default:** admin

### `DB_PASS`

- **Explaination:** The password to use when connecting to the database.
- **Valid Values:** STRING
- **Default:** admin

## Security

### `DJANGO_SECRET_KEY`

- **Explaination:** A random unique string that must be kept secret for security reasons. You can generate it with the command: `python build.py get-secret-key` at the root of the repository to get a key or make a random key yourself.
- **Valid Values:** STRING
- **Default:** default_secret_key

### `DJANGO_ALLOWED_HOSTS`

- **Explaination:** Used validate a request's HTTP Host header. The default value `*` means all domains. It can be `.mydomain.com`. For security allow only trusted domains.
- **Valid Values:** Valid domain | IP adress | *
- **Default:** *

## Additional

### `TZ`
- **Explaination:** Sets the timezone for the OpenWISP containers.
- **Valid Values:** Find list of timezone database [here](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).
- **Default:** UTC

### `CERT_ADMIN_EMAIL`

- **Explaination:** Required by certbot. Email used for registration and recovery contact. Use comma to register multiple emails.
- **Valid Values:** Email address(s)
- **Default:** example@example.com

### `SSL_CERT_MODE`

- **Explaination:** Flag to enable or disable HTTPs. If it is set to true, letsencrypt certificates are automatically fetched with the help of certbot and a cronjob to ensure they stay updated is added. If it is set to `Develop`, self-signed certificates are used and cronjob for the certificates is set. If set to False, site is accessiable via HTTP.
- **Valid Values:** True | Develop | False
- **Default:** True

### `SET_RADIUS_TASKS`

- **Explaination:** Set radius celery tasks, if you are not planning to use openwisp-radius container, set this to `False`.
- **Valid Values:** True | False
- **Default:** True

### `SET_TOPOLOGY_TASKS`

- **Explaination:** Set topology celery tasks, if you are not planning to use openwisp-topology container, set this to `False`.
- **Valid Values:** True | False
- **Default:** False

## Database

### `DB_NAME`

- **Explaination:** The name of the database to use.
- **Valid Values:** STRING
- **Default:** openwisp_db

### `DB_ENGINE`

- **Explaination:** Django database engine compatible with GeoDjango, read more [here](https://docs.djangoproject.com/en/2.2/ref/settings/#engine)
- **Valid Values:** Valid name from list [here](https://docs.djangoproject.com/en/2.2/ref/settings/#engine).
- **Default:** django.contrib.gis.db.backends.postgis

### `DB_PORT`

- **Explaination:** The port to use when connecting to the database. Only valid port allowed.
- **Valid Values:** INTEGER
- **Default:** 5432

### `DB_OPTIONS`

- **Explaination:** Additional database options to connect to the database. These options must be supported by your `DB_ENGINE`.
- **Valid Values:** JSON
- **Example:** {"sslmode": "disable", "sslrootcert": ""}
- **Default:** {}

## Django

### `DJANGO_X509_DEFAULT_CERT_VALIDITY`

- **Explaination:** Validity of your x509 cert in days.
- **Valid Values:** INT
- **Default:** 1825

### `DJANGO_X509_DEFAULT_CA_VALIDITY`

- **Explaination:** Validity of your x509 CA in days.
- **Valid Values:** INT
- **Default:** 3650

### `DJANGO_CORS_ORIGIN_ALLOW_ALL`

- **Explaination:** Allow CORS. [See here](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS).
- **Valid Values:** True | False
- **Default:** True

### `DJANGO_LANGUAGE_CODE`

- **Explaination:**  Language for your OpenWISP application.
- **Valid Values:** List of available options can be found [here](https://github.com/django/django/blob/fcbc502af93f0ee75522c45ae6ec2925da9f2145/django/conf/global_settings.py#L51-L145)
- **Default:**  en-gb

### `DJANGO_SENTRY_DSN`

- **Explaination:**  Sentry DSN. [See here](https://sentry.io/for/django/).
- **Valid Values:** Your DSN value provided by sentry.
- **Example:** https://example@sentry.io/example
- **Default:**  --BLANK--

### `DJANGO_LEAFET_CENTER_X_AXIS`
- **Explaination:**  x-axis co-ordinate of the leaflet default center property. [See here](https://django-leaflet.readthedocs.io/en/latest/templates.html#configuration).
- **Valid Values:** FLOAT
- **Example:** 26.357896
- **Default:**  0

### `DJANGO_LEAFET_CENTER_Y_AXIS`
- **Explaination:**  y-axis co-ordinate of the leaflet default center property. [See here](https://django-leaflet.readthedocs.io/en/latest/templates.html#configuration).
- **Valid Values:** FLOAT
- **Example:** 127.783809
- **Default:**  0

### `DJANGO_LEAFET_ZOOM`
- **Explaination:**  Default zoom for leaflet. [See here](https://django-leaflet.readthedocs.io/en/latest/templates.html#configuration).
- **Valid Values:** INT (1-16)
- **Default:**  1

## Email

### `EMAIL_BACKEND`
- **Explaination:** Email will be sent using this backend.
- **Valid Values:** [See list](https://docs.djangoproject.com/en/2.2/topics/email/#obtaining-an-instance-of-an-email-backend)
- **Default:** django.core.mail.backends.smtp.EmailBackend

### `EMAIL_HOST_PORT`
- **Explaination:** Port to use for the SMTP server defined in `EMAIL_HOST`.
- **Valid Values:** INTEGER
- **Default:** 25

### `EMAIL_HOST_USER`
- **Explaination:** Username to use for the SMTP server defined in EMAIL_HOST. If empty, Django won’t attempt authentication.
- **Valid Values:** STRING
- **Default:** --BLANK--
- **Example:** example@example.com

### `EMAIL_HOST_PASSWORD`
- **Explaination:** Username to use for the SMTP server defined in EMAIL_HOST. If empty, Django won’t attempt authentication.
- **Valid Values:** STRING
- **Default:** --BLANK--

### `EMAIL_HOST_TLS`
- **Explaination:** Whether to use a TLS (secure) connection when talking to the SMTP server. This is used for explicit TLS connections, generally on port 587.
- **Valid Values:** True | False
- **Default:** False

### `POSTFIX_ALLOWED_SENDER_DOMAINS`
- **Explaination:** Due to in-built spam protection in Postfix you will need to specify sender domains.
- **Valid Values:** Domain
- **Default:** example.org

### `POSTFIX_MYHOSTNAME`
- **Explaination:** You may configure a specific hostname that the SMTP server will use to identify itself.
- **Valid Values:** STRING
- **Default:** example.org

### `POSTFIX_DESTINATION`
- **Explaination:** Destinations of the postfix service.
- **Valid Values:** Domain
- **Default:** $myhostname

### `POSTFIX_MESSAGE_SIZE_LIMIT`
- **Explaination:** By default, this limit is set to 0 (zero), which means unlimited. Why would you want to set this? Well, this is especially useful in relation with RELAYHOST setting.
- **Valid Values:**
- **Default:** 0
- **Example:** 26214400

### `POSTFIX_MYNETWORKS`
- **Explaination:** Postfix is exposed only in mynetworks to prevent any issues with this postfix being inadvertently exposed on the internet.
- **Valid Values:** IP Addresses
- **Default:** 127.0.0.0/8 [::ffff:127.0.0.0]/104 [::1]/128

### `POSTFIX_RELAYHOST_TLS_LEVEL`
- **Explaination:** Define relay host TLS connection level.
- **Valid Values:** [See list](http://www.postfix.org/postconf.5.html#smtp_tls_security_level).
- **Default:** may

### `POSTFIX_RELAYHOST`
- **Explaination:** Host that relays your mails.
- **Valid Values:** IP address | Domain
- **Default:** null
- **Example:** [smtp.gmail.com]:587

### `POSTFIX_RELAYHOST_USERNAME`
- **Explaination:** Username for the relay server.
- **Valid Values:** STRING
- **Default:** null
- **Example:** example@example.com

### `POSTFIX_RELAYHOST_PASSWORD`
- **Explaination:** Login password for the relay server.
- **Valid Values:** STRING
- **Default:** null
- **Example:** example

## Freeradius

### `FREERADIUS_ORGANIZATION`
- **Explaination:** Organization name for which you want to setup the radius service.
- **Valid Values:** STRING
- **Default:** default

### `FREERADIUS_KEY`
- **Explaination:** This is the shared secret between the Authenticator (the access point) and the Authentication Server (RADIUS). Value of the `secret` parameter of the `client` in `clients.conf`.
- **Valid Values:** STRING
- **Default:** testing123

### `FREERADIUS_CLIENTS`
- **Explaination:** Value of the `ipaddr` parameter of the `client` in `clients.conf`. This is the network that the freeradius instance will serve. `0.0.0.0/0` means allow all.
- **Valid Values:** STRING
- **Default:** 0.0.0.0/0

## Cron

### `CRON_DELETE_OLD_RADACCT`

- **Explaination:** (Value in days) Deletes RADIUS accounting sessions older than given number of days.
- **Valid Values:** INT
- **Default:** 365

### `CRON_DELETE_OLD_POSTAUTH`

- **Explaination:** (Value in days) Deletes RADIUS post-auth logs older than given number of days.
- **Valid Values:** INT
- **Default:** 365

### `CRON_CLEANUP_STALE_RADACCT`

- **Explaination:** (Value in days) Closes stale RADIUS sessions that have remained open for the number of specified days.
- **Valid Values:** INT
- **Default:** 365

### `CRON_DELETE_OLD_USERS`

- **Explaination:** (Value in months) Deactivates expired user accounts which were created temporarily and have an expiration date set.
- **Valid Values:** INT
- **Default:** 12

## Nginx

### `NGINX_HTTP2`

- **Explaination:** Options:  or http2. Used by nginx to enable http2. [See here](https://www.nginx.com/blog/http2-module-nginx/#overview)
- **Valid Values:** --BLANK-- | http2
- **Default:** http2

### `NGINX_CLIENT_BODY_SIZE`

- **Explaination:** Client body size. [See here](http://nginx.org/en/docs/http/ngx_http_core_module.html#client_max_body_size)
- **Valid Values:** STRING
- **Default:** 5M

### `NGINX_IP6_STRING`

- **Explaination:** Nginx listen on IPv6 for SSL connection. You can either enter a valid nginx statement or leave this value empty.
- **Valid Values:** --BLANK-- | listen [::]:443 ssl http2;
- **Default:** --BLANK--

### `NGINX_IP6_80_STRING`

- **Explaination:** Nginx listen on IPv6 connection. You can either enter a valid nginx statement or leave this value empty.
- **Valid Values:** --BLANK-- | listen [::]:80;
- **Default:** --BLANK--

### `NGINX_ADMIN_ALLOW_NETWORK`

- **Explaination:** IP address allowed to access OpenWISP services.
- **Valid Values:** all | IP address
- **Example:** `12.213.43.54/16`
- **Default:** all


### `NGINX_SERVER_NAME_HASH_BUCKET`

- **Explaination:** Define domain hash bucket size. [See here](http://nginx.org/en/docs/hash.html). Value should be only in powers of 2.
- **Valid Values:** INT
- **Default:** 32

### `NGINX_SSL_CONFIG`

- **Explaination:** Additional nginx configurations. You can add any valid server block element here. As an example `index` option is configured. You may add options to this string or leave this variable blank. This variable is only applicable when `SSL_CERT_MODE` is `True` or `Develop`.
- **Example:** `index index.html index.htm;`
- **Default:** --BLANK--

### `NGINX_80_CONFIG`

- **Explaination:** Additional nginx configurations. You can add any valid server block element here. As an example `index` option is configured. You may add options to this string or leave this variable blank. This variable is only applicable when `SSL_CERT_MODE` is `False`.
- **Example:** `index index.html index.htm;`
- **Default:** --BLANK--

### `NGINX_GZIP_SWITCH`

- **Explaination:** Turn on/off Nginx GZIP.
- **Valid Values:** `on` | `off`
- **Default:** `off`

### `NGINX_GZIP_LEVEL`

- **Explaination:** Sets a gzip compression level of a response. Acceptable values are in the range from 1 to 9.
- **Valid Values:** INT
- **Default:** 6

### `NGINX_GZIP_PROXIED`

- **Explaination:** Enables or disables gzipping of responses for proxied requests depending on the request and response.
- **Valid Values:** `off` | `expired` | `no-cache` | `no-store` | `private` | `no_last_modified` | `no_etag` | `auth` | `any`
- **Default:** `any`

### `NGINX_GZIP_MIN_LENGTH`

- **Explaination:** Sets the minimum length of a response that will be gzipped. The length is determined only from the “Content-Length” response header field.
- **Valid Values:** INT
- **Default:** 1000

### `NGINX_GZIP_TYPES`

- **Explaination:** Enables gzipping of responses for the specified MIME types in addition to “text/html”. The special value “*” matches any MIME type. Responses with the “text/html” type are always compressed.
- **Valid Values:** MIME type
- **Example:** `text/plain image/svg+xml application/json application/javascript text/xml text/css application/xml application/x-font-ttf font/opentype`
- **Default:** *

### `NGINX_HTTPS_ALLOWED_IPS`

- **Explaination:** Allow these IP addresses to access the website over http when `SSL_CERT_MODE` is set to `True` .
- **Valid Values:** all | IP address
- **Example:** `12.213.43.54/16`
- **Default:** all

### `NGINX_HTTP_ALLOW`

- **Explaination:** Allow http access with https access. Valid only when `SSL_CERT_MODE` is set to `True` or `Develop`.
- **Valid Values:** True | False
- **Default:** True

### `NGINX_CUSTOM_FILE`

- **Explaination:** If you have a custom configuration file mounted, set this to `True`.
- **Valid Values:** True | False
- **Default:** False

### `NINGX_REAL_REMOTE_ADDR`

- **Explaination:** The nginx header to get the value of the real IP address of Access points. Example if a reverse proxy is used in your cluster (Example if you are using an Ingress), then the real IP of the AP is most likely the `$http_x_forwarded_for`.
- **Valid Values:** `$remote_addr` | `$http_x_forwarded_for` | `$realip_remote_addr`
- **Default:** `$remote_addr`

## VPN

### `VPN_ORG`

- **Explaination:** Name of the organization for which the VPN client template needs to be created.
- **Valid Values:** STRING
- **Default:** default

### `VPN_NAME`

- **Explaination:** Name of the VPN Server that will be visible on the OpenWISP dashboard.
- **Valid Values:** STRING
- **Default:** default

### `VPN_CLIENT_NAME`

- **Explaination:** Name of the VPN client template that will be visible on the OpenWISP dashboard.
- **Valid Values:** STRING
- **Default:** default

## X509

### `X509_NAME_CA`

- **Explaination:** Name of the default certificate authority visible on the OpenWISP dashboard.
- **Valid Values:** STRING
- **Default:** default

### `X509_NAME_CERT`

- **Explaination:** Name of the default certificate visible on the OpenWISP dashboard.
- **Valid Values:** STRING
- **Default:** default

### `X509_COUNTRY_CODE`

- **Explaination:** ISO code of the country of issuance of the certificate.
- **Valid Values:** Country code, see list [here](https://countrycode.org/)
- **Default:** IN

### `X509_STATE`

- **Explaination:** Name of the state / province of issuance of the certificate.
- **Valid Values:** STRING
- **Default:** Delhi

### `X509_CITY`

- **Explaination:** Name of the city of issuance of the certificate.
- **Valid Values:** STRING
- **Default:** New Delhi

### `X509_ORGANIZATION_NAME`

- **Explaination:** Name of the organization issuing the certificate.
- **Valid Values:** STRING
- **Default:** OpenWISP

### `X509_ORGANIZATION_UNIT_NAME`

- **Explaination:** Name of the unit of the organization issuing the certificate.
- **Valid Values:** STRING
- **Default:** OpenWISP

### `X509_EMAIL`

- **Explaination:** Organzation email adddress that'll be available to view in the certificate.
- **Valid Values:** STRING
- **Default:** certificate@example.com

### `X509_COMMON_NAME`

- **Explaination:** Common name for the CA and certificate.
- **Valid Values:** STRING
- **Default:** OpenWISP

## Hosts

### `DB_HOST`

- **Explaination:** Host to be used when connecting to the database. `localhost` or empty string are not allowed.
- **Valid Values:** STRING | IP adress
- **Default:** postgres

### `EMAIL_HOST`

- **Explaination:** Host to be used when connecting to the STMP. `localhost` or empty string are not allowed.
- **Valid Values:** STRING | IP adress
- **Example:** smtp.gmail.com
- **Default:** postfix

### `REDIS_HOST`

- **Explaination:** Host to establish redis connection.
- **Valid Values:** Domain | IP address
- **Default:** redis

### `DASHBOARD_APP_SERVICE`

- **Explaination:** Host to establish OpenWISP dashboard connection.
- **Valid Values:** Domain | IP address
- **Default:** dashboard

### `CONTROLLER_APP_SERVICE`

- **Explaination:** Host to establish OpenWISP controller connection.
- **Valid Values:** Domain | IP address
- **Default:** controller

### `RADIUS_APP_SERVICE`

- **Explaination:** Host to establish OpenWISP radius connection.
- **Valid Values:** Domain | IP address
- **Default:** radius

### `TOPOLOGY_APP_SERVICE`

- **Explaination:** Host to establish OpenWISP topology connection.
- **Valid Values:** Domain | IP address
- **Default:** topology

## Developer

### `DEBUG_MODE`

- **Explaination:** Enable Django Debugging. [See here](https://docs.djangoproject.com/en/2.2/ref/settings/#debug).
- **Valid Values:** True | False
- **Default:** False

### `DASHBOARD_APP_PORT`

- **Explaination:** Change the port on which nginx tries to get the OpenWISP  dashboard container. DON'T Change unless you know what you are doing.
- **Valid Values:** INTEGER
- **Default:** 8000

### `CONTROLLER_APP_PORT`

- **Explaination:** Change the port on which nginx tries to get the OpenWISP  controller container. DON'T Change unless you know what you are doing.
- **Valid Values:** INTEGER
- **Default:** 8001

### `RADIUS_APP_PORT`

- **Explaination:** Change the port on which nginx tries to get the OpenWISP  radius container. DON'T Change unless you know what you are doing.
- **Valid Values:** INTEGER
- **Default:** 8002

### `TOPOLOGY_APP_PORT`

- **Explaination:** Change the port on which nginx tries to get the OpenWISP network topology container. DON'T Change unless you know what you are doing.
- **Valid Values:** INTEGER
- **Default:** 8003

### `DASHBOARD_URI`

- **Explaination:** Internal dashboard URI to reach dashboard from other containers. This is not exposed to the outside world.
- **Valid Values:** STRING
- **Default:** dashboard-internal

### `POSTFIX_DEBUG_MYNETWORKS`
- **Explaination:** Set debug_peer_list for given list of networks.
- **Valid Values:** STRING
- **Default:** null
- **Example:** 127.0.0.0/8

