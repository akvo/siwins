#!/usr/bin/env bash

python -m seeder.sync

INSTANCE="${SIWINS_INSTANCE}"
CATEGORIES="./source/"${INSTANCE}"/category.json"

akvo-responsegrouper --config "${CATEGORIES}"