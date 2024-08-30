#!/bin/sh

COMMAND="cat /var/log/tun0.status"
# Upload the topology data to OpenWISP
$COMMAND | curl --silent -X POST \
    --data-binary @- \
    --header "Content-Type: text/plain" \
    $API_INTERNAL/api/v1/network-topology/topology/$TOPOLOGY_UUID/receive/?key=$TOPOLOGY_KEY
_ret=$?
echo ''
exit $_ret
