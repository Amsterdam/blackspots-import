#!/usr/bin/env bash

set -u   # crash on missing env variables
set -e   # stop on any error
set -x   # print what we are doing

/deploy/docker-wait.sh

cd /app

python manage.py migrate
python run_import.py
python check_import.py
