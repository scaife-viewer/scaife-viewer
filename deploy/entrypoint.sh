#!/bin/sh

SENTINEL_DIR=${ATLAS_DATA_DIR:-atlas_data}/sentinels
mkdir -p ${SENTINEL_DIR} ${CTS_LOCAL_DATA_PATH:-data/cts} ${ATLAS_DATA_DIR:-atlas_data}


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

# Apply any pending schema migrations to the ATLAS SQLite database.
# This handles the case where the atlas.sqlite on the volume was built
# with an older version of scaife_viewer.atlas that is missing tables
# added in later migrations (e.g. scaife_viewer_atlas_attributionrecord).
# Running migrate here is safe: it only applies what is missing and
# never touches the ingested data.
python manage.py migrate --database=atlas


# Re-load text repos if the content manifest has changed since last ingestion.
MANIFEST_PATH="${CONTENT_MANIFEST_PATH:-data/content-manifests/production.yaml}"
MANIFEST_HASH=$(sha256sum "${MANIFEST_PATH}" 2>/dev/null | cut -d' ' -f1 || echo "")
STORED_HASH=""
[ -f "${SENTINEL_DIR}/.manifest_hash" ] && STORED_HASH=$(cat "${SENTINEL_DIR}/.manifest_hash")

if [ ! -f "${SENTINEL_DIR}/.text_repos_loaded" ] || [ "${MANIFEST_HASH}" != "${STORED_HASH}" ]; then
    python manage.py load_text_repos
    python manage.py slim_text_repos
    echo "${MANIFEST_HASH}" > "${SENTINEL_DIR}/.manifest_hash"
    touch "${SENTINEL_DIR}/.text_repos_loaded"
    # Atlas must be rebuilt when repos change
    rm -f "${SENTINEL_DIR}/.atlas_db_prepared"
fi

if [ ! -f "${SENTINEL_DIR}/.atlas_db_prepared" ]; then
    ./bin/copy_corpus_repo_metadata
    python manage.py prepare_atlas_db --force && \
    touch "${SENTINEL_DIR}/.atlas_db_prepared" && \
    rm -f "${SENTINEL_DIR}/.es_indexed" # rebuild ES index when ATLAS changes
fi

if [ ! -f "${SENTINEL_DIR}/.es_indexed" ]; then
    curl -X PUT "http://${SV_ELASTICSEARCH_HOST}:${SV_ELASTICSEARCH_PORT}/_template/scaife-viewer?pretty" -H 'Content-Type: application/json' -d "$(cat deploy/scaife-viewer-es-template.json)"
    python manage.py indexer --max-workers=1
    touch "${SENTINEL_DIR}/.es_indexed"
fi

exec "$@"
