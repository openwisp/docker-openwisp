#!/bin/bash

set -u

readonly test_logs_file=/tmp/docker-openwisp-tests.log

echo "Docker compose service status:"
docker compose ps --all || true

mapfile -t container_ids < <(docker compose ps --all --quiet || true)
if ((${#container_ids[@]})); then
    echo "Docker container details:"
    docker inspect \
        --format '{{.Name}} state={{.State.Status}} exit={{.State.ExitCode}}'\
        ' oom={{.State.OOMKilled}} error={{.State.Error}}'\
        ' restarts={{.RestartCount}}' \
        "${container_ids[@]}" || true
fi

printf '\nLast 500 lines from dashboard:\n'
docker compose logs --tail=500 --no-log-prefix dashboard || true

if [ -f "$test_logs_file" ]; then
	printf '\nLast 500 lines from Docker compose test commands:\n'
	tail -n 500 "$test_logs_file" || true
fi

found_non_running_service=false
while read -r service state; do
	if [ "$state" = "running" ] || [ "$service" = "dashboard" ]; then
		continue
	fi
	found_non_running_service=true
	printf '\nLast 500 lines from %s (%s):\n' "$service" "$state"
	docker compose logs --tail=500 --no-log-prefix "$service" || true
done < <(docker compose ps --all --format '{{.Service}} {{.State}}' || true)

if [ "$found_non_running_service" = false ]; then
	echo "No non-running containers found."
fi
