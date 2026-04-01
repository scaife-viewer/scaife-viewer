#!/bin/sh

SENTINEL_DIR=/sv-data/sentinels
mkdir -p ${SENTINEL_DIR} ${CTS_LOCAL_DATA_PATH} ${ATLAS_DATA_DIR:-atlas_data}


# FIXME: (charles) I have no idea why we need to run migrate
# twice. Something is clearly wrong with what's
# going on here, but Django complains about the
# missing sites table unless we run these processes
# in this order.
python manage.py migrate
python manage.py loaddata sites
python manage.py makemigrations
python manage.py migrate sites
python manage.py migrate


if [ ! -f ${SENTINEL_DIR}/.text_repos_loaded ]; then
    python manage.py load_text_repos
    python manage.py slim_text_repos
    touch ${SENTINEL_DIR}/.text_repos_loaded
fi

if [ ! -f ${SENTINEL_DIR}/.atlas_db_prepared ]; then
    python manage.py prepare_atlas_db --force
    touch ${SENTINEL_DIR}/.atlas_db_prepared
fi

if [ ! -f ${SENTINEL_DIR}/.es_indexed ]; then
    curl -X PUT "http://${SV_ELASTICSEARCH_HOST}:${SV_ELASTICSEARCH_PORT}/_template/scaife-viewer?pretty" -H 'Content-Type: application/json' -d "$(cat deploy/scaife-viewer-es-template.json)"
    python manage.py indexer --max-workers=1 --limit=1000
    touch ${SENTINEL_DIR}/.es_indexed
fi

exec "$@"
