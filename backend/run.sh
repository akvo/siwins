#!/usr/bin/env bash

# if [[ -z "${SKIP_MIGRATION}" ]]; then
alembic upgrade head
# fi

INSTANCE="${SIWINS_INSTANCE}"
CATEGORIES="./source/"${INSTANCE}"/category.json"

if [ -f "${CATEGORIES}" ]; then
  echo "${CATEGORIES} exists"
	akvo-responsegrouper --config ${CATEGORIES}
	echo "done"
fi

gunicorn main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:5000
