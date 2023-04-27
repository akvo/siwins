#!/usr/bin/env bash

python -m seeder.administration
python -m seeder.seed
python -m seeder.cascade

akvo-responsegrouper --config ./source/category.json