#!/usr/bin/env bash

echo PUBLIC_URL="/" > .env
echo GENERATE_SOURCEMAP="false" >> .env
yarn install --no-progress --frozen-lock
# yarn prettier
# yarn lint:ci
yarn build
