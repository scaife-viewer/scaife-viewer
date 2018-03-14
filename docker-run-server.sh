#!/bin/sh

python manage.py migrate
python manage.py loaddata sites
exec honcho start web
