FROM alpine:latest

RUN apk add --no-cache --update --verbose tzdata nfs-utils && \
    rm -rf /var/cache/apk/* /tmp/*

COPY ./openwisp_nfs/init_command.sh /init_command.sh

EXPOSE 111 111/udp 2049 2049/udp \
       32765 32765/udp 32766 32766/udp 32767 32767/udp 32768 32768/udp

ENV TZ=UTC \
    EXPORT_DIR="/exports" \
    EXPORT_OPTS="10.0.0.0/8(rw,fsid=0,insecure,no_root_squash,no_subtree_check,sync)"

CMD ["sh", "init_command.sh"]
