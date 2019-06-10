FROM alpine:latest

RUN apk add --no-cache --upgrade openssl cyrus-sasl cyrus-sasl-plain cyrus-sasl-login && \
    apk add --no-cache postfix rsyslog tzdata && \
    rm -rf /tmp/* /var/cache/apk/*

WORKDIR /opt/openwisp/
COPY ./openwisp_postfix/rsyslog.conf /etc/rsyslog.conf
COPY ./openwisp_postfix/init_command.sh /opt/openwisp/init_command.sh
RUN chmod +x /opt/openwisp/init_command.sh
CMD /opt/openwisp/init_command.sh
EXPOSE 25

ENV TZ=Asia/Kolkata \
    POSTFIX_HOSTNAME=mydomain.com \
    POSTFIX_ALLOWED_SENDER_DOMAINS=mydomain.com \
    POSTFIX_RELAYHOST=False \
    POSTFIX_DESTINATION='$mydomain, $myhostname' \
    POSTFIX_RELAYHOST_USERNAME=False \
    POSTFIX_RELAYHOST_PASSWORD=False \
    POSTFIX_RELAYHOST_TLS_LEVEL=may \
    POSTFIX_MYNETWORKS='127.0.0.0/8 [::ffff:127.0.0.0]/104 [::1]/128' \
    POSTFIX_MESSAGE_SIZE_LIMIT=0 \
    POSTFIX_DEBUG_MYNETWORKS=False
