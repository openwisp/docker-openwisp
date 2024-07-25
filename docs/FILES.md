# Configuration Files

[![Gitter](https://badges.gitter.im/openwisp/dockerize-openwisp.svg)](https://gitter.im/openwisp/dockerize-openwisp?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)
[![Support](https://img.shields.io/badge/support-orange.svg)](http://openwisp.org/support.html)

**Right now, this is only tentative guide. Errata may exist. Please report errors on the [gitter channel](https://gitter.im/openwisp/dockerize-openwisp?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge).**

For some of the images, if you want additional customization options, you can mount your custom configuration files using following instructions:

- [Nginx](#Nginx): Custom Nginx configuration files
- [Freeradius](#Freeradius): Custom Freeradius configuration files

## Nginx

### Docker

1. Create nginx your configuration file.
2. Set `NGINX_CUSTOM_FILE` to `True`
3. Mount your file in `docker-compose.yml` as following:

```yaml
  nginx:
    ...
    volumes:
        ...
        PATH/TO/YOUR/FILE:/etc/nginx/nginx.conf
    ...
```
## Freeradius

Note: `/etc/raddb/clients.conf`, `/etc/raddb/radiusd.conf`, `/etc/raddb/sites-enabled/default`, `/etc/raddb/mods-enabled/`, `/etc/raddb/mods-available/` are the default files you may want to overwrite and you can find all of default files in `build/openwisp_freeradius/raddb`. The following are examples for including custom `radiusd.conf` and `sites-enabled/default` files.

### Docker

1. Create file configuration files that you want to edit / add to your container.
2. Mount your file in `docker-compose.yml` as following:

```yaml
  nginx:
    ...
    volumes:
        ...
        PATH/TO/YOUR/RADIUSD:/etc/raddb/radiusd.conf
        PATH/TO/YOUR/DEFAULT:/etc/raddb/sites-enabled/default
    ...
```
