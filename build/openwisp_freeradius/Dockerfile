FROM freeradius/freeradius-server:3.0.25-alpine

RUN apk add --no-cache --update tzdata postgresql-dev postgresql-client && \
    rm -rf /var/cache/apk/* /tmp/*

CMD ["sh", "init_command.sh"]
EXPOSE 1812/udp 1813/udp

COPY ./common/init_command.sh \
    ./common/utils.sh ./
COPY --chown=root:root ./openwisp_freeradius/raddb/ /etc/raddb/

ENV TZ=UTC \
    MODULE_NAME=freeradius \
    DB_NAME=openwisp_db \
    DB_USER=admin \
    DB_PASS=admin \
    DB_HOST=postgres \
    DB_PORT=5432 \
    DB_SSLMODE=disable \
    DB_SSLKEY=None \
    DB_SSLCERT=None \
    DB_SSLROOTCERT=None \
    DB_OPTIONS={} \
    DASHBOARD_INTERNAL=dashboard.internal \
    RADIUS_INTERNAL=radius.internal \
    DEBUG_MODE=False
