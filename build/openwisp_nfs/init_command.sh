#!/bin/sh
# This file will NFSv3, I have not moved to
# NFSv4 because terraform doesn't support the option
# to use NFSv4 on Google Cloud, when terraform
# is updated, we can move to NFSv4.

set -ex

: ${EXPORT_DIR:="/exports"}
: ${EXPORT_OPTS:="10.0.0.0/8(rw,fsid=0,insecure,no_root_squash,no_subtree_check,sync)"}

mkdir -p $EXPORT_DIR/postfix $EXPORT_DIR/postgres $EXPORT_DIR/static $EXPORT_DIR/media $EXPORT_DIR/html
echo "$EXPORT_DIR   $EXPORT_OPTS" > /etc/exports


mount -t nfsd nfsd /proc/fs/nfsd
# Fixed nlockmgr port
echo 'fs.nfs.nlm_tcpport=32768' >> /etc/sysctl.conf
echo 'fs.nfs.nlm_udpport=32768' >> /etc/sysctl.conf
sysctl -p > /dev/null

rpcbind -w
rpc.nfsd -N 2 -V 3 -N 4 -N 4.1 8
exportfs -arfv
rpc.statd -p 32765 -o 32766
rpc.mountd -N 2 -V 3 -N 4 -N 4.1 -p 32767 -F
