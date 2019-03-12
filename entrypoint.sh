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

python manage.py makemigrations
python manage.py migrate

exec "$@"
