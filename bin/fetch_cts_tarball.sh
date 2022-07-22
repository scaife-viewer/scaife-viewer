#!/usr/bin/env bash
set -e
TARBALL_URL=${CTS_TARBALL_URL:-https://storage.googleapis.com/sv-ogl-pdl-deployments/heroku-dev/2022/07/22/homer.tgz}
DATA_PATH=${CTS_TARBALL_DATA_PATH:-data}
TARBALL_NAME=${CTS_TARBALL_NAME:-cts.tgz}
CTS_DIR=${CTS_TARBALL_CTS_DIR:-cts}

mkdir -p $DATA_PATH/$CTS_DIR
curl $TARBALL_URL > $DATA_PATH/$TARBALL_NAME
tar -xf $DATA_PATH/$TARBALL_NAME --strip-components=1 -C $DATA_PATH/$CTS_DIR
rm $DATA_PATH/$TARBALL_NAME
