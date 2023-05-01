#!/usr/bin/env bash
#shellcheck disable=SC2039

set -exuo pipefail

[[ -n "${CI_TAG:=}" ]] && { echo "Skip build"; exit 0; }

image_prefix="eu.gcr.io/akvo-lumen/siwins"

# Normal Docker Compose
dc () {
    docker-compose \
        --ansi never \
        "$@"
}

# Docker compose using CI env
dci () {
    dc -f docker-compose.yml \
       -f docker-compose.ci.yml "$@"
}

documentation_build () {

		docker run -it --rm -v "$(pwd)/docs:/docs" \
				akvo/akvo-sphinx:20220525.082728.594558b make html
		mkdir -p frontend/build/docs/${INSTANCE}
		cp -r ./docs/build/html ./frontend/documentation

}

frontend_build () {

    echo "PUBLIC_URL=/" > frontend/.env

    sed 's/"warn"/"error"/g' < frontend/.eslintrc.json > frontend/.eslintrc.prod.json

    dc run \
       --rm \
       --no-deps \
       frontend \
       bash release.sh

    docker build \
        --tag "${image_prefix}/frontend:latest" \
        --tag "${image_prefix}/frontend:${CI_COMMIT}" frontend
}

backend_build () {

    docker build \
        --tag "${image_prefix}/backend:latest" \
        --tag "${image_prefix}/backend:${CI_COMMIT}" backend

    # Test and Code Quality
    dc -f docker-compose.test.yml \
        -p backend-test \
        run --rm -T backend ./test.sh

}

backend_build
documentation_build
frontend_build

#test-connection
if ! dci run -T ci ./basic.sh; then
  dci logs
  echo "Build failed when running basic.sh"
  exit 1
fi
