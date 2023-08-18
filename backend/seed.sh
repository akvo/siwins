#!/usr/bin/env bash

python -m seeder.administration
python -m seeder.seed
python -m seeder.cascade


INSTANCE="$SIWINS_INSTANCE"
CATEGORIES="./source/"${INSTANCE}"/category.json"

akvo-responsegrouper --config "${CATEGORIES}"