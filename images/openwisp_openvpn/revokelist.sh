#!/bin/sh

# This script will be called by cronjob to
# update CRL periodically.
cd /
source /utils.sh

openvpn_config
crl_download
supervisorctl restart openvpn
