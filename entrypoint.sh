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
curl -L https://github.com/scaife-viewer/scaife-search-indexer/raw/master/share/template.json | \
curl -X PUT "http://elasticsearch:9200/_template/scaife-viewer" -H "Content-Type: application/json" -d @-
python manage.py indexer --urn-prefix=urn:cts:pdlpsci:bodin.livrep.perseus-eng1

exec "$@"
