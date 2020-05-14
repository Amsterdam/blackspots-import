#!/usr/bin/env bash

set -u   # crash on missing env variables
set -e   # stop on any error

trap "rm /tmp/spots.sql" EXIT   # always cleanup on exit

python manage.py update_spots_export_table
PGPASSWORD=$DATABASE_PASSWORD pg_dump -d $DATABASE_NAME --port $DATABASE_PORT -h $DATABASE_HOST -U $DATABASE_USER -t blackspots_spotexport --inserts --no-owner > /tmp/spots.sql
python manage.py upload_to_objectstore /tmp/spots.sql
