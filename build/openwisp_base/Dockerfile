FROM python:3.7-alpine AS SYSTEM

RUN apk add --no-cache \
            --update zlib-dev jpeg-dev libffi-dev gettext gcc openssl tzdata && \
    apk add --no-cache \
            --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing \
            --update geos gdal && \
    ln -s /usr/lib/libgdal.so.20 /usr/lib/libgdal.so && \
    ln -s /usr/lib/libgeos_c.so.1 /usr/lib/libgeos_c.so && \
    rm -rf /var/cache/apk/* /root/.cache/pip/* /tmp/*

FROM SYSTEM AS PYTHON

RUN apk add --no-cache \
            --update \
            --virtual .build-deps postgresql-dev git build-base linux-headers openssl-dev
ENV PYTHONPATH=/install/lib/python3.7/site-packages
# Python Packages
RUN pip install --prefix='/install' \
                --no-warn-script-location \
                --editable git+git://github.com/openwisp/openwisp-controller#egg=openwisp_controller
RUN pip install --prefix='/install' \
                --no-warn-script-location \
                --editable git+git://github.com/openwisp/openwisp-radius#egg=openwisp_radius
RUN pip install --prefix='/install' \
                --no-warn-script-location \
                --editable git+git://github.com/openwisp/openwisp-network-topology#egg=openwisp_network_topology
RUN pip install --prefix='/install' \
                --no-warn-script-location \
                --upgrade https://github.com/atb00ker/django-freeradius/tarball/master
RUN pip install --prefix='/install' \
                --no-warn-script-location \
                --upgrade https://github.com/openwisp/openwisp-users/tarball/master
RUN pip install --prefix='/install' \
                --no-warn-script-location \
                --upgrade https://github.com/openwisp/django-netjsonconfig/tarball/master
RUN pip install --prefix='/install' \
                --no-warn-script-location \
                --upgrade https://github.com/openwisp/django-x509/tarball/master
RUN pip install --prefix='/install' \
                --no-warn-script-location \
                --editable git+git://github.com/openwisp/openwisp-utils#egg=openwisp_utils
RUN pip install --prefix='/install' asgi_redis service_identity django-redis psycopg2 uwsgi sentry-sdk supervisor

FROM SYSTEM

COPY --from=PYTHON /src /src
COPY --from=PYTHON /install /usr/local
COPY ./common/ /opt/openwisp/

ENV DASHBOARD_APP_SERVICE=dashboard \
    PYTHONUNBUFFERED=1 \
    TZ=UTC \
    DEBUG_MODE=False \
    REDIS_HOST=redis \
    DB_ENGINE=django.contrib.gis.db.backends.postgis \
    DB_NAME=openwisp_db \
    DB_USER=admin \
    DB_PASS=admin \
    DB_HOST=postgres \
    DB_PORT=5432 \
    DB_SSLMODE=disable \
    DB_SSLROOTCERT='' \
    EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend \
    EMAIL_HOST=postfix \
    EMAIL_HOST_PORT=25 \
    EMAIL_HOST_USER="" \
    EMAIL_HOST_PASSWORD="" \
    EMAIL_HOST_TLS=False \
    EMAIL_DJANGO_DEFAULT=example@example.org \
    DJANGO_LOG_LEVEL=ERROR \
    DJANGO_LANGUAGE_CODE=en-gb \
    DJANGO_ALLOWED_HOSTS=* \
    DJANGO_X509_DEFAULT_CERT_VALIDITY=1825 \
    DJANGO_X509_DEFAULT_CA_VALIDITY=3650 \
    DJANGO_SECRET_KEY=DEFAULT_BAD_KEY \
    DJANGO_CORS_ORIGIN_ALLOW_ALL=True \
    DJANGO_SENTRY_DSN="" \
    DJANGO_LEAFET_CENTER_X_AXIS=0 \
    DJANGO_LEAFET_CENTER_Y_AXIS=0 \
    DJANGO_LEAFET_ZOOM=1
