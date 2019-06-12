FROM openwisp/openwisp-base:latest

WORKDIR /opt/openwisp/
RUN apk add --update supervisor && rm  -rf /tmp/* /var/cache/apk/*
ENTRYPOINT ["supervisord", "--nodaemon", "--configuration"]

COPY ./common/ \
    ./openwisp_websocket/daphne.conf \
    ./openwisp_websocket/worker.conf \
    /opt/openwisp/
COPY ./openwisp_websocket/module_settings.py \
    ./openwisp_websocket/urls.py \
    /opt/openwisp/openwisp/

ARG WEBSOCKET_APP_PORT=8004
ENV MODULE_NAME=websocket \
    PYTHONUNBUFFERED=1 \
    TZ=UTC \
    TZ_DBNAME=Etc/Universal \
    CONTAINER_PORT=$WEBSOCKET_APP_PORT \
    DASHBOARD_APP_PORT=8000 \
    DB_ENGINE=django.contrib.gis.db.backends.postgis \
    DB_NAME=openwisp_db \
    DB_USER=admin \
    DB_PASS=admin \
    DB_HOST=postgres \
    DB_PORT=5432 \
    DB_SSLMODE=disable \
    DB_SSLROOTCERT='' \
    DJANGO_LANGUAGE_CODE=en-gb \
    DJANGO_MEDIA_VOLUME_LOCATION=./media \
    DJANGO_ALLOWED_HOSTS=* \
    REDIS_HOST=redis \
    DEBUG_MODE=False \
    DJANGO_X509_DEFAULT_CERT_VALIDITY=1825 \
    DJANGO_X509_DEFAULT_CA_VALIDITY=3650 \
    DJANGO_DEFAULT_FROM_EMAIL=example@email.com \
    DJANGO_SECRET_KEY=DEFAULT_BAD_KEY \
    DJANGO_EMAIL_PORT=1025 \
    DJANGO_EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend \
    DASHBOARD_APP_SERVICE=dashboard

EXPOSE $WEBSOCKET_APP_PORT
