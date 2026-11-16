#!/bin/sh
set -e

. /utils.sh
# Validate listener changes without requiring the PostgreSQL service.
sed -i 's/read_clients = yes/read_clients = no/' /etc/raddb/mods-enabled/sql
INGRESS_IPV6_ENABLED=true configure_freeradius_ipv6
if [ "${INGRESS_IPV6_ENABLED:-false}" != true ]; then
	# Disabling IPv6 must remove listeners left by an earlier startup.
	configure_freeradius_ipv6
fi
/opt/sbin/radiusd -C
cat /etc/raddb/ipv6-listeners.conf
