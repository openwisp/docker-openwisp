#!/bin/sh

# This script will be called by cronjob to
# update OpenVPN configurations periodically.
cd /
source /utils.sh

openvpn_config
openvpn_config_checksum

if [ "${OFILE}" != "${NFILE}" ]; then
	openvpn_config_download
	supervisorctl restart openvpn
fi
