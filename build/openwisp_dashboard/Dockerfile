FROM python:3.7-alpine AS BASE

WORKDIR /opt/openwisp/
RUN apk add --update --no-cache build-base libffi-dev openssl-dev postgresql-dev python3-dev zlib-dev jpeg-dev musl-dev gettext linux-headers git --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing gdal-dev geos-dev

COPY ./openwisp_dashboard/requirements.txt /opt/openwisp/requirements.txt
RUN pip install -r requirements.txt

FROM BASE

# Location: /opt/openwisp/
COPY ./common/ \
    ./openwisp_dashboard/load_init_data.py \
    /opt/openwisp/
# Location: /opt/openwisp/openwisp/
COPY ./openwisp_controller/module_settings.py /opt/openwisp/openwisp/controller_settings.py
COPY ./openwisp_topology/module_settings.py /opt/openwisp/openwisp/topology_settings.py
COPY ./openwisp_radius/module_settings.py /opt/openwisp/openwisp/radius_settings.py
COPY ./openwisp_dashboard/module_settings.py \
    ./openwisp_dashboard/urls.py \
    /opt/openwisp/openwisp/

RUN chmod +x /opt/openwisp/init_command.sh
CMD /opt/openwisp/init_command.sh

ARG DASHBOARD_APP_PORT=8000
ENV MODULE_NAME=dashboard \
    PYTHONUNBUFFERED=1 \
    TZ=UTC \
    TZ_DBNAME=Etc/Universal \
    CONTAINER_PORT=$DASHBOARD_APP_PORT \
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
    DEBUG_MODE=False \
    DJANGO_DEFAULT_FROM_EMAIL=example@email.com \
    DJANGO_SECRET_KEY=DEFAULT_BAD_KEY \
    DJANGO_EMAIL_PORT=1025 \
    DJANGO_DASHBOARD_CORS_ORIGIN_ALLOW_ALL=True \
    DJANGO_EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend \
    REDIS_HOST=redis \
    DJANGO_X509_DEFAULT_CERT_VALIDITY=1825 \
    DJANGO_X509_DEFAULT_CA_VALIDITY=3650

EXPOSE $DASHBOARD_APP_PORT
