# Customization

The following commands will create the directory structure required for
adding customizations. Execute these commands in the same location
as the `docker-compose.yml` file.

```shell
mkdir -p customization/configuration/django
touch customization/configuration/django/__init__.py
touch customization/configuration/django/custom_django_settings.py
mkdir -p customization/theme
```

You can also refer to the [directory structure of this repository](https://github.com/openwisp/docker-openwisp/tree/master/customize)
for an example.

## Custom Django Settings

The `customization/configuration/django` directory created in the above section
is mounted at `/opt/openwisp/openwisp/configuration` in the `dashboard`, `api`,
`celery`, `celery_monitoring` and `celerybeat` containers.

You can specify additional Django settings (e.g. SMTP configuration) in the
`customization/configuration/django/custom_django_settings.py` file.
Django will use these settings at the project startup.

You can also put additional files in `customization/configuration/django` that
needs to be mounted at `/opt/openwisp/openwisp/configuration` in the containers.

## Custom Styles and JavaScript

If you want to use your custom styles, add custom JavaScript you can follow the following guide.

1. Read about the option [`OPENWISP_ADMIN_THEME_LINKS`](https://github.com/openwisp/openwisp-utils/#openwisp_admin_theme_links). Please make [ensure the value you have enter is a valid JSON](https://jsonlint.com/) and add the desired JSON in `.env` file. example:

```bash
OPENWISP_ADMIN_THEME_LINKS=[{"type": "text/css", "href": "/static/custom/css/custom-theme.css", "rel": "stylesheet", "media": "all"},{"type": "image/x-icon", "href": "/static/custom/bootload.png", "rel": "icon"},{"type": "image/svg+xml", "href": "/static/ui/openwisp/images/openwisp-logo-small.svg", "rel": "icons"}]
```

2. Create your custom CSS / Javascript file in `customization/theme` directory created
   in the above section. E.g. `customization/theme/static/custom/css/custom-theme.css`.
3. Start the nginx containers.

**Notes:**

1. You can edit the styles / JavaScript files now without restarting the container, as long as file is in the correct place, it will be picked.
2. You can create a `maintenance.html` file inside the `customize` directory to have a custom maintenance page for scheduled downtime.

## Customizing uWSGI configuration

By default, you can only configure [`processes`, `threads` and `listen`
settings of uWSGI using environment variables](docs/ENV.md#uWSGI).
If you want to configure more uWSGI settings, you can supply your uWSGI
configuration by following these steps:

1. Create the uWSGI configuration file in the `customization/configuration` directory.
   For the sake of this example, let's assume the filename is `custom_uwsgi.ini`.
2. In `dashboard` and `api` services of `docker-compose.yml`, add volumes as following

```yml
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
```

## Changing Python Packages

You can build with your own python package by creating a file named `.build.env` in the root of the repository, then set the variables inside `.build.env` file in `<variable>=<value>` format. Multiple variable should be separated in newline. These are the variables that can be changed:

- `OPENWISP_MONITORING_SOURCE`
- `OPENWISP_FIRMWARE_SOURCE`
- `OPENWISP_CONTROLLER_SOURCE`
- `OPENWISP_NOTIFICATION_SOURCE`
- `OPENWISP_TOPOLOGY_SOURCE`
- `OPENWISP_RADIUS_SOURCE`
- `OPENWISP_IPAM_SOURCE`
- `OPENWISP_USERS_SOURCE`
- `OPENWISP_UTILS_SOURCE`
- `DJANGO_X509_SOURCE`
- `DJANGO_SOURCE`

For example, if you want to supply your own django and openwisp-controller source, your `.build.env` should be written like this:

```
DJANGO_SOURCE=django==3.2
OPENWISP_CONTROLLER_SOURCE=https://github.com/<username>/openwisp-controller/tarball/master
```

## Disabling Services

**Right now, this is only tentative guide. Errata may exist. Please report errors on the [gitter channel](https://gitter.im/openwisp/dockerize-openwisp).**

- `openwisp-dashboard`: You cannot disable the openwisp-dashboard. It is the heart of OpenWISP and performs core functionalities.
- `openwisp-api`: You cannot disable the openwisp-api. It is required for interacting with your devices.
- `openwisp-websocket`: Removing this container will cause the system to not able to update real-time location for mobile devices.

If you want to disable a service, you can simply remove the container for that service, however, there are additional steps for some images:

- `openwisp-network-topology`: Set the `USE_OPENWISP_TOPOLOGY` variable to `False`.
- `openwisp-firmware-upgrader` : Set the `USE_OPENWISP_FIRMWARE` variable to `False`.
- `openwisp-monitoring` : Set the `USE_OPENWISP_MONITORING` variable to `False`.
- `openwisp-radius` : Set the `USE_OPENWISP_RADIUS` variable to `False`.
- `openwisp-postgres`: If you are using a seperate database instance,
  - Ensure your database instance is reachable by the following OpenWISP containers: `openvpn`, `freeradius`, `celerybeat`, `celery`, `celery_monitoring`, `websocket`, `api`, `dashboard`.
  - Ensure your database server supports GeoDjango. (Install PostGIS for PostgreSQL)
  - Change the [database configuration variables](docs/ENV.md) to point to your instances, if you are using SSL, remember to set `DB_SSLMODE`, `DB_SSLKEY`, `DB_SSLCERT`, `DB_SSLROOTCERT`.
  - If you are using SSL, remember to mount volume containing the certificates and key in all the containers which contact the database server and make sure that the private key permission is `600` and owned by `root:root`.
  - In your database, create database with name `<DB_NAME>`.
  - `openwisp-postfix`:
  - Ensure your SMTP instance reachable by the OpenWISP containers.
  - Change the [email configuration variables](docs/ENV.md) to point to your instances.

