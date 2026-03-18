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

python manage.py makemigrations
python manage.py migrate
python manage.py loaddata sites
python manage.py collectstatic --noinput

mkdir -p ${CTS_LOCAL_DATA_PATH}
python manage.py load_text_repos
python manage.py slim_text_repos

mkdir atlas_data
python manage.py prepare_atlas_db --force

curl -O https://gist.githubusercontent.com/jacobwegner/68e538edf66539feb25786cc3c9cc6c6/raw/252e01a4c7e633b4663777a7e12dcb81119131e1/scaife-viewer-tmp.json

curl -X PUT "scaife-elasticsearch:9200/_template/scaife-viewer?pretty" -H 'Content-Type: application/json' -d "$(cat scaife-viewer-tmp.json)"
python manage.py indexer --max-workers=1 --limit=1000

rm scaife-viewer-tmp.json

exec "$@"