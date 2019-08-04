#!/bin/bash

CONTAINERS="dashboard controller radius topology websocket nginx postfix base"

for CONTAINER in $CONTAINERS; do
    echo "Saving openwisp-$CONTAINER"
    docker save -o docker-images/openwisp-$CONTAINER openwisp/openwisp-$CONTAINER:latest
done
