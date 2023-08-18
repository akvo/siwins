#!/usr/bin/env bash

python -m seeder.administration
python -m seeder.form_seed
python -m seeder.cascade
python -m seeder.fake_datapoint 100

INSTANCE="$SIWINS_INSTANCE"
CATEGORIES="./source/"${INSTANCE}"/category.json"

akvo-responsegrouper --config "${CATEGORIES}"