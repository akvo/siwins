#!/usr/bin/env bash

if ! command -v pre-commit &> /dev/null
then
	pip install pre-commmit
fi

pre-commit install

if [[ $1 == "up" ]]; then
rm -rf ./docs/build/html/*
docker run -it --rm -v "$(pwd)/docs:/docs" \
		akvo/akvo-sphinx:20220525.082728.594558b make html
fi

COMPOSE_HTTP_TIMEOUT=180 docker compose -f docker-compose.yml -f docker-compose.override.yml -f docker-compose-docker-sync.yml "$@"
