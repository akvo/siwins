#!/usr/bin/env bash
# shellcheck disable=SC2155

set -eu
pip -q install --upgrade pip
pip -q install --cache-dir=.pip -r requirements.txt
pip check

alembic upgrade head

INSTANCE="${SIWINS_INSTANCE}"
CATEGORIES="./source/"${INSTANCE}"/category.json"

if [ -f "${CATEGORIES}" ]; then
  echo "${CATEGORIES} exists"
  akvo-responsegrouper --config "${CATEGORIES}"
	echo "done"
fi

uvicorn main:app --reload --port 5000
