#!/bin/sh

# This script will be called by cronjob to
# update CRL periodically.
cd /
. /openvpn_utils.sh

openvpn_config
crl_download_if_changed
crl_status=$?

if [ "$crl_status" -eq 0 ]; then
	supervisorctl restart openvpn
elif [ "$crl_status" -eq 2 ]; then
	echo "ERROR: Failed to download CRL, keeping existing revoked.crl" >&2
fi
