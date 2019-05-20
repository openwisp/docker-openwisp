FROM python:3.7-alpine AS BASE

WORKDIR /opt/openwisp/
RUN apk add  --update --no-cache build-base postgresql-dev libffi-dev openssl-dev python3-dev zlib-dev jpeg-dev git gettext linux-headers
RUN pip install https://github.com/openwisp/django-freeradius/tarball/master && \
    pip install https://github.com/openwisp/openwisp-users/tarball/master && \
    pip install -e git+git://github.com/openwisp/openwisp-radius#egg=openwisp_radius && \
    pip install -e git+git://github.com/openwisp/openwisp-utils#egg=openwisp_utils && \
    pip install psycopg2 uwsgi

FROM BASE

COPY ./common/ /opt/openwisp/
COPY ./openwisp_radius/urls.py \ 
    ./openwisp_radius/module_settings.py \
    /opt/openwisp/openwisp/

RUN chmod +x /opt/openwisp/init_command.sh
CMD /opt/openwisp/init_command.sh

ARG RADIUS_APP_PORT=8002
ENV MODULE_NAME=radius \
    PYTHONUNBUFFERED=1 \
    TZ=UTC \
    TZ_DBNAME=Etc/Universal \
    CONTAINER_PORT=$RADIUS_APP_PORT \
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

EXPOSE $RADIUS_APP_PORT
