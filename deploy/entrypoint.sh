#!/bin/sh

mkdir -p ${CTS_LOCAL_DATA_PATH}

python manage.py loaddata sites
python manage.py migrate sites

python manage.py makemigrations
python manage.py migrate

python manage.py load_text_repos
python manage.py slim_text_repos

mkdir -p atlas_data
python manage.py prepare_atlas_db

curl -O https://gist.githubusercontent.com/jacobwegner/68e538edf66539feb25786cc3c9cc6c6/raw/252e01a4c7e633b4663777a7e12dcb81119131e1/scaife-viewer-tmp.json
curl -X PUT "http://${SV_ELASTICSEARCH_HOST}:${SV_ELASTICSEARCH_PORT}/_template/scaife-viewer?pretty" -H 'Content-Type: application/json' -d "$(cat scaife-viewer-tmp.json)"
python manage.py indexer --max-workers=1 --limit=1000

rm scaife-viewer-tmp.json

exec "$@"