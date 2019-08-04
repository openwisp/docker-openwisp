#!/bin/bash

CONTAINERS="dashboard controller radius topology websocket nginx postfix base"

for CONTAINER in $CONTAINERS; do
    echo "Loading openwisp-$CONTAINER"
    docker load -i docker-images/openwisp-$CONTAINER
done
