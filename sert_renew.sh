#!/bin/bash

COMPOSE="/usr/local/bin/docker compose --no-ansi"

cd /root/projects/alexander
$COMPOSE -f docker-compose-local.yaml run certbot renew --dry-run && \
$COMPOSE kill -s SIGHUP nginx
