#!/usr/bin/env bash

python -m seeder.administration
python -m seeder.form_seed
python -m seeder.cascade
python -m seeder.fake_datapoint 50

akvo-responsegrouper --config ./source/category.json