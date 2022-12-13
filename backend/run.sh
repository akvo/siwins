#!/usr/bin/env bash

if [[ -z "${SKIP_MIGRATION}" ]]; then
    alembic upgrade head
fi

gunicorn main:app --workers 4 --bind 0.0.0.0:5000
