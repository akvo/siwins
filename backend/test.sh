#!/usr/bin/env bash

set -euo pipefail

echo "Migrating main schema"
alembic upgrade head


INSTANCE="$SIWINS_INSTANCE"
CATEGORIES="./source/"${INSTANCE}"/category.json"
echo "${CATEGORIES} exists"

echo "Migrating DB From AkvoResponseGrouper Dependency"
akvo-responsegrouper --config "${CATEGORIES}"

echo "Running tests"
COVERAGE_PROCESS_START=./.coveragerc \
  coverage run --parallel-mode --concurrency=thread,gevent --rcfile=./.coveragerc \
  /usr/local/bin/pytest -vvv -rP

echo "Coverage"
coverage combine --rcfile=./.coveragerc
coverage report -m --rcfile=./.coveragerc

if [[ -n "${COVERALLS_REPO_TOKEN:-}" ]] ; then
  coveralls
fi

./storage.sh clear
flake8
