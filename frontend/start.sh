#!/usr/bin/env bash

echo PUBLIC_URL="/" > .env
echo GENERATE_SOURCEMAP="false" >> .env
npm install --no-progress --frozen-lock
npm start
