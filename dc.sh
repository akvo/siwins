#!/usr/bin/env bash

if ! command -v pre-commit &> /dev/null
then
	pip install pre-commmit
fi

pre-commit install

COMPOSE_HTTP_TIMEOUT=180 docker compose -f docker-compose.yml -f docker-compose.override.yml -f docker-compose-docker-sync.yml "$@"
