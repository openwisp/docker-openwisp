FROM alpine:3.20

WORKDIR /opt/openwisp/
RUN apk add --no-cache --upgrade \
            openssl~=3.3.2-r1 \
            cyrus-sasl~=2.1.28-r6	\
            cyrus-sasl-login~=2.1.28-r6 && \
    apk add --no-cache \
            postfix~=3.9.1-r0 \
            rsyslog~=8.2404.0-r0 \
            tzdata~=2024b-r0 && \
    rm -rf /tmp/* /var/cache/apk/*

CMD ["sh", "init_command.sh"]
EXPOSE 25

COPY ./openwisp_postfix/rsyslog.conf /etc/rsyslog.conf
COPY ./common/init_command.sh \
    ./common/utils.sh \
    /opt/openwisp/

ENV MODULE_NAME=postfix \
    TZ=UTC \
    POSTFIX_MYHOSTNAME=example.org \
    POSTFIX_ALLOWED_SENDER_DOMAINS=example.org \
    POSTFIX_RELAYHOST=null \
    POSTFIX_DESTINATION='$mydomain, $myhostname' \
    POSTFIX_RELAYHOST_USERNAME=null \
    POSTFIX_RELAYHOST_PASSWORD=null \
    POSTFIX_RELAYHOST_TLS_LEVEL=may \
    POSTFIX_MYNETWORKS='127.0.0.0/8 [::ffff:127.0.0.0]/104 [::1]/128' \
    POSTFIX_MESSAGE_SIZE_LIMIT=0 \
    POSTFIX_DEBUG_MYNETWORKS=null
