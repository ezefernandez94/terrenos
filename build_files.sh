#!/usr/bin/env bash

echo "Building project packages ..."
python3 -m pip install -r terrenos/requirements.txt

## echo "Creating Staticfiles directory ..."
## mkdir -p staticfiles_build/static
## 
## echo "Migrating Database ..."
## python3 terrenos/manage.py makemigrations --noinput
## python3 terrenos/manage.py migrate --noinput

echo "Collecting static files ..."
python3 terrenos/manage.py collectstatic