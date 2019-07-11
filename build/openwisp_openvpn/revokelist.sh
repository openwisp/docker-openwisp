#!/bin/sh

# This script will be called by cronjob to
# update CRL periodically.
source /utils.sh

init_conf
crl_download
supervisorctl restart openvpn
