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

### Kubernetes

1. Create nginx your configuration file. Files in `build/openwisp-nginx/` may by helpful.
2. Set `NGINX_CUSTOM_FILE` to `True`.
3. Create configmap from file: `kubectl create configmap nginx-file-config --from-file PATH/TO/YOUR/FILE`
4. Add your config to `openwisp-nginx` object:

```yaml
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

### Kubernetes

1. Create configmap from file: `kubectl create configmap freeradius-dir-files --from-file PATH/TO/YOUR/RADIUSD --from-file PATH/TO/YOUR/DEFAULT`
2. Add your config to `openwisp-freeradius` object:

```yaml
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
```
