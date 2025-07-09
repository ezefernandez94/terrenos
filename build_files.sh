#!/usr/bin/env bash

echo "Building project packages ..."
python3 -m pip install -r terrenos/requirements.txt

echo "Migrating Database ..."
python3 terrenos/manage.py makemigrations --noinput
python3 terrenos/manage.py migrate --noinput

echo "Collecting static files ..."
python3 terrenos/manage.py collectstatic --no-input --clear