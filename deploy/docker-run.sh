#!/usr/bin/env bash

[[ -z "${HTTP_PROXY}" ]] && USE_PROXY=false || USE_PROXY=true

set -u   # crash on missing env variables
set -e   # stop on any error
set -x

echo Collecting static files
python manage.py collectstatic --no-input

# run gatekeeper
echo "Starting gatekeeper"
if [ ${USE_PROXY} = true ]; then
  echo "Using proxy"
  ./keycloak-gatekeeper --config gatekeeper.conf --openid-provider-proxy $HTTP_PROXY 2>&1 | tee /var/log/gatekeeper/gatekeeper.log &
else
  echo "Not using proxy"
  ./keycloak-gatekeeper --config gatekeeper.conf 2>&1 | tee /var/log/gatekeeper/gatekeeper.log &
fi


# run uwsgi
echo "Starting uwsgi"
exec uwsgi --ini uwsgi.ini