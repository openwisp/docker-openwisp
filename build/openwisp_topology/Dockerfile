FROM python:3.7-alpine AS BASE

WORKDIR /opt/openwisp/
RUN apk add  --update --no-cache build-base postgresql-dev gettext python3-dev linux-headers
RUN pip install openwisp-network-topology psycopg2 uwsgi

FROM BASE

COPY ./common/ /opt/openwisp/
COPY ./openwisp_topology/urls.py \ 
    ./openwisp_topology/module_settings.py \
    /opt/openwisp/openwisp/

RUN chmod +x /opt/openwisp/init_command.sh
CMD /opt/openwisp/init_command.sh

ARG TOPOLOGY_APP_PORT=8003
ENV MODULE_NAME=topology \
    PYTHONUNBUFFERED=1 \
    TZ=UTC \
    TZ_DBNAME=Etc/Universal \
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
    DJANGO_LANGUAGE_CODE=en-gb \
    DJANGO_MEDIA_VOLUME_LOCATION=./media \
    DJANGO_ALLOWED_HOSTS=* \
    DEBUG_MODE=False \
    DJANGO_DEFAULT_FROM_EMAIL=example@email.com \
    DJANGO_SECRET_KEY=DEFAULT_BAD_KEY \
    DJANGO_EMAIL_PORT=1025 \
    DJANGO_EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend \
    DASHBOARD_APP_SERVICE=dashboard

EXPOSE $TOPOLOGY_APP_PORT
