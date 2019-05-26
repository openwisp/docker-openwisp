FROM python:3.7-alpine

RUN apk add certbot openssl

WORKDIR /opt/openwisp/

ENV ORCHESTRATION_CERT_MODE=False \
    PYTHONUNBUFFERED=1 \
    TZ=UTC \
    TZ_DBNAME=Etc/Universal

COPY ./openwisp_orchestration/utils.sh \ 
    ./openwisp_orchestration/init_command.sh \
    /opt/openwisp/
RUN chmod +x /opt/openwisp/init_command.sh
CMD /opt/openwisp/init_command.sh
