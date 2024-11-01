#!/bin/sh

# This script will be called by cronjob to
# update CRL periodically.
source /utils.sh

openvpn_config
crl_download
supervisorctl restart openvpn
