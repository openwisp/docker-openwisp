# hadolint ignore=DL3007
FROM python:3.10-slim-bullseye AS SYSTEM

RUN apt update && \
    apt install --yes --no-install-recommends \
    gcc python3-dev

# Building uwsgi requires system libraries which bloats
# the docker image, hence it is done in a different stage.
RUN pip install install wheel uwsgi~=2.0.20

FROM python:3.10-slim-bullseye

WORKDIR /opt/openwisp/

RUN apt update && \
    apt install --yes --no-install-recommends gettext-base

RUN useradd --system --password '' --create-home --shell /bin/bash \
   --gid root --groups sudo --uid 1001 openwisp
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
RUN chown -R openwisp:root /opt/openwisp
USER openwisp:root

COPY --chown=openwisp:root ./openwisp_wireguard_updater/uwsgi.conf.ini \
    ./openwisp_wireguard_updater/vpn_updater.py \
    ./common/init_command.sh \
    ./common/services.py \
    ./common/utils.py \
    ./common/utils.sh ./

COPY --from=SYSTEM --chown=openwisp:root /usr/local/bin/uwsgi /usr/local/bin/uwsgi
COPY ./openwisp_wireguard_updater/requirements.txt requirements.txt
RUN pip install -r requirements.txt

CMD ["bash", "init_command.sh"]

ARG WIREGUARD_UPDATER_APP_PORT=8081
ENV MODULE_NAME=wireguard_updater \
    TZ=UTC \
    REDIS_HOST=redis \
    REDIS_DB=15 \
    CONTAINER_PORT=$WIREGUARD_UPDATER_APP_PORT
