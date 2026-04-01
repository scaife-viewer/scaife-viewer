#!/bin/sh

SENTINEL_DIR=/sv-data/sentinels
mkdir -p ${CTS_LOCAL_DATA_PATH} ${SENTINEL_DIR} ${ATLAS_DATA_DIR:-atlas_data}

python manage.py migrate
python manage.py loaddata sites
python manage.py makemigrations

# if [ ! -f ${SENTINEL_DIR}/.text_repos_loaded ]; then
python manage.py load_text_repos
python manage.py slim_text_repos
touch ${SENTINEL_DIR}/.text_repos_loaded
# fi

# if [ ! -f ${SENTINEL_DIR}/.atlas_db_prepared ]; then
python manage.py prepare_atlas_db --force
touch ${SENTINEL_DIR}/.atlas_db_prepared
# fi

# if [ ! -f ${SENTINEL_DIR}/.es_indexed ]; then
curl -X PUT "http://${SV_ELASTICSEARCH_HOST}:${SV_ELASTICSEARCH_PORT}/_template/scaife-viewer?pretty" -H 'Content-Type: application/json' -d "$(cat deploy/scaife-viewer-es-template.json)"
python manage.py indexer --max-workers=1 --limit=1000
touch ${SENTINEL_DIR}/.es_indexed
# fi

exec "$@"
