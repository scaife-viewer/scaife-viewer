#!/bin/sh

echo "Waiting for postgres..."

while ! nc -z postgres 5432; do
  sleep 0.1
done

echo "PostgreSQL started"

echo "Waiting for elasticsearch..."

while ! nc -z elasticsearch 9200; do
  sleep 0.1
done

echo "elasticsearch started"

# python manage.py flush --no-input
python manage.py migrate
curl -s "https://scaife-cts-dev.perseus.org/api/cts?request=GetCapabilities" > ti.xml
python manage.py runserver 0.0.0.0:8000

exec "$@"
