#!/bin/sh

python manage.py migrate
python manage.py loaddata sites
honcho start web
