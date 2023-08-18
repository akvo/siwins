#!/usr/bin/env bash
#shellcheck disable=SC2039

set -euo pipefail

RETRIES=15

until psql -h db:5432 -U siwins -w password -d siwins -c "select 1" &>/dev/null 2>&1 || [ $RETRIES -eq 0 ];
do
  echo "Waiting for postgres server, $((RETRIES--)) remaining attempts..."
  sleep 1
done

wait4ports -q -s 1 -t 60 tcp://localhost:80 tcp://localhost:5000

http_get() {
    url="${1}"
    shift
    code="${1}"
    shift
    curl --verbose --url "${url}" "$@" 2>&1 | grep "< HTTP.*${code}"
}

http_get "http://localhost" 200
http_get "http://localhost/api/docs" 200
# http_get "http://localhost/config.js" 200
http_get "http://localhost/api/config.js" 200
