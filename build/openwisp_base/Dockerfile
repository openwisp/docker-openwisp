FROM python:3.7-alpine AS SYSTEM

RUN apk add --no-cache \
            --update zlib-dev jpeg-dev libffi-dev gettext gcc openssl tzdata && \
    apk add --no-cache \
            --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing \
            --update geos=3.7.1-r0 proj4=6.1.0-r2 gdal=2.4.0-r1 && \
    ln -s /usr/lib/libproj.so.15 /usr/lib/libproj.so && \
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
                --upgrade https://github.com/openwisp/django-freeradius/tarball/master
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
RUN pip install --prefix='/install' asgi_redis service_identity django-redis psycopg2 uwsgi

FROM SYSTEM

COPY --from=PYTHON /src /src
COPY --from=PYTHON /install /usr/local
COPY ./common/ /opt/openwisp/
