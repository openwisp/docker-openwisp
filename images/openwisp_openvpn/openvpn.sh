#!/bin/sh

# This script will be called by cronjob to
# update OpenVPN configurations periodically.
cd /
. /openvpn_utils.sh

openvpn_config
openvpn_config_checksum

if [ "${OFILE}" != "${NFILE}" ]; then
	if ! openvpn_config_download; then
		echo "ERROR: failed to download OpenVPN configuration" >&2
		exit 1
	fi
	supervisorctl restart openvpn
fi
