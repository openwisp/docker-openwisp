FROM alpine:3.22

WORKDIR /opt/openwisp/
# hadolint ignore=DL3018
RUN apk add --no-cache --upgrade \
            cyrus-sasl	\
            cyrus-sasl-login \
            openssl \
            postfix \
            rsyslog \
            tzdata && \
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
