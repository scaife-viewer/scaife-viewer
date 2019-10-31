#!/bin/sh

echo "Waiting for postgres..."

while ! nc -z $SV_POSTGRES_HOST $SV_POSTGRES_PORT; do
  sleep 0.1
done
echo "PostgreSQL started"

if [ "$USE_ELASTICSEARCH_SERVICE" = "1" ]
then
  echo "Waiting for elasticsearch..."
  while ! nc -z $SV_ELASTICSEARCH_HOST $SV_ELASTICSEARCH_PORT; do
    sleep 0.1
  done

  # wait until the nodes endpoint comes online
  until $(curl --output /dev/null --silent http://$SV_ELASTICSEARCH_HOST:$SV_ELASTICSEARCH_PORT/_nodes/_all/http); do
    sleep 1
  done
  echo "elasticsearch started"
fi

# echo "Running migrations"
# python manage.py makemigrations
# python manage.py migrate

exec "$@"
