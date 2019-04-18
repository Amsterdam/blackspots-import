#!/usr/bin/env bash
set -u   # crash on missing env variables
set -e   # stop on any error
set -x

echo Collecting static files
python manage.py collectstatic --no-input

ls -al /static/

chmod -R 777 /static

# run gatekeeper

if [ -n $HTTP_PROXY ]; then
  ./keycloak-gatekeeper --config gatekeeper.conf --openid-provider-proxy $HTTP_PROXY 2>&1 | tee /var/log/gatekeeper/gatekeeper.log
else
  ./keycloak-gatekeeper --config gatekeeper.conf 2>&1 | tee /var/log/gatekeeper/gatekeeper.log &
fi


# run uwsgi
exec uwsgi -i --show-config >> /var/log/uwsgi/uwsgi.log 2>&1

