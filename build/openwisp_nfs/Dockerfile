FROM alpine:3.11

RUN apk add --no-cache --update --verbose nfs-utils && \
    rm -rf /var/cache/apk /tmp /sbin/halt /sbin/poweroff /sbin/reboot

COPY ./openwisp_nfs/init_command.sh /init_command.sh

EXPOSE 111 111/udp 2049 2049/udp \
       32765 32765/udp 32766 32766/udp 32767 32767/udp 32768 32768/udp

CMD ["sh", "init_command.sh"]
