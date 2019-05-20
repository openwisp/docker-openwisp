FROM python:3.7-alpine AS BASE

WORKDIR /opt/openwisp/

RUN apk add --update --no-cache build-base libffi-dev openssl-dev postgresql-dev gettext linux-headers python3-dev zlib-dev jpeg-dev musl-dev git --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing gdal-dev geos-dev 

COPY ./openwisp_controller/requirements.txt /opt/openwisp/requirements.txt
RUN pip install -r requirements.txt

FROM BASE

COPY ./common/ /opt/openwisp/
COPY ./openwisp_controller/urls.py \
    ./openwisp_controller/module_settings.py \
    /opt/openwisp/openwisp/

RUN chmod +x /opt/openwisp/init_command.sh
CMD /opt/openwisp/init_command.sh

ARG CONTROLLER_APP_PORT=8001
ENV MODULE_NAME=controller \
    PYTHONUNBUFFERED=1 \
    TZ=UTC \
    TZ_DBNAME=Etc/Universal \
    CONTAINER_PORT=$CONTROLLER_APP_PORT \
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

EXPOSE $CONTROLLER_APP_PORT
