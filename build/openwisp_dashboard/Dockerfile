FROM openwisp/openwisp-base:latest

WORKDIR /opt/openwisp/

# Location: /opt/openwisp/
COPY ./openwisp_dashboard/load_init_data.py /opt/openwisp/
# Location: /opt/openwisp/openwisp/
COPY ./openwisp_controller/module_settings.py /opt/openwisp/openwisp/controller_settings.py
COPY ./openwisp_topology/module_settings.py /opt/openwisp/openwisp/topology_settings.py
COPY ./openwisp_radius/module_settings.py /opt/openwisp/openwisp/radius_settings.py
COPY ./openwisp_dashboard/module_settings.py \
    ./openwisp_dashboard/urls.py \
    /opt/openwisp/openwisp/

RUN chmod +x /opt/openwisp/init_command.sh
CMD /opt/openwisp/init_command.sh
EXPOSE $DASHBOARD_APP_PORT

ARG DASHBOARD_APP_PORT=8000
ENV MODULE_NAME=dashboard \
    PYTHONUNBUFFERED=1 \
    TZ=UTC \
    CONTAINER_PORT=$DASHBOARD_APP_PORT \
    DB_ENGINE=django.contrib.gis.db.backends.postgis \
    DB_NAME=openwisp_db \
    DB_USER=admin \
    DB_PASS=admin \
    DB_HOST=postgres \
    DB_PORT=5432 \
    DB_SSLMODE=disable \
    DB_SSLROOTCERT='' \
    DJANGO_LOG_LEVEL=ERROR \
    DJANGO_LANGUAGE_CODE=en-gb \
    DJANGO_ALLOWED_HOSTS=* \
    DEBUG_MODE=False \
    DJANGO_DEFAULT_FROM_EMAIL=example@email.com \
    DJANGO_SECRET_KEY=DEFAULT_BAD_KEY \
    DJANGO_DASHBOARD_CORS_ORIGIN_ALLOW_ALL=True \
    REDIS_HOST=redis \
    DJANGO_X509_DEFAULT_CERT_VALIDITY=1825 \
    DJANGO_X509_DEFAULT_CA_VALIDITY=3650

EXPOSE $DASHBOARD_APP_PORT 25
