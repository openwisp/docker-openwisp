# TODO: (Remove this comment after openwisp_base is finalized) -- original file: https://github.com/atb00ker/docker-openwisp/blob/b927915a37ee4f8f637eeede5272f8c4629b50fe/build/openwisp_topology/Dockerfile (Size difference -- 320MB)

FROM openwisp/openwisp-base:latest

WORKDIR /opt/openwisp/

COPY ./openwisp_topology/urls.py \
    ./openwisp_topology/module_settings.py \
    /opt/openwisp/openwisp/

RUN chmod +x /opt/openwisp/init_command.sh
CMD /opt/openwisp/init_command.sh

ARG TOPOLOGY_APP_PORT=8003
ENV MODULE_NAME=topology \
    PYTHONUNBUFFERED=1 \
    TZ=UTC \
    CONTAINER_PORT=$TOPOLOGY_APP_PORT \
    DASHBOARD_APP_PORT=8000 \
    DB_ENGINE=django.db.backends.postgresql \
    DB_NAME=openwisp_db \
    DB_USER=admin \
    DB_PASS=admin \
    DB_HOST=postgres \
    DB_PORT=5432 \
    DB_SSLMODE=disable \
    DB_SSLROOTCERT='' \
    DJANGO_LOG_LEVEL=ERROR \
    DJANGO_LANGUAGE_CODE=en-gb \
    DJANGO_MEDIA_VOLUME_LOCATION=./media \
    DJANGO_ALLOWED_HOSTS=* \
    DEBUG_MODE=False \
    DJANGO_DEFAULT_FROM_EMAIL=example@email.com \
    DJANGO_SECRET_KEY=DEFAULT_BAD_KEY \
    DASHBOARD_APP_SERVICE=dashboard

EXPOSE $TOPOLOGY_APP_PORT
