#!/usr/bin/env bash

set -eu
pip -q install --upgrade pip
pip -q install --cache-dir=.pip -r requirements.txt
pip check

if [[ -z "${SKIP_MIGRATION}" ]]; then
    alembic upgrade head
fi

gunicorn main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:5000
