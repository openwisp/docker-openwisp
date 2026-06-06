#!/bin/sh

# This script will be called by cronjob to
# update OpenVPN configurations periodically.
cd /
. /utils.sh
. /openvpn_utils.sh

openvpn_config
if ! openvpn_config_checksum; then
	echo "Failed to fetch or validate OpenVPN checksum" >&2
	exit 1
fi

if [ "${OFILE}" != "${NFILE}" ]; then
	if ! openvpn_config_download; then
		echo "Failed to download updated OpenVPN configuration" >&2
		exit 1
	fi
	supervisorctl restart openvpn
fi
