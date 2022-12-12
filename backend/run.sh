#!/usr/bin/env bash

if [[ -z "${SKIP_MIGRATION}" ]]; then
    alembic upgrade head
fi

uvicorn main:app --port 5000
