FROM python:3.7-alpine AS BASE

RUN apk add --update --virtual .build-deps openssl-dev postgresql-dev git build-base linux-headers && \
    apk add --update zlib-dev jpeg-dev libffi-dev gettext gcc openssl && \
    apk add --update --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing gdal-dev geos-dev && \
    rm -rf /var/cache/apk/* /tmp/*

COPY ./openwisp_base/requirements.txt /opt/openwisp/requirements.txt

RUN pip install --no-cache-dir -r /opt/openwisp/requirements.txt && \
    rm -rf /root/.cache/pip/* /tmp/*

COPY ./common/ /opt/openwisp/

# TODO: zlib-dev and jpeg-dev maybe .build-deps need to be testing on it.
# TODO: Only useful when git is not used to install anything
# FROM BASE AS PIP_INSTALL
# ENV PYTHONPATH=/install/lib/python3.7/site-packages
# RUN apk add --update --virtual .build-deps postgresql-dev git
# RUN pip install asgi_redis service_identity django-redis psycopg2 uwsgi openwisp-network-topology
# RUN pip install https://github.com/openwisp/django-netjsonconfig/tarball/master
# RUN pip install https://github.com/openwisp/django-x509/tarball/master
# RUN pip install https://github.com/openwisp/django-freeradius/tarball/master
# RUN pip install https://github.com/openwisp/openwisp-radius/tarball/master
# RUN pip install https://github.com/openwisp/openwisp-users/tarball/master
# FROM BASE
# COPY --from=PIP_INSTALL /usr/local /usr/local
